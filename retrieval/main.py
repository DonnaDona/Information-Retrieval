import dotenv
import pyterrier as pt

import indexer
import loader
import retriever

INDEX_PATH = "./index"


def index():
    dotenv.load_dotenv(override=True)  # override JAVA_HOME if set in .env

    pt.init()

    # Creating an index
    indexer.create_index_serverside(INDEX_PATH, meta={"docno": 20})


def retrieve():
    # Performing a query about a movie
    index = retriever.load_index(INDEX_PATH)
    print(index.getCollectionStatistics())

    query = "best spider man movie ever"
    result_set = retriever.perform_query(index, query)
    print(result_set)


def main():
    index()
    retrieve()


if __name__ == "__main__":
    main()
