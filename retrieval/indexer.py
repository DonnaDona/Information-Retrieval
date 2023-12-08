import pyterrier as pt
import pandas as pd


def create_index(index_path, crawled_data):
    df = pd.DataFrame(crawled_data)

    indexing_pipeline = pt.IterDictIndexer(index_path, meta={"image_url": 255, "docno": 20}, overwrite=True)
    # rename the column id to docno
    df = df.rename(columns={"id": "docno"})
    # serialize all the "date" values to a string in the form "day Month year"
    df["release"] = pd.to_datetime(df["release"]).dt.strftime("%d %B %Y")
    print("Started indexing...")

    indexing_pipeline.index(df.to_dict(orient="records"), fields=df.head())
    print("Finished indexing...")
    #indexing_pipeline.run()
