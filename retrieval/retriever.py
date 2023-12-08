import pyterrier as pt


def initialize_terrier(index_path):
    return pt.IndexFactory.of(index_path)


def perform_query(index, query):
    assert 10 == index.getCollectionStatistics().getNumberOfFields()

    bm25 = pt.BatchRetrieve(index, wmodel="BM25F",
                            controls={'w.0': 1, 'w.1': 4, 'w.2': 1, 'w.3': 1, 'w.4': 1, 'w.5': 1, 'w.6': 1, 'w.7': 1,
                                      'w.8': 1, 'w.9': 1, 'c.0': 0.5, 'c.1': 0.5, 'c.2': 0.1, 'c.3': 0.5, 'c.4': 0.5,
                                      'c.5': 0.5, 'c.6': 0.5, 'c.7': 0.5, 'c.8': 0.1, 'c.9': 0.5})
    result_set = bm25.search(query)
    return result_set
