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


def format_movie_data_df(movie_data):
    movie_data["duration"] = movie_data["duration"].apply(lambda x: f"{x // 60} hours {x % 60} minutes")
    movie_data["reviews"] = movie_data["reviews"].apply(lambda x: "  ".join(x) if x and all(x) else "")
    movie_data["urls"] = movie_data["urls"].apply(lambda x: "  ".join(x) if x and all(x) else "")
    movie_data["page_titles"] = movie_data["page_titles"].apply(lambda x: "  ".join(x) if x and all(x) else "")
    movie_data["genres"] = movie_data["genres"].apply(lambda x: "  ".join(x) if x and all(x) else "")
    return movie_data

def format_movie_data_dict(movie_data):
    return format_movie_data_df(pd.DataFrame([movie_data])).to_dict(orient="records")[0]

DEFAULT_FIELDS = ["docno", "title", "description", "release", "duration", "genres", "directors", "actors", "plot", "urls",
                  "page_titles", "reviews"]

DATA_QUERY = """
SELECT
    m.id AS docno,
    m.title, m.description, m.release, m.duration, m.genres, m.directors, m.actors, m.plot,
    ARRAY_AGG(DISTINCT ds.url) AS urls,
    ARRAY_AGG(DISTINCT ds.page_title) AS page_titles,
    ARRAY_AGG(r.title || ' - ' || r.content) AS reviews
FROM
    movies m
LEFT JOIN
    data_sources ds ON ds.movie_id = m.id
LEFT JOIN
    reviews r ON r.movie_id = m.id
GROUP BY
    m.id;
"""


def load_crawled_data() -> pd.DataFrame:
    from time import time
    connection, cursor = setup_postgres_connection()

    start_time = time()

    cursor.execute(DATA_QUERY)
    movie_data: pd.DataFrame = pd.DataFrame(cursor.fetchall())

    end_time = time()

    print(f"Loaded {len(movie_data)} movies in {end_time - start_time} seconds")

    movie_data = format_movie_data_df(movie_data)

    # Close the connection
    cursor.close()
    connection.close()

    return movie_data

class ServerSideMovieLoader:
    def __iter__(self):
        self.connection, self.cursor = setup_postgres_connection("movies_cursor")
        self.cursor.execute(DATA_QUERY)
        self.rows: pd.DataFrame = None
        self.row_idx = 0
        return self

    def __next__(self):
        if self.rows is None or self.row_idx >= len(self.rows):
            self.rows = self.cursor.fetchmany(3000)
            if not self.rows:
                self.cursor.close()
                self.connection.close()
                raise StopIteration
            
            print(f"Loaded {len(self.rows)} movies")

            self.row_idx = 0

        row = self.rows[self.row_idx]
        self.row_idx += 1
        return format_movie_data_dict(row)
