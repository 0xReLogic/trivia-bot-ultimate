#ifndef FEEDBACK_QUEUE_H
#define FEEDBACK_QUEUE_H

#include <queue>
#include <mutex>
#include <condition_variable>
#include <string>
#include <opencv2/opencv.hpp>

struct FeedbackItem {
    cv::Mat screenshot;
    std::string question_id; // A unique ID for the question that was answered
    std::chrono::system_clock::time_point timestamp;
};

class FeedbackQueue {
public:
    void push(const FeedbackItem& item);
    bool pop(FeedbackItem& item); // Non-blocking pop
    void cleanup(int max_age_seconds = 60);

private:
    std::queue<FeedbackItem> queue_;
    std::mutex mutex_;
};

#endif // FEEDBACK_QUEUE_H
