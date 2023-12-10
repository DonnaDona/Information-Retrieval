import psycopg2
import psycopg2.extras
from config import setup_db_config


def setup_db():
    db_config = setup_db_config()
    db = psycopg2.connect(**db_config)
    return db


def load_crawled_data():
    with setup_db() as db:
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM movies")
        results = cursor.fetchall()
    return results
