from sentence_transformers import SentenceTransformer
from functools import lru_cache

# Load the model only once
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

@lru_cache(maxsize=1024)
def generate_embedding(question_text):
    """
    Generates a sentence embedding for a given text.
    Uses LRU cache to avoid re-computing for the same text.
    """
    return MODEL.encode(question_text)

def generate_embeddings_batch(questions_list):
    """
    Generates embeddings for a batch of questions for efficiency.
    """
    return MODEL.encode(questions_list)
