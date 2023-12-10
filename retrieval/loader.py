from typing import Generator

import pandas as pd
import psycopg2
import psycopg2.extras


def setup_postgres_connection(cursor_name=None):
    import os
    hostname = os.environ["DB_HOST"]
    username = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    database = os.environ["DB_NAME"]

    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    if cursor_name:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor, name=cursor_name)
    else:
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return connection, cursor


def format_movie_data(movie_data: pd.DataFrame):
    movie_data["duration"] = movie_data["duration"].apply(lambda x: f"{x // 60} hours {x % 60} minutes")
    movie_data["reviews"] = movie_data["reviews"].apply(lambda x: "  ".join(x) if x and all(x) else "")


DATA_QUERY = """
    SELECT
        m.id AS id,
        m.title AS title,
        m.description,
        m.release,
        m.duration,
        m.genres,
        m.directors,
        m.actors,
        m.plot,
        array_agg(ds.url) AS urls,
        array_agg(ds.page_title) AS page_titles,
        array_agg(r.title || ' ' || r.content) AS reviews
    FROM movies AS m
    JOIN data_sources AS ds ON m.id = ds.movie_id
    LEFT JOIN reviews AS r ON m.id = r.movie_id
    GROUP BY m.id
"""


def load_crawled_data() -> pd.DataFrame:
    from time import time
    connection, cursor = setup_postgres_connection()

    start_time = time()

    cursor.execute(DATA_QUERY)
    movie_data: pd.DataFrame = pd.DataFrame(cursor.fetchall())

    end_time = time()

    print(f"Loaded {len(movie_data)} movies in {end_time - start_time} seconds")

    format_movie_data(movie_data)

    # Close the connection
    cursor.close()
    connection.close()

    return movie_data


def load_crawled_data_iter(callback):
    from time import time
    connection, cursor = setup_postgres_connection("movies_cursor")

    start_time = time()
    
    cursor.execute(DATA_QUERY)
    while True:
        rows = cursor.fetchmany(1000)
        if not rows:
            break
        rows = pd.DataFrame(rows)
        format_movie_data(rows)
        callback(rows)

    end_time = time()

    print(f"Loaded movies in {end_time - start_time} seconds")

    # Close the connection
    cursor.close()
    connection.close()
