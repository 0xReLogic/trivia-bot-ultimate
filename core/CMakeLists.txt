# Menentukan versi minimum CMake yang dibutuhkan
cmake_minimum_required(VERSION 3.10)

# Menentukan nama proyek
project(TriviaBotCore CXX)

# Mengatur standar C++ ke C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Menemukan paket OpenCV yang wajib ada
find_package(OpenCV REQUIRED)
# Menemukan paket Tesseract yang wajib ada
find_package(Tesseract REQUIRED)

# Menambahkan direktori header dari library yang ditemukan
include_directories(${OpenCV_INCLUDE_DIRS} ${Tesseract_INCLUDE_DIRS})

# Mengumpulkan semua file source (.cpp) di direktori saat ini
# (Asumsi file ini ada di dalam direktori 'core/')
file(GLOB_RECURSE SOURCES "*.cpp" "../bridge/*.cpp")

# Membuat file executable dari file-file source
add_executable(trivia_bot ${SOURCES})

# Menautkan executable dengan library yang dibutuhkan
target_link_libraries(trivia_bot PRIVATE ${OpenCV_LIBS} ${Tesseract_LIBRARIES})

# Menentukan direktori output untuk executable
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
