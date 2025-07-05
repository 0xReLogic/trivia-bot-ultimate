import hashlib
import re

def normalize_text(text):
    """Normalizes text by lowercasing, removing punctuation and extra spaces."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip() # Remove extra spaces
    return text

def generate_hash(question_text):
    """
    Generates a stable MD5 hash for a given question text after normalization.
    """
    normalized_question = normalize_text(question_text)
    return hashlib.md5(normalized_question.encode('utf-8')).hexdigest()
