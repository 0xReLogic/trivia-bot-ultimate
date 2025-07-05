#include "feedback_queue.h"

void FeedbackQueue::push(const FeedbackItem& item) {
    std::lock_guard<std::mutex> lock(mutex_);
    queue_.push(item);
}

bool FeedbackQueue::pop(FeedbackItem& item) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (queue_.empty()) {
        return false;
    }
    item = queue_.front();
    queue_.pop();
    return true;
}

void FeedbackQueue::cleanup(int max_age_seconds) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto now = std::chrono::system_clock::now();
    
    while (!queue_.empty()) {
        auto& front_item = queue_.front();
        auto age = std::chrono::duration_cast<std::chrono::seconds>(now - front_item.timestamp).count();
        if (age > max_age_seconds) {
            queue_.pop(); // Remove old item
        } else {
            break; // The rest are newer
        }
    }
}
