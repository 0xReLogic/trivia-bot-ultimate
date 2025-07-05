#ifndef ROBUST_SCREENSHOT_VALIDATOR_H
#define ROBUST_SCREENSHOT_VALIDATOR_H

#include <opencv2/opencv.hpp>

/**
 * @brief Validates the integrity and relevance of a screenshot.
 * 
 * @param image The input image (screenshot).
 * @return bool True if the screenshot is valid, false otherwise.
 */
bool validate_screenshot(const cv::Mat& image);

#endif // ROBUST_SCREENSHOT_VALIDATOR_H
