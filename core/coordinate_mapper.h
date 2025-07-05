#ifndef COORDINATE_MAPPER_H
#define COORDINATE_MAPPER_H

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>

struct TapCoordinate {
    int x;
    int y;
};

/**
 * @brief Maps an answer option key (e.g., "A", "B", "C", "D") to a screen coordinate.
 * 
 * @param option_key The key of the option to tap.
 * @param config_path The path to the settings.json file.
 * @return TapCoordinate The (x, y) coordinate to tap. Returns {-1, -1} on failure.
 */
TapCoordinate get_tap_coordinate(const std::string& option_key, const std::string& config_path);

#endif // COORDINATE_MAPPER_H
