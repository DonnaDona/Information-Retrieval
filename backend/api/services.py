import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from retrieval.retriever import perform_query, load_index, recommend

index = load_index()

def perform_search(query, *args, **kwargs):
    return perform_query(index, query, *args, **kwargs)["docno"]

def retrieve_recommended(q):
    return recommend(index, q)["docno"]
