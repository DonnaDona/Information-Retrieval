# retriever.py
import pandas as pd
import pyterrier as pt

INDEX_PATH = "./index"


def init():
    if not pt.started():
        pt.init()


def load_index(index_path=None):
    if not index_path:
        import os
        index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index")
    init()
    return pt.IndexFactory.of(index_path)


def batch_retrieve(index, query, field_weights=None, limit=1000, query_expansion=True, metadata=["docno", "genres"]):
    import hashlib

    query = "".join([x if x.isalnum() else " " for x in query])

    field_names = index.getCollectionStatistics().fieldNames
    if field_weights is None:
        field_weights = {"docno": (0, 0), "title": (25, 2.5), "description": (2, 1), "release": (5, 0.25),
                         "duration": (1, 0.5), "genres": (2, 0.5), "directors": (4, 0.5), "actors": (1, 0.5),
                         "plot": (0.1, 20), "urls": (1, 0.5), "page_titles": (0.5, 0.5), "reviews": (0.005, 100)}
    assert len(field_names) == len(field_weights)

    # BM25F
    controls = {"qe": "on", "qemodel": "Bo1"} if query_expansion else {}
    for i, field_name in enumerate(field_names):
        controls[f"w.{i}"] = field_weights[field_name][0]
        controls[f"c.{i}"] = field_weights[field_name][1]

    br = pt.BatchRetrieve(index, wmodel="BM25F", controls=controls, metadata=metadata)
    pipe = pt.rewrite.SDM() >> br
    retrieve_pipeline = ~pipe % limit

    # using the hashed query as the pipe we can cache the results based on the query
    # instead of the qid
    md5_query = hashlib.md5(query.encode()).hexdigest()

    query_df = pt.new.queries([query], qid=[md5_query])
    result_set = retrieve_pipeline.transform(query_df)
    return result_set


def perform_query(index, query, limit=1000):
    return batch_retrieve(index, query, limit=limit)


def recommend(index, query):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    num_query_results = 5

    query_results = batch_retrieve(index, query, limit=num_query_results, metadata=["docno", "genres"])
    query_genres = "  ".join(query_results["genres"].tolist())

    num_documents = index.getCollectionStatistics().getNumberOfDocuments()
    genre_strings_all_documents = []
    for docid in range(num_documents):
        genres = index.getMetaIndex().getItem("genres", docid)
        if genres:
            genre_strings_all_documents.append(genres)

    vectorizer = TfidfVectorizer(sublinear_tf=True, analyzer="word")
    all_vectors = vectorizer.fit_transform(genre_strings_all_documents).toarray()
    query_vectors = vectorizer.transform([query_genres]).toarray()

    similarities = cosine_similarity(query_vectors, all_vectors)
    similarities = similarities[0]

    zipped = zip(range(num_documents), similarities)
    sorted_zipped = sorted(zipped, key=lambda x: x[1], reverse=True)
    sorted_zipped = sorted_zipped[:10]

    docnos = [index.getMetaIndex().getItem("docno", docid) for docid, _ in sorted_zipped]
    
    # transform array to dataframe
    df = pd.DataFrame(docnos, columns=['docno'])
    return df
