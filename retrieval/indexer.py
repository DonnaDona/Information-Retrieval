# indexer.py
from typing import Generator

import pandas as pd
import loader
import pyterrier as pt



def create_index(index_path, df: pd.DataFrame, meta=None):
    import time

    indexing_pipeline = pt.IterDictIndexer(index_path, meta=meta, overwrite=True, blocks=True)
    fields = df.columns.tolist()

    start_time = time.time()
    indexing_pipeline.index(df.to_dict(orient="records"), fields=fields)
    end_time = time.time()

    print(f"Indexed {len(df)} documents in {end_time - start_time} seconds")


def create_index_serverside(index_path, ss_iterator, meta=None):
    import time
    from datetime import datetime

    indexing_pipeline = pt.IterDictIndexer(index_path, meta=meta, overwrite=True, blocks=True)

    start_time = time.time()
    print(f"Starting indexing at {datetime.now()}")
    indexing_pipeline.index(ss_iterator, fields=loader.DEFAULT_FIELDS)
    end_time = time.time()

    print(f"Indexed documents in {end_time - start_time} seconds")
