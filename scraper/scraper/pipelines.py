# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

import psycopg2
from dotenv import load_dotenv
from scrapy.exceptions import DropItem

from .items import Movie, Plot
from .items import Review


class PostgresPipeline:

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

        ## Create quotes table if none exists
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
                score float4,
                critic_score float4,
                director varchar (255),
                actors varchar (255) [],
                plot text,
                metadata_url text UNIQUE NOT NULL,
                metadata_image_url text,
                metadata_page_title varchar (255),
                CONSTRAINT superkey_crosswebsite UNIQUE (title, director, release)
            )
            """)

    def process_review(self, item: Review):
        self.cur.execute("""
            INSERT INTO reviews (url, score, title, content) 
            VALUES (%s, %s, %s, %s)
        """, (item.url, item.score, item.title, item.text))

    def process_movie(self, item: Movie):
        self.cur.execute("""
            INSERT INTO movies (title, description, release, duration, genres, score, director, actors, plot, metadata_url, metadata_image_url, metadata_page_title) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (item.title, item.description, item.release, item.duration, item.genres, item.score, item.director,
              item.actors, item.plot, item.metadata.url, item.metadata.image_url, item.metadata.page_title))

    def process_item(self, item, spider, retried=False):
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
        if isinstance(item, Movie) and item.plot:
            return item  # no need to merge, the plot is already there

        # If the plot is not already contained in the movie, merge it with a plot request
        if isinstance(item, Movie):
            return self.process_movie(item)
        elif isinstance(item, Plot):
            return self.process_plot(item)

        # No match, just return the item
        return item
