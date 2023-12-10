import os
import dotenv

del os.environ['JAVA_HOME']
dotenv.load_dotenv()
print(os.environ['JAVA_HOME'])

import pyterrier as pt
from config import load_environment_variables
from retrieval import retriever, loader, indexer


def main():
    load_environment_variables()
    pt.init()

    # Loading crawled data from the database
    crawled_data = loader.load_crawled_data()
    index_path = "./data/index"

    # Creating an index
    indexer.create_index(index_path, crawled_data, fields=['image_url', 'id'], meta={"image_url": 255, "docno": 20})

    # Performing a query about a movie
    index = retriever.initialize_terrier(index_path)
    print(index.getCollectionStatistics())

    query = "The Matrix 1999"
    result_set = retriever.perform_query(index, query)
    print(result_set)


if __name__ == "__main__":
    main()
