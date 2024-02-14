from fastembed import TextEmbedding
from typing import List
import numpy as np

def numpy_serializer(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError("Not serializable")

embedding_model = TextEmbedding(model_name="BAAI/bge-base-en")

def generate_embedding(documents):
    if isinstance(documents, str):
        documents = [documents]
    
    embeddings: List[np.ndarray] = list(embedding_model.embed(documents))
    embeddings = [arr.tolist() for arr in embeddings]
    return embeddings

def gen_embedding_lambda_handler(event, context):
    return generate_embedding(event['documents'])

if __name__ == "__main__":
    
    documents: List[str] = [
        "passage: Hello, World!",
        "query: Hello, World!", # these are two different embedding
        "passage: This is an example passage.",
        "fastembed is supported by and maintained by Qdrant." # You can leave out the prefix but it's recommended
    ]
    
    embeddings = generate_embedding(documents)