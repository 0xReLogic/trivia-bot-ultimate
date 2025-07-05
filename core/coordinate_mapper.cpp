#include "coordinate_mapper.h"
#include <fstream>
#include <iostream>
#include "json.hpp" // Assuming use of a JSON library like nlohmann/json

using json = nlohmann::json;

TapCoordinate get_tap_coordinate(const std::string& option_key, const std::string& config_path) {
    std::ifstream config_file(config_path);
    if (!config_file.is_open()) {
        std::cerr << "Error: Could not open config file: " << config_path << std::endl;
        return {-1, -1};
    }

    try {
        json settings;
        config_file >> settings;

        // Ensure the key exists in the tap_coordinates map
        if (settings["device"]["tap_coordinates"].contains(option_key)) {
            auto coords = settings["device"]["tap_coordinates"][option_key];
            return {coords[0], coords[1]};
        } else {
            std::cerr << "Error: Option key '" << option_key << "' not found in config." << std::endl;
            return {-1, -1};
        }
    } catch (json::exception& e) {
        std::cerr << "Error parsing JSON config: " << e.what() << std::endl;
        return {-1, -1};
    }
}
