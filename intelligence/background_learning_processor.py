import time
import threading
from core.feedback_queue import FeedbackQueue # Assuming access to the C++ queue via a Python wrapper
from intelligence.feedback_analyzer import analyze_feedback_colors
from intelligence.answer_validator import validate_bot_choice, update_accuracy_stats
from intelligence.learning_updater import update_learning_db
import os

# This is a conceptual Python representation of the C++ queue.
# A real implementation would use a C++/Python binding like pybind11.
class PyFeedbackQueue:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()

    def pop(self):
        with self.lock:
            if not self.items:
                return None
            return self.items.pop(0)

    def push(self, item):
        with self.lock:
            self.items.append(item)

# Global queue instance (singleton pattern)
feedback_queue = PyFeedbackQueue()

def process_feedback_entry(entry):
    """
    Processes a single entry from the feedback queue.
    """
    # In a real system, entry would contain the screenshot path, question, options, and bot's choice.
    screenshot_path = entry["screenshot_path"]
    question_text = entry["question_text"]
    options_list = entry["options_list"]
    bot_choice_index = entry["bot_choice_index"]

    # 1. Analyze the feedback screenshot
    analysis_result = analyze_feedback_colors(screenshot_path)

    # 2. Validate the bot's choice
    validation_result = validate_bot_choice(bot_choice_index, analysis_result)

    # 3. Update learning database if necessary
    update_learning_db(question_text, options_list, validation_result)

    # 4. Update overall accuracy stats
    if validation_result["is_success"] is not None:
        update_accuracy_stats(validation_result["is_success"])
    
    # 5. Clean up the temporary screenshot
    try:
        os.remove(screenshot_path)
    except OSError as e:
        print(f"Error removing temp screenshot {screenshot_path}: {e}")

def background_learning_loop():
    """
    The main loop for the background learning thread.
    """
    print("Background learning processor started.")
    while True:
        entry = feedback_queue.pop()
        if entry:
            print(f"Processing feedback for question: '{entry['question_text'][:30]}...'")
            process_feedback_entry(entry)
        else:
            # Wait for a bit if the queue is empty
            time.sleep(2)

def start_background_processor():
    """
    Starts the background learning processor in a separate thread.
    """
    learning_thread = threading.Thread(target=background_learning_loop, daemon=True)
    learning_thread.start()
    return learning_thread
