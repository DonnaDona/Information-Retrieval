# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import psycopg2
from dotenv import load_dotenv

from .items import Movie


class ScraperPipeline:

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
            INSERT INTO movies (title, description, release, duration, genres, score, director, actors, metadata_url, metadata_image_url, metadata_page_title) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            item["title"],
            item["description"],
            item["release"],
            item["duration"],
            ','.join(item["genres"]),
            item["score"],
            item["director"],
            ','.join(item["actors"]),
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
