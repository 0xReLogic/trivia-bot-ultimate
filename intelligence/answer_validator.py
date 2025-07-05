import sqlite3
import os

DB_PATH = os.path.join('models', 'trivia_knowledge_base.db')

def validate_bot_choice(bot_choice_index, analysis_result):
    """
    Validates the bot's choice against the analyzed feedback.
    """
    is_success = False
    if analysis_result["result"] == "correct":
        is_success = True
    elif analysis_result["result"] == "wrong" and analysis_result["correct_option_index"] is not None:
        # The bot was wrong, but we know the correct answer now.
        is_success = False
    else:
        # Unknown result, cannot validate.
        return {"is_success": None, "correct_answer_index": None}

    return {
        "is_success": is_success,
        "correct_answer_index": analysis_result["correct_option_index"] if not is_success else bot_choice_index
    }

def update_accuracy_stats(was_correct):
    """
    Updates the overall accuracy statistics in the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE learning_stats SET stat_value = stat_value + 1 WHERE stat_key = 'total_questions_answered'")
    if was_correct:
        cursor.execute("UPDATE learning_stats SET stat_value = stat_value + 1 WHERE stat_key = 'total_correct_answers'")
        
    conn.commit()
    conn.close()
