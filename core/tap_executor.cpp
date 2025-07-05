#include "tap_executor.h"
#include <iostream>
#include <cstdlib> // For system()

bool execute_tap(const std::string& device_id, int x, int y) {
    std::string command = "adb -s " + device_id + " shell input tap " + std::to_string(x) + " " + std::to_string(y);
    std::cout << "Executing tap command: " << command << std::endl;

    try {
        int return_code = system(command.c_str());
        if (return_code != 0) {
            std::cerr << "ADB tap command failed with return code: " << return_code << std::endl;
            return false;
        }
        // In a real scenario, you might want to verify the tap, 
        // but for now, a zero return code is our success metric.
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Exception while executing tap command: " << e.what() << std::endl;
        return false;
    }
}
