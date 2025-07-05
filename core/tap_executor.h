#ifndef TAP_EXECUTOR_H
#define TAP_EXECUTOR_H

#include <string>

/**
 * @brief Executes a tap command at the given coordinates using ADB.
 * 
 * @param device_id The ADB device serial ID.
 * @param x The x-coordinate.
 * @param y The y-coordinate.
 * @return bool True if the command was executed successfully, false otherwise.
 */
bool execute_tap(const std::string& device_id, int x, int y);

#endif // TAP_EXECUTOR_H
