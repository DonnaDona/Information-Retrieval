# retriever.py
import pyterrier as pt


def initialize_terrier(index_path):
    return pt.IndexFactory.of(index_path)


def perform_query(index, query):
    assert 5 == index.getCollectionStatistics().getNumberOfFields()

    bm25 = pt.BatchRetrieve(index, wmodel="BM25F",
                            controls={'w.0': 8, 'w.1': 1, 'w.2': 1, 'w.3': 1, 'w.4': 1,
                                      'c.0': 0.5, 'c.1': 0.5, 'c.2': 0.5, 'c.3': 0.5, 'c.4': 0.1})
    result_set = bm25.search(query)
    return result_set
