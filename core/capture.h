#ifndef CAPTURE_H
#define CAPTURE_H

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>

// Structure to hold the parsed trivia data
struct TriviaData {
    std::string question;
    std::vector<std::string> options;
};

/**
 * @brief Captures a screenshot from the connected ADB device.
 * 
 * @param device_id The ADB device serial ID.
 * @return cv::Mat The captured screenshot as an OpenCV matrix. Returns an empty matrix on failure.
 */
cv::Mat capture_screenshot(const std::string& device_id);

/**
 * @brief Performs OCR on a specific region of the input image.
 * 
 * @param image The input image (screenshot).
 * @param roi The region of interest to perform OCR on.
 * @return std::string The extracted text.
 */
std::string perform_ocr(const cv::Mat& image, const cv::Rect& roi);

/**
 * @brief Parses the raw OCR text into a structured TriviaData object.
 * 
 * @param raw_text The raw text extracted from OCR.
 * @return TriviaData The structured question and options.
 */
TriviaData parse_text(const std::string& raw_text);

#endif // CAPTURE_H
