#ifndef PIPE_HANDLER_H
#define PIPE_HANDLER_H

#include <string>
#include <vector>
#include "json.hpp" // Assuming nlohmann/json

using json = nlohmann::json;

namespace ipc {

/**
 * @brief Sends a request to the Python bridge server.
 * 
 * @param request_data JSON object containing the request (e.g., question and options).
 * @return bool True on success, false on failure.
 */
bool send_to_python(const json& request_data);

/**
 * @brief Receives a response from the Python bridge server.
 * 
 * @param timeout_ms The maximum time to wait for a response.
 * @return json The JSON response from Python. Returns an empty json object on failure or timeout.
 */
json receive_from_python(int timeout_ms = 5000);

}

#endif // PIPE_HANDLER_H
