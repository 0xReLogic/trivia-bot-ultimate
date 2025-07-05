#ifndef UI_ELEMENTS_DETECTOR_H
#define UI_ELEMENTS_DETECTOR_H

#include <opencv2/opencv.hpp>
#include <vector>

/**
 * @brief Detects UI elements like buttons and progress indicators in an image.
 * 
 * @param image The input image (screenshot).
 * @return std::vector<cv::Rect> A vector of rectangles for the detected elements.
 */
std::vector<cv::Rect> detect_ui_elements(const cv::Mat& image);

#endif // UI_ELEMENTS_DETECTOR_H
