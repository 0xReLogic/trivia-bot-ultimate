#ifndef MATCHER_H
#define MATCHER_H

#include <string>
#include <vector>

struct MatchResult {
    std::string best_match;
    double confidence_score; // 0.0 (no match) to 1.0 (perfect match)
    int match_index; // Index of the best match in the provided list
};

/**
 * @brief Calculates the Levenshtein distance between two strings.
 * 
 * @param s1 The first string.
 * @param s2 The second string.
 * @return unsigned int The Levenshtein distance.
 */
unsigned int levenshtein_distance(const std::string& s1, const std::string& s2);

/**
 * @brief Finds the best fuzzy match for a target string within a list of candidates.
 * 
 * @param target The string to find (e.g., the answer from the decision engine).
 * @param candidates A vector of strings to search within (e.g., the OCR'd options).
 * @return MatchResult The best match found, along with its confidence score and index.
 */
MatchResult find_best_match(const std::string& target, const std::vector<std::string>& candidates);

#endif // MATCHER_H
