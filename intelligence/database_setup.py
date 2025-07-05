import sqlite3
import os

DB_PATH = os.path.join('models', 'trivia_knowledge_base.db')

def setup_database():
    """
    Sets up the comprehensive SQLite database with all necessary tables and indexes.
    """
    # Ensure the models directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Cache Table: For storing exact question matches (fastest lookup)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache_questions (
        id INTEGER PRIMARY KEY,
        question_hash TEXT NOT NULL UNIQUE,
        question_text TEXT NOT NULL,
        answer_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_question_hash ON cache_questions (question_hash);')

    # 2. Learned Questions Table: For semantic/similarity-based lookups
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learned_questions (
        id INTEGER PRIMARY KEY,
        question_text TEXT NOT NULL UNIQUE,
        question_embedding BLOB NOT NULL,
        correct_answer TEXT NOT NULL,
        confidence REAL DEFAULT 0.0,
        times_answered INTEGER DEFAULT 0,
        times_correct INTEGER DEFAULT 0,
        last_answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_question_text ON learned_questions (question_text);')

    # 3. TinyLLM Patterns Table: For rule-based or keyword-based matching
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tinyllm_patterns (
        id INTEGER PRIMARY KEY,
        question_pattern TEXT NOT NULL UNIQUE, -- e.g., "What is the capital of *?"
        answer_pattern TEXT NOT NULL,      -- e.g., "The capital of {1} is {A}."
        keywords TEXT,                     -- Comma-separated keywords
        success_rate REAL DEFAULT 0.0,
        times_used INTEGER DEFAULT 0
    );
    ''')

    # 4. Learning Stats Table: For monitoring overall bot performance
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learning_stats (
        id INTEGER PRIMARY KEY,
        stat_key TEXT NOT NULL UNIQUE,
        stat_value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    # Insert some initial stats
    cursor.execute("INSERT OR IGNORE INTO learning_stats (stat_key, stat_value) VALUES ('total_questions_answered', '0')")
    cursor.execute("INSERT OR IGNORE INTO learning_stats (stat_key, stat_value) VALUES ('total_correct_answers', '0')")
    cursor.execute("INSERT OR IGNORE INTO learning_stats (stat_key, stat_value) VALUES ('cache_hits', '0')")

    conn.commit()
    conn.close()
    print(f"Database setup complete at {DB_PATH}")

if __name__ == '__main__':
    setup_database()
