import pyterrier as pt


def initialize_terrier(index_path):
    pt.init()
    return pt.IndexFactory.of(index_path)


def perform_query(index, query):
    bm25 = pt.BatchRetrieve(index, wmodel="BM25")
    result_set = bm25.transform(query)
    return result_set
