import sqlite3
import hashlib
import os

DB_PATH = os.path.join('models', 'trivia_knowledge_base.db')

def get_question_hash(question_text):
    """Generates a SHA-256 hash for a given question text."""
    return hashlib.sha256(question_text.strip().lower().encode()).hexdigest()

def check_cache(question_text):
    """Checks the cache for a given question and returns the answer if found."""
    question_hash = get_question_hash(question_text)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT answer_text FROM cache_questions WHERE question_hash = ?", (question_hash,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        print(f"Cache hit for question: '{question_text[:30]}...'")
        return result[0]
    return None

def save_to_cache(question_text, answer_text):
    """Saves a question and its answer to the cache."""
    question_hash = get_question_hash(question_text)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO cache_questions (question_hash, question_text, answer_text) VALUES (?, ?, ?)",
                       (question_hash, question_text, answer_text))
        conn.commit()
        print(f"Saved to cache: '{question_text[:30]}...'")
    except sqlite3.IntegrityError:
        # Question hash already exists, which is fine.
        pass
    finally:
        conn.close()

def get_cache_stats():
    """Retrieves statistics about the cache."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM cache_questions")
    total_entries = cursor.fetchone()[0]
    
    # This stat would be incremented elsewhere, but we can query it here.
    cursor.execute("SELECT stat_value FROM learning_stats WHERE stat_key = 'cache_hits'")
    cache_hits = cursor.fetchone()[0]
    
    conn.close()
    return {"total_entries": total_entries, "cache_hits": int(cache_hits)}
