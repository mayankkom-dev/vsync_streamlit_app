from fastembed import TextEmbedding
from typing import List
import numpy as np
import pymongo


def numpy_serializer(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError("Not serializable")

embedding_model = TextEmbedding(model_name="BAAI/bge-base-en")
client = pymongo.MongoClient("mongodb+srv://mayank:mayank123@virtualsynccluster.xxs5t9r.mongodb.net/?retryWrites=true&w=majority")
db = client["vysncup"]
collection = db["fast_embeded"]

def generate_embedding(documents):
    if isinstance(documents, str):
        documents = [documents]
    
    embeddings: List[np.ndarray] = list(embedding_model.embed(documents))
    embeddings = [arr.tolist() for arr in embeddings]
    return embeddings

def gen_embedding_lambda_handler(event, context):
    return generate_embedding(event['documents'])

def fetch_fast_topn(input_query, collection=collection):
    if len(input_query)<100:
        input_query = f"""I am looking for information about {input_query}"""

    results = collection.aggregate([
    {"$vectorSearch": {
        "queryVector": generate_embedding([input_query])[0],
        "path": "fast_embed",
        "numCandidates": 100,
        "limit": 20,
        "index": "vector_index",
        }}
    ]);
    
    return list(results)


if __name__ == "__main__":
    
    # documents: List[str] = [
    #     "passage: Hello, World!",
    #     "query: Hello, World!", # these are two different embedding
    #     "passage: This is an example passage.",
    #     "fastembed is supported by and maintained by Qdrant." # You can leave out the prefix but it's recommended
    # ]
    client = pymongo.MongoClient("mongodb+srv://mayank:mayank123@virtualsynccluster.xxs5t9r.mongodb.net/?retryWrites=true&w=majority")
    db = client["vysncup"]
    collection = db["fast_embeded"]

    # embeddings = generate_embedding(documents)
    fetch_fast_topn("graph neural network attention", collection)