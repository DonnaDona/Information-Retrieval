# indexer.py
from typing import Generator

import pandas as pd
from . import loader
import pyterrier as pt


class CustomIndexer:
    def __init__(self, index_path, meta=None):
        self._index = pt.IterDictIndexer(index_path, meta=meta, overwrite=True, blocks=True)
        self.fields = None

    def index(self, df: pd.DataFrame):
        df = df.rename(columns={"id": "docno"})
        if self.fields is None:
            self.fields = df.columns.tolist()

        self._index.index(df.to_dict(orient="records"), fields=self.fields)
        print(f"Indexed {len(df)} documents")


def create_index(index_path, df: pd.DataFrame, meta=None):
    import time

    indexing_pipeline = CustomIndexer(index_path, meta=meta)

    start_time = time.time()
    indexing_pipeline.index(df.to_dict(orient="records"))
    end_time = time.time()

    print(f"Indexed {len(df)} documents in {end_time - start_time} seconds")


def create_index_serverside(index_path, meta=None):
    import time

    index = CustomIndexer(index_path, meta=meta)

    start_time = time.time()
    loader.load_crawled_data_iter(index.index)
    end_time = time.time()

    print(f"Indexed documents in {end_time - start_time} seconds")
