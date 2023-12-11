# retriever.py
import pyterrier as pt


def init():
    if not pt.started():
        pt.init()


def load_index(index_path=None):
    if not index_path:
        import os
        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index")
    init()
    return pt.IndexFactory.of(index_path)


def perform_query(index, query, limit=1000):
    query = "".join([x if x.isalnum() else " " for x in query])

    field_names = index.getCollectionStatistics().fieldNames
    field_weights = {"docno": (0, 0), "title": (25, 2.5), "description": (2, 1), "release": (5, 0.25),
                     "duration": (1, 0.5), "genres": (2, 0.5), "directors": (4, 0.5), "actors": (1, 0.5),
                     "plot": (0.1, 10), "urls": (1, 0.5), "page_titles": (0.5, 0.5), "reviews": (0.01, 100)}
    assert len(field_names) == len(field_weights)

    # BM25F
    controls = {"qe": "on", "qemodel": "Bo1"}
    for i, field_name in enumerate(field_names):
        controls[f"w.{i}"] = field_weights[field_name][0]
        controls[f"c.{i}"] = field_weights[field_name][1]

    br = pt.BatchRetrieve(index, wmodel="BM25F", controls=controls)
    retrieve_pipeline = (pt.rewrite.SDM() >> br) % limit

    query_df = pt.new.queries(query)
    result_set = retrieve_pipeline.transform(query_df)
    return result_set
