#include "pipe_handler.h"
#include <fstream>
#include <iostream>
#include <thread>
#include <chrono>
#include <filesystem>

namespace fs = std::filesystem;

const fs::path CPP_TO_PY_PIPE = "temp/cpp_to_py.pipe";
const fs::path PY_TO_CPP_PIPE = "temp/py_to_cpp.pipe";

namespace ipc {

bool send_to_python(const json& request_data) {
    try {
        fs::create_directories(CPP_TO_PY_PIPE.parent_path());
        std::ofstream pipe(CPP_TO_PY_PIPE, std::ios::out | std::ios::trunc);
        if (!pipe.is_open()) {
            std::cerr << "Error: Could not open pipe for writing: " << CPP_TO_PY_PIPE << std::endl;
            return false;
        }
        pipe << request_data.dump();
        pipe.close();
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Exception in send_to_python: " << e.what() << std::endl;
        return false;
    }
}

json receive_from_python(int timeout_ms) {
    auto start_time = std::chrono::steady_clock::now();
    while (true) {
        if (fs::exists(PY_TO_CPP_PIPE)) {
            std::ifstream pipe(PY_TO_CPP_PIPE);
            if (pipe.is_open()) {
                json response_data;
                pipe >> response_data;
                pipe.close();
                fs::remove(PY_TO_CPP_PIPE); // Consume the pipe file
                return response_data;
            }
        }

        auto current_time = std::chrono::steady_clock::now();
        auto elapsed_time = std::chrono::duration_cast<std::chrono::milliseconds>(current_time - start_time).count();
        if (elapsed_time > timeout_ms) {
            std::cerr << "Timeout: No response from Python within " << timeout_ms << "ms." << std::endl;
            return json({}); // Return empty json on timeout
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(50)); // Poll every 50ms
    }
}

}
