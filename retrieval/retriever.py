# retriever.py
import pandas as pd
import pyterrier as pt


def init():
    if not pt.started():
        pt.init()


def load_index(index_path):
    init()
    return pt.IndexFactory.of(index_path)


def perform_query(index, query):
    field_names = index.getCollectionStatistics().fieldNames
    field_weights = {"docno": (0, 0), "title": (20, 0.5), "description": (2, 1), "release": (1, 0.5),
                     "duration": (1, 0.5), "genres": (2, 0.5), "directors": (1, 0.5), "actors": (1, 0.5),
                     "urls": (1, 0.5), "page_titles": (1, 0.5), "reviews": (0.01, 1000)}
    assert len(field_names) == len(field_weights)

    # BM25F
    controls = {"qe": "on", "qemodel": "Bo1"}
    for i, field_name in enumerate(field_names):
        controls[f"w.{i}"] = field_weights[field_name][0]
        controls[f"c.{i}"] = field_weights[field_name][1]

    br = pt.BatchRetrieve(index, wmodel="BM25F", controls=controls)
    retrieve_pipeline = (pt.rewrite.SDM() >> br)

    query_df = pt.new.queries(query)
    result_set = retrieve_pipeline.transform(query_df)
    return result_set
