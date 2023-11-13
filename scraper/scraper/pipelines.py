# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import psycopg2
from dotenv import load_dotenv

from .items import Movie

from scrapy.exceptions import DropItem

from .items import Movie, Plot

class PostgresPipeline:

    def __init__(self):
        load_dotenv()

        hostname = os.environ.get("DB_HOST")
        username = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASSWORD")
        database = os.environ.get("DB_NAME")

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews(
                id serial PRIMARY KEY, 
                url text,
                score int,
                title text,
                content text
            )
            """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS movies(
                id serial PRIMARY KEY, 
                title text,
                description text,
                release date,
                duration text,
                genres text,
                score text,
                director text,
                actors text,
                plot text,
                metadata_url text,
                metadata_image_url text,
                metadata_page_title text
            )
            """)

    def reviewItem(self, item):
        self.cur.execute("""
            INSERT INTO reviews (url, score, title, content) 
            VALUES (%s, %s, %s, %s)
        """, (
            item["url"],
            item["score"],
            item["title"],
            item["content"]
        ))

    def movieItem(self, item):
        self.cur.execute("""
            INSERT INTO movies (title, description, release, duration, genres, score, director, actors, plot, metadata_url, metadata_image_url, metadata_page_title) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            item["title"],
            item["description"],
            item["release"],
            item["duration"],
            ','.join(item["genres"]),
            item["score"],
            item["director"],
            ','.join(item["actors"]),
            item["plot"],
            item["metadata"]["url"],
            item["metadata"]["image_url"],
            item["metadata"]["page_title"]
        ))

    def process_item(self, item, spider):

        # check if item is a movie or a review
        if isinstance(item, Movie):
            self.movieItem(item)
        else:
            self.reviewItem(item)

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
        if isinstance(item, Movie):
            return self.process_movie(item)
        elif isinstance(item, Plot):
            return self.process_plot(item)
        return item
