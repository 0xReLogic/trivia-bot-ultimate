import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer, util
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join('models', 'trivia_knowledge_base.db')
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def find_similar_question(question_text, threshold=0.85):
    """Finds a semantically similar question in the learning database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, question_text, question_embedding, correct_answer FROM learned_questions")
    rows = cursor.fetchall()
    
    if not rows:
        conn.close()
        return None

    question_embedding = MODEL.encode(question_text)
    db_embeddings = np.array([np.frombuffer(row[2], dtype=np.float32) for row in rows])

    similarities = util.pytorch_cos_sim(question_embedding, db_embeddings)[0]
    best_match_idx = np.argmax(similarities).item()
    
    if similarities[best_match_idx] > threshold:
        result = rows[best_match_idx]
        conn.close()
        return {
            "id": result[0],
            "question_text": result[1],
            "correct_answer": result[3],
            "similarity": similarities[best_match_idx].item()
        }
        
    conn.close()
    return None

def save_learned_answer(question_text, answer_text, confidence):
    """Saves a new question and its learned answer to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    embedding = MODEL.encode(question_text).tobytes()
    
    cursor.execute("INSERT OR IGNORE INTO learned_questions (question_text, question_embedding, correct_answer, confidence, times_answered, times_correct) VALUES (?, ?, ?, ?, 1, 1)",
                   (question_text, embedding, answer_text, confidence))
    
    conn.commit()
    conn.close()

def update_success_count(question_id, success=True):
    """Updates the success/failure count for a learned question."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if success:
        cursor.execute("UPDATE learned_questions SET times_answered = times_answered + 1, times_correct = times_correct + 1, last_answered_at = CURRENT_TIMESTAMP WHERE id = ?", (question_id,))
    else:
        cursor.execute("UPDATE learned_questions SET times_answered = times_answered + 1, last_answered_at = CURRENT_TIMESTAMP WHERE id = ?", (question_id,))
        
    conn.commit()
    conn.close()

def cleanup_old_entries(days=30):
    """Removes old, infrequently used entries from the learning database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Example criteria: remove entries not answered in 30 days and answered less than 5 times
    cursor.execute("DELETE FROM learned_questions WHERE last_answered_at < ? AND times_answered < 5", (cutoff_date,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Cleaned up {deleted_count} old entries.")
    return deleted_count
