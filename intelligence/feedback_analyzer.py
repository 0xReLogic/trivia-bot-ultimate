import cv2
import numpy as np
from utils.config_manager import config
from utils.logger import log

def analyze_feedback_colors(screenshot_path):
    """
    Analyzes a feedback screenshot to determine if the answer was correct or incorrect,
    and attempts to identify the correct option if highlighted.
    """
    image = cv2.imread(screenshot_path)
    if image is None:
        log.error(f"Could not load image at {screenshot_path}")
        return {"result": "error", "correct_option_index": None}

    color_thresholds = config.get('color_thresholds')
    ocr_regions = config.get('device.ocr_regions')

    # --- Dynamic Answer Region Calculation ---
    # Get the main block for all answers
    ans_x, ans_y, ans_w, ans_h = ocr_regions['answers']
    option_height = ans_h // 4 # Assuming 4 options evenly spaced

    # Define the four sub-regions based on the main block
    answer_regions = {
        0: (ans_x, ans_y, ans_w, option_height),                         # Option A
        1: (ans_x, ans_y + option_height, ans_w, option_height),      # Option B
        2: (ans_x, ans_y + (option_height * 2), ans_w, option_height),# Option C
        3: (ans_x, ans_y + (option_height * 3), ans_w, option_height) # Option D
    }

    # Define color ranges
    correct_lower = np.array(color_thresholds['correct_feedback']['bgr_min'])
    correct_upper = np.array(color_thresholds['correct_feedback']['bgr_max'])
    wrong_lower = np.array(color_thresholds['wrong_feedback']['bgr_min'])
    wrong_upper = np.array(color_thresholds['wrong_feedback']['bgr_max'])

    # Check the overall feedback area first
    fb_x, fb_y, fb_w, fb_h = ocr_regions['feedback']
    feedback_roi = image[fb_y : fb_y + fb_h, fb_x : fb_x + fb_w]

    is_correct = cv2.countNonZero(cv2.inRange(feedback_roi, correct_lower, correct_upper)) > 500
    is_wrong = cv2.countNonZero(cv2.inRange(feedback_roi, wrong_lower, wrong_upper)) > 500

    result = "unknown"
    correct_option_index = None

    if is_correct:
        result = "correct"
        log.info("Feedback analysis: Correct answer detected.")
    elif is_wrong:
        result = "wrong"
        log.warning("Feedback analysis: Wrong answer detected. Searching for correct option...")
        # If wrong, the game might highlight the correct answer in green.
        for i, region in answer_regions.items():
            x, y, w, h = region
            roi = image[y : y + h, x : x + w]
            highlight_mask = cv2.inRange(roi, correct_lower, correct_upper)
            if cv2.countNonZero(highlight_mask) > 200:
                correct_option_index = i
                log.info(f"Detected correct answer highlighted at option index: {i}")
                break

    return {"result": result, "correct_option_index": correct_option_index}
