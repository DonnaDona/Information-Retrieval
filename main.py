from src import loader, indexer, retriever


def main():
    crawled_data_path = "data/crawled_data.json"
    index_path = "data/index"

    crawled_data = loader.load_crawled_data(crawled_data_path)

    # Creating an index
    indexer.create_index(index_path)

    # Performing a query about a movie
    index = retriever.initialize_terrier(index_path)
    query = "What movies start with the letter A?"
    results = retriever.perform_query(index, query)

    print(results.head())


if __name__ == "__main__":
    main()
