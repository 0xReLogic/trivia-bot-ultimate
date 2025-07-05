#include "matcher.h"
#include <vector>
#include <algorithm>
#include <numeric>

unsigned int levenshtein_distance(const std::string& s1, const std::string& s2) {
    const std::size_t len1 = s1.size(), len2 = s2.size();
    std::vector<unsigned int> col(len2 + 1), prev_col(len2 + 1);

    std::iota(prev_col.begin(), prev_col.end(), 0);

    for (unsigned int i = 0; i < len1; i++) {
        col[0] = i + 1;
        for (unsigned int j = 0; j < len2; j++) {
            col[j + 1] = std::min({ prev_col[j + 1] + 1, col[j] + 1, prev_col[j] + (s1[i] == s2[j] ? 0 : 1) });
        }
        col.swap(prev_col);
    }
    return prev_col[len2];
}

MatchResult find_best_match(const std::string& target, const std::vector<std::string>& candidates) {
    MatchResult best_result = {"", 0.0, -1};
    if (candidates.empty()) {
        return best_result;
    }

    int best_distance = -1;

    for (int i = 0; i < candidates.size(); ++i) {
        unsigned int distance = levenshtein_distance(target, candidates[i]);
        if (best_distance == -1 || distance < best_distance) {
            best_distance = distance;
            best_result.best_match = candidates[i];
            best_result.match_index = i;
        }
    }

    // Calculate confidence score
    if (best_distance != -1) {
        double max_len = std::max(target.length(), best_result.best_match.length());
        if (max_len > 0) {
            best_result.confidence_score = 1.0 - (static_cast<double>(best_distance) / max_len);
        }
    }

    return best_result;
}
