import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_embedding(text: str) -> np.ndarray:
    embedding = model.encode(text, normalize_embeddings=True)
    return np.squeeze(embedding)


def store_in_faiss():
    
    pass