# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import psycopg2
from dotenv import load_dotenv


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
        CREATE TABLE IF NOT EXISTS Review(
            id serial PRIMARY KEY, 
            url text,,
            score text,
            title text
            content text
        )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Movie(
                id serial PRIMARY KEY, 
                url text,
                image_url text,
                title text,
                description text
                release text,
                duration text,
                genres text,
                score text,
                director text,
                actors text,
                plot text,
                metadata text,
            )
            """)

    def process_item(self, item, spider):
        # Check if the item already exists in the Review table
        self.cur.execute("SELECT id FROM Review WHERE url = %s", (item["url"],))
        existing_review = self.cur.fetchone()

        if not existing_review:
            # If the item does not exist, insert it into the Review table
            self.cur.execute("""
                        INSERT INTO Review (url, score, title, content) VALUES (%s, %s, %s, %s)
                    """, (
                item["url"],
                item["score"],
                item["title"],
                item["content"]
            ))

        # Check if the item already exists in the Movie table
        self.cur.execute("SELECT id FROM Movie WHERE url = %s", (item["url"],))
        existing_movie = self.cur.fetchone()

        if not existing_movie:
            # If the item does not exist, insert it into the Movie table
            self.cur.execute("""
                        INSERT INTO Movie (url, image_url, title, description, release, duration, genres, score, director, actors, plot, metadata) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                item["url"],
                item["image_url"],
                item["title"],
                item["description"],
                item["release"],
                item["duration"],
                item["genres"],
                item["score"],
                item["director"],
                item["actors"],
                item["plot"],
                item["metadata"]
            ))

        # Execute insert of data into the database
        self.connection.commit()
        return item

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()
