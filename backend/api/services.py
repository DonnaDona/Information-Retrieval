from retrieval.retriever import perform_query, load_index

index = load_index()

def perform_search(query):
    results = perform_query(index, query)["docno"]
    return results