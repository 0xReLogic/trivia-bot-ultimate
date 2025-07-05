#include "robust_screenshot_validator.h"
#include <iostream>
#include <numeric> // For std::accumulate

// Validates the screenshot for integrity, dimensions, and content relevance.
bool validate_screenshot(const cv::Mat& image) {
    std::cout << "Performing robust validation of the screenshot." << std::endl;

    // 1. Check for empty matrix
    if (image.empty()) {
        std::cerr << "Validation Failed: Screenshot matrix is empty." << std::endl;
        return false;
    }

    // 2. Validate dimensions (e.g., must be at least a certain size)
    const int min_width = 640;
    const int min_height = 480;
    if (image.cols < min_width || image.rows < min_height) {
        std::cerr << "Validation Failed: Screenshot dimensions (" << image.cols << "x" << image.rows 
                  << ") are smaller than the required minimum (" << min_width << "x" << min_height << ")." << std::endl;
        return false;
    }

    // 3. Check for corruption or blank screens (e.g., mostly a single color)
    cv::Mat gray;
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    
    // Calculate the standard deviation of pixel intensities.
    // A very low standard deviation suggests a blank or uniform image.
    cv::Scalar mean, stddev;
    cv::meanStdDev(gray, mean, stddev);

    if (stddev[0] < 15) { // Threshold for variability; low value means uniform color
        std::cerr << "Validation Failed: Screenshot appears to be blank or corrupt (low pixel variance). StdDev: " << stddev[0] << std::endl;
        return false;
    }

    // 4. Validate content relevance (e.g., contains some amount of text-like features)
    // This is a more advanced check. We can use edge detection as a proxy for complexity.
    cv::Mat edges;
    cv::Canny(gray, edges, 50, 150);
    int edge_pixels = cv::countNonZero(edges);
    double edge_density = static_cast<double>(edge_pixels) / (image.cols * image.rows);

    if (edge_density < 0.01) { // If less than 1% of pixels are edges, it might be irrelevant.
        std::cerr << "Validation Failed: Screenshot lacks sufficient detail or text-like features. Edge density: " << edge_density << std::endl;
        return false;
    }

    std::cout << "Screenshot validation successful. Image is valid and appears relevant." << std::endl;
    return true;
}
