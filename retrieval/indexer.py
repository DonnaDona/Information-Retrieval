# indexer.py
import pyterrier as pt
import pandas as pd


def create_index(index_path, crawled_data, fields=None, meta=None):
    df = pd.DataFrame(crawled_data)

    if fields is None:
        fields = df.columns.tolist()

    indexing_pipeline = pt.IterDictIndexer(index_path, meta=meta, overwrite=True)
    df = df.rename(columns={"id": "docno"})
    df["release"] = pd.to_datetime(df["release"]).dt.strftime("%d %B %Y")

    print("Started indexing...")
    indexing_pipeline.index(df.to_dict(orient="records"), fields=fields)
    print("Finished indexing...")
