from retrieval.retriever import perform_query, load_index

index = load_index()

def perform_search(query, *args, **kwargs):
    results = perform_query(index, query, *args, **kwargs)["docno"]
    return results