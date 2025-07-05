#include "capture.h"
#include <iostream>
#include <memory>
#include <stdexcept>
#include <vector>
#include <sstream>
#include <algorithm>

// --- Headers untuk Implementasi Nyata ---
// Diperlukan untuk menjalankan perintah shell dan membaca outputnya
#include <cstdio>
// Diperlukan untuk Tesseract OCR. Pastikan library telah terinstal.
#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>

// --- Implementasi Nyata ---

/**
 * @brief Menjalankan perintah shell dan mengembalikan output binary-nya.
 */
std::vector<char> exec_binary(const char* cmd) {
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("popen() failed!");
    }
    std::vector<char> buffer(4096);
    std::vector<char> result;
    while (size_t bytes_read = fread(buffer.data(), 1, buffer.size(), pipe.get())) {
        result.insert(result.end(), buffer.data(), buffer.data() + bytes_read);
    }
    return result;
}

/**
 * @brief Mengambil screenshot dari perangkat ADB dan memuatnya ke cv::Mat.
 */
cv::Mat capture_screenshot(const std::string& device_id) {
    std::cout << "[C++] Capturing screenshot from ADB device: " << device_id << std::endl;
    std::string command = "adb -s " + device_id + " exec-out screencap -p";

    try {
        std::vector<char> png_data = exec_binary(command.c_str());
        if (png_data.empty()) {
            std::cerr << "[C++] Error: No data received from ADB screencap." << std::endl;
            return cv::Mat();
        }

        // Decode data PNG langsung dari memori
        cv::Mat image = cv::imdecode(png_data, cv::IMREAD_COLOR);
        if (image.empty()) {
            std::cerr << "[C++] Error: Failed to decode screenshot PNG." << std::endl;
            return cv::Mat();
        }

        std::cout << "[C++] Screenshot captured and decoded successfully." << std::endl;
        return image;

    } catch (const std::exception& e) {
        std::cerr << "[C++] Exception while capturing screenshot: " << e.what() << std::endl;
        return cv::Mat();
    }
}

/**
 * @brief Melakukan OCR pada ROI (Region of Interest) dari gambar menggunakan Tesseract.
 */
std::string perform_ocr(const cv::Mat& image, const cv::Rect& roi) {
    if (image.empty()) return "";

    // Crop gambar ke ROI yang ditentukan
    cv::Mat cropped_image = image(roi);

    // Inisialisasi Tesseract
    tesseract::TessBaseAPI* api = new tesseract::TessBaseAPI();
    if (api->Init(NULL, "eng")) { // Menggunakan bahasa Inggris
        std::cerr << "[C++] Could not initialize tesseract." << std::endl;
        return "";
    }

    // Set gambar untuk di-OCR
    api->SetImage(cropped_image.data, cropped_image.cols, cropped_image.rows, 3, cropped_image.step);
    
    // Dapatkan hasil OCR
    char* outText = api->GetUTF8Text();
    std::string ocr_result(outText);

    // Bersihkan memori
    api->End();
    delete api;
    delete[] outText;

    std::cout << "[C++] OCR performed on region. Text length: " << ocr_result.length() << std::endl;
    return ocr_result;
}

// Helper untuk membersihkan spasi berlebih dari string
std::string trim(const std::string& str) {
    size_t first = str.find_first_not_of(" \t\n\r");
    if (std::string::npos == first) return str;
    size_t last = str.find_last_not_of(" \t\n\r");
    return str.substr(first, (last - first + 1));
}

/**
 * @brief Mem-parsing teks mentah dari OCR menjadi pertanyaan dan pilihan yang terstruktur.
 */
TriviaData parse_text(const std::string& raw_text) {
    TriviaData data;
    std::stringstream ss(raw_text);
    std::string line;
    std::vector<std::string> lines;

    while (std::getline(ss, line)) {
        std::string trimmed_line = trim(line);
        if (!trimmed_line.empty()) {
            lines.push_back(trimmed_line);
        }
    }

    if (lines.empty()) return data;

    bool question_found = false;
    for (const auto& l : lines) {
        if (!question_found) {
            data.question += l + " ";
            if (l.find('?') != std::string::npos) {
                question_found = true;
                data.question = trim(data.question);
            }
        } else {
            if (l.length() > 2 && (l[1] == ')' || l[1] == '.') && std::isupper(l[0])) {
                 data.options.push_back(trim(l));
            }
        }
    }
    
    if (!question_found && !lines.empty()) {
        data.question = lines[0];
    }

    std::cout << "[C++] Parsed Question: " << data.question << std::endl;
    for(size_t i = 0; i < data.options.size(); ++i) {
        std::cout << "[C++] Parsed Option " << i << ": " << data.options[i] << std::endl;
    }

    return data;
}
