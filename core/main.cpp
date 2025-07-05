#include <iostream>
#include <thread>
#include <chrono>
#include <vector>

#include "capture.h"
#include "robust_screenshot_validator.h"
#include "ui_elements_detector.h"
#include "matcher.h"
#include "coordinate_mapper.h"
#include "tap_executor.h"
#include "bridge/pipe_handler.h"
#include "json.hpp"

using json = nlohmann::json;

// Bot's finite state machine states
enum class GameState {
    LOOKING_FOR_GAME,
    PLAYING_TRIVIA,
    GAME_ENDED,
    RECOVERY
};

// --- Main Application Logic ---
int main(int argc, char** argv) {
    std::cout << "--- Trivia Bot Ultimate --- Starting..." << std::endl;

    // Assume the Python bridge server is started separately.
    // In a real application, you might launch it from here.
    std::cout << "Please ensure the Python bridge server is running: python bridge/bridge_server.py" << std::endl;

    std::string device_id = "emulator-5554"; // Should be loaded from config
    std::string config_path = "config/settings.json";
    GameState current_state = GameState::LOOKING_FOR_GAME;
    bool running = true;

    // Main game loop
    while (running) {
        switch (current_state) {
            case GameState::LOOKING_FOR_GAME: {
                std::cout << "\n[State: LOOKING_FOR_GAME]" << std::endl;
                // In a real scenario, we would look for a "Start" or "Play" button.
                // For this simulation, we will assume a game is found and transition to playing.
                std::cout << "Looking for a new game to start... Found one!" << std::endl;
                current_state = GameState::PLAYING_TRIVIA;
                std::this_thread::sleep_for(std::chrono::seconds(2));
                break;
            }

            case GameState::PLAYING_TRIVIA: {
                std::cout << "\n[State: PLAYING_TRIVIA]" << std::endl;
                
                // 1. Capture & Validate Screenshot
                cv::Mat screen = capture_screenshot(device_id);
                if (!validate_screenshot(screen)) {
                    std::cerr << "Screenshot validation failed. Entering recovery state." << std::endl;
                    current_state = GameState::RECOVERY;
                    continue;
                }

                // 2. OCR & Parse Text
                // For this simulation, we use the whole screen. A real implementation would use OCR regions from config.
                cv::Rect ocr_region(0, 0, screen.cols, screen.rows);
                std::string ocr_text = perform_ocr(screen, ocr_region);
                TriviaData trivia = parse_text(ocr_text);

                if (trivia.question.empty() || trivia.options.size() < 4) {
                    std::cout << "Could not parse a valid question. Maybe the game has ended?" << std::endl;
                    current_state = GameState::GAME_ENDED;
                    continue;
                }

                // 3. Communicate with Python Intelligence Core
                json request;
                request["type"] = "GET_ANSWER";
                request["question"] = trivia.question;
                request["options"] = trivia.options;

                std::cout << "Sending question to Python: " << trivia.question << std::endl;
                if (!ipc::send_to_python(request)) {
                    std::cerr << "Failed to send request to Python. Entering recovery state." << std::endl;
                    current_state = GameState::RECOVERY;
                    continue;
                }

                json response = ipc::receive_from_python(10000); // 10-second timeout
                if (response.empty() || response.value("answer", "").empty()) {
                    std::cerr << "Failed to get a valid answer from Python. Entering recovery state." << std::endl;
                    current_state = GameState::RECOVERY;
                    continue;
                }

                std::string chosen_answer = response["answer"];
                std::cout << "Received answer from Python: " << chosen_answer 
                          << " (Source: " << response.value("source", "N/A") 
                          << ", Confidence: " << response.value("confidence", 0.0) << ")" << std::endl;

                // 4. Match Answer and Execute Tap
                MatchResult match = find_best_match(chosen_answer, trivia.options);
                if (match.confidence_score < 0.7) { // If the match is poor
                    std::cerr << "Could not confidently match answer to options. Skipping tap." << std::endl;
                } else {
                    // Map option index to key ("A", "B", "C", "D")
                    std::string option_key = std::string(1, 'A' + match.match_index);
                    TapCoordinate coords = get_tap_coordinate(option_key, config_path);
                    if (coords.x != -1) {
                        execute_tap(device_id, coords.x, coords.y);
                        std::cout << "Tapped option " << option_key << " at (" << coords.x << ", " << coords.y << ")" << std::endl;
                    }
                }

                // 5. Wait before next cycle (simulating gameplay delay)
                std::this_thread::sleep_for(std::chrono::seconds(5));
                break;
            }

            case GameState::GAME_ENDED: {
                std::cout << "\n[State: GAME_ENDED]" << std::endl;
                // Here you would look for a "Play Again" button and tap it.
                std::cout << "Game has ended. Looking for 'Play Again' button..." << std::endl;
                std::this_thread::sleep_for(std::chrono::seconds(3));
                std::cout << "Tapping 'Play Again' and returning to LOOKING_FOR_GAME state." << std::endl;
                current_state = GameState::LOOKING_FOR_GAME;
                break;
            }

            case GameState::RECOVERY: {
                std::cout << "\n[State: RECOVERY]" << std::endl;
                std::cout << "An error occurred. Waiting for 10 seconds before trying again..." << std::endl;
                std::this_thread::sleep_for(std::chrono::seconds(10));
                std::cout << "Recovery complete. Returning to LOOKING_FOR_GAME state." << std::endl;
                current_state = GameState::LOOKING_FOR_GAME;
                break;
            }
        }
    }

    std::cout << "--- Trivia Bot Ultimate --- Shutting down." << std::endl;
    return 0;
}
