import sqlite3
import os
import re

DB_PATH = os.path.join('models', 'trivia_knowledge_base.db')

def find_pattern_match(question_text, threshold=0.60):
    """Finds a matching pattern in the database using regex and keyword matching."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, question_pattern, answer_pattern, keywords FROM tinyllm_patterns")
    patterns = cursor.fetchall()
    conn.close()
    
    question_lower = question_text.lower()
    
    for pid, q_pattern, a_pattern, keywords in patterns:
        # Keyword check first for efficiency
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]
            if not any(keyword in question_lower for keyword in keyword_list):
                continue

        # Regex pattern matching
        try:
            if re.search(q_pattern, question_text, re.IGNORECASE):
                print(f"Found pattern match: '{q_pattern}'")
                # In a real system, you'd extract groups from the match to format the answer
                return {"id": pid, "answer_pattern": a_pattern}
        except re.error as e:
            print(f"Regex error for pattern '{q_pattern}': {e}")
            continue
            
    return None

def save_pattern(question_pattern, answer_pattern, keywords):
    """Saves a new question pattern to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO tinyllm_patterns (question_pattern, answer_pattern, keywords) VALUES (?, ?, ?)",
                       (question_pattern, answer_pattern, keywords))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Pattern already exists
    finally:
        conn.close()

def update_pattern_success(pattern_id, success=True):
    """Updates the success rate of a pattern."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # This is a simplified success rate calculation
    if success:
        cursor.execute("UPDATE tinyllm_patterns SET times_used = times_used + 1, success_rate = success_rate + 0.1 WHERE id = ?", (pattern_id,))
    else:
        cursor.execute("UPDATE tinyllm_patterns SET times_used = times_used + 1, success_rate = success_rate - 0.1 WHERE id = ?", (pattern_id,))
    
    conn.commit()
    conn.close()
