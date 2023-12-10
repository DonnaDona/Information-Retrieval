import os


def setup_postgres_connection():
    import psycopg2
    hostname = os.environ["DB_HOST"]
    username = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    database = os.environ["DB_NAME"]

    connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cursor = connection.cursor()
    return connection, cursor
