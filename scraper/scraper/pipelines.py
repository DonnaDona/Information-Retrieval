# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

import psycopg2
from dotenv import load_dotenv
from scrapy import Spider
from scrapy.exceptions import DropItem

from .items import Movie, Plot
from .items import Review


class PostgresPipeline:

    WHITELIST = ["imdb", "metacritic", "rottentomatoes"]

    def __setup_connection__(self):
        hostname = os.environ["DB_HOST"]
        username = os.environ["DB_USER"]
        password = os.environ["DB_PASSWORD"]
        database = os.environ["DB_NAME"]

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

    def __init__(self):
        load_dotenv()

        self.connection = None
        self.cur = None

        self.__setup_connection__()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews(
                id serial PRIMARY KEY, 
                url text NOT NULL,
                score float4,
                title varchar (255) NOT NULL,
                content text
            )
            """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS movies(
                id serial PRIMARY KEY, 
                title varchar (255) NOT NULL,
                description text,
                release date,
                duration smallint,
                genres varchar (128) [],
                director varchar (255),
                actors varchar (255) [],
                plot text,
                image_url text,
                CONSTRAINT superkey_crosswebsite UNIQUE (title, director, release)
            )
            """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS data_sources(
                id serial PRIMARY KEY,
                movie_id integer NOT NULL,
                movie_source_uid varchar (255),
                name varchar (255) NOT NULL,
                url text UNIQUE NOT NULL,
                page_title text,
                score float4,
                critic_score float4,
                last_crawled timestamp DEFAULT NOW(),
                CONSTRAINT fk_movie_id FOREIGN KEY (movie_id) REFERENCES movies(id)
            )
            """)

    def process_review(self, item: Review):
        self.cur.execute("""
            INSERT INTO reviews (url, score, title, content) 
            VALUES (%s, %s, %s, %s)
        """, (item.url, item.score, item.title, item.text))

    def process_movie(self, item: Movie):
        """
        If the movie does not exist in the database, insert it into the movies table
            and insert the current source into the data_sources table.
        If the movie exists, try to fill in the missing data.
        If the movie exists but the current source does not, insert the current source into the data_sources table.
        If the movie exists and the current source exists, update the last_crawled timestamp.

        :param item: the movie item
        """
        if not isinstance(item, Movie):
            raise ValueError("Item must be a Movie")
        self.cur.execute("""
            SELECT id, description, plot FROM movies WHERE title = %s AND director = %s AND release = %s
        """, (item.title, item.director, item.release))
        movie = self.cur.fetchone()

        if movie is None:
            self.cur.execute("""
                INSERT INTO movies (title, description, release, duration, genres, director, actors, plot, image_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (item.title, item.description, item.release, item.duration, item.genres, item.director, item.actors,
                  item.plot, item.metadata.image_url))

            movie_id = self.cur.fetchone()[0]
            self.cur.execute("""
                INSERT INTO data_sources (movie_id, movie_source_uid, name, url, page_title, score, critic_score) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (movie_id, item.movie_id, item.metadata.source_name, item.metadata.url, item.metadata.page_title,
                  item.score, item.critic_score))

            return

        movie_id = movie[0]
        db_description = movie[1]
        db_plot = movie[2]

        item.description = item.description if len(item.description) > len(db_description) else db_description
        item.plot = item.plot if len(item.plot) > len(db_plot) else db_plot

        # coalesce the data in the movie
        self.cur.execute("""
            UPDATE movies SET 
                description = COALESCE(description, %s),
                duration = COALESCE(duration, %s),
                genres = COALESCE(genres, %s),
                director = COALESCE(director, %s),
                actors = COALESCE(actors, %s),
                plot = COALESCE(plot, %s),
                image_url = COALESCE(image_url, %s)
            WHERE id = %s
        """, (item.description, item.duration, item.genres, item.director, item.actors, item.plot,
              item.metadata.image_url, movie_id))

        self.cur.execute("""
            SELECT id FROM data_sources WHERE movie_id = %s AND name = %s
        """, (movie_id, item.metadata.source_name))
        source_id = self.cur.fetchone()

        if source_id is None:
            self.cur.execute("""
                INSERT INTO data_sources (movie_id, movie_source_uid, name, url, page_title, score, critic_score) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (movie_id, item.movie_id, item.metadata.source_name, item.metadata.url, item.metadata.page_title,
                  item.score, item.critic_score))
        else:
            self.cur.execute("""
                UPDATE data_sources SET last_crawled = NOW() WHERE id = %s
            """, (source_id[0],))

    def process_item(self, item, spider: Spider, retried=False):
        if spider.name not in self.WHITELIST:
            return item
        try:
            # check if item is a movie or a review
            if isinstance(item, Movie):
                self.process_movie(item)
            else:
                self.process_review(item)
        except psycopg2.InterfaceError as e:
            print("Connection to database lost: ", e)
            self.__setup_connection__()
            if not retried:
                return self.process_item(item, spider, retried=True)
            return None
        except Exception as e:
            print("Error while inserting into database: ", e)
            import traceback
            traceback.print_exc()

            self.connection.rollback()
            return None
        else:
            # Execute insert of data into the database
            self.connection.commit()
            return item

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()


class MergePipeline:
    """
    Merge Movie and Plot objects into a single Movie object.

    This pipeline is responsible for keeping a Movie object until its Plot object is found.
    They are then merged and the Movie object is yielded.
    """

    def __init__(self):
        self.movies: dict[str, Movie] = {}
        self.plots: dict[str, Plot] = {}

    @staticmethod
    def get_key(item: Movie or Plot) -> str:
        return item.movie_id

    def process_movie(self, item: Movie):
        key = self.get_key(item)
        if key in self.plots:
            item.plot = self.plots[key].text
            del self.plots[key]
            return item
        else:
            self.movies[key] = item
            raise DropItem()

    def process_plot(self, item: Plot):
        key = self.get_key(item)
        if key in self.movies:
            movie = self.movies[key]
            movie.plot = item.text
            del self.movies[key]
            return movie
        else:
            self.plots[key] = item
            raise DropItem()

    def process_item(self, item, spider):
        if isinstance(item, Movie) and (item.plot or not item.wait_for_plot):
            return item  # no need to merge, the plot is already there

        # If the plot is not already contained in the movie, merge it with a plot request
        if isinstance(item, Movie):
            return self.process_movie(item)
        elif isinstance(item, Plot):
            return self.process_plot(item)

        # No match, just return the item
        return item
