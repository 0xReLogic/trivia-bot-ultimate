from intelligence.database_setup import DB_PATH
from intelligence.learning_db import save_learned_answer, update_success_count
from intelligence.cache_db import save_to_cache

def update_learning_db(question_text, options_list, validation_result):
    """
    Updates the learning database based on the validation result.
    """
    if validation_result["is_success"] is None:
        print("Skipping DB update due to unknown validation result.")
        return

    # If the answer was wrong, but we now know the correct one, we learn it.
    if not validation_result["is_success"] and validation_result["correct_answer_index"] is not None:
        correct_answer_index = validation_result["correct_answer_index"]
        if 0 <= correct_answer_index < len(options_list):
            correct_answer_text = options_list[correct_answer_index]
            
            print(f"Learning correct answer for '{question_text[:30]}...': {correct_answer_text}")
            
            # Save to the long-term learning database with high confidence
            save_learned_answer(question_text, correct_answer_text, confidence=0.99) # High confidence because it was verified
            
            # Also save it to the cache for fast future lookups
            save_to_cache(question_text, correct_answer_text)
    
    # Here you could also update the success/fail count for existing entries
    # For example, if the answer came from the learning_db, you would call update_success_count
    # This logic would be part of the main orchestrator loop.
