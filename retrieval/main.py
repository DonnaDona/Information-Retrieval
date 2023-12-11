import dotenv
import pyterrier as pt

import indexer
import retriever
import loader

INDEX_PATH = "./index"


def index():
    dotenv.load_dotenv(override=True)  # override JAVA_HOME if set in .env

    pt.init()

    ss_iterator = iter(loader.ServerSideMovieLoader())
    # Creating an index
    indexer.create_index_serverside(INDEX_PATH, ss_iterator, meta={"docno": 20})


def retrieve():
    # Performing a query about a movie
    index = retriever.load_index(INDEX_PATH)
    print(index.getCollectionStatistics())

    query = "The Matrix"
    result_set = retriever.perform_query(index, query)
    print(result_set)


def main():
    index()
    retrieve()


if __name__ == "__main__":
    main()
