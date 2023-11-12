import pyterrier as pt


def create_index(index_path):
    pt.init()
    indexing_pipeline = pt.DFIndexer(index_path)
    indexing_pipeline.run()
