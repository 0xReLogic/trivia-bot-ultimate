import numpy as np
from scipy.spatial.distance import cosine

def calculate_cosine_similarity(embedding1, embedding2):
    """Calculates the cosine similarity between two embeddings."""
    # Cosine distance is 1 - similarity, so similarity is 1 - distance
    return 1 - cosine(embedding1, embedding2)

def find_most_similar(target_embedding, candidates_list):
    """
    Finds the most similar item in a list of candidates.
    Each candidate in the list should be a tuple: (item_id, item_embedding)
    """
    if not candidates_list:
        return None, 0.0

    best_match = None
    highest_similarity = -1.0

    for item_id, candidate_embedding in candidates_list:
        similarity = calculate_cosine_similarity(target_embedding, candidate_embedding)
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = item_id
            
    return best_match, highest_similarity
