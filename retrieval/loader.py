import os

import dotenv
import psycopg2
import psycopg2.extras


def setup_db():
    # load the environment variables
    dotenv.load_dotenv()

    # set up the database connection
    db = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )

    return db


def load_crawled_data():
    # set up the database connection
    db = setup_db()

    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM movies")
    results = cursor.fetchall()
    cursor.close()
    db.close()

    return results
