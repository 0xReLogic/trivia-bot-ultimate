#!/bin/bash

# =========================================
# TRIVIA BOT ULTIMATE - STARTUP SCRIPT
# =========================================

echo "--- Starting Trivia Bot Ultimate ---"

# --- Variabel ---
EXECUTABLE_NAME="trivia_bot"
BUILD_DIR="build"

# Function for graceful shutdown
cleanup() {
    echo "\n--- Shutting down Trivia Bot Ultimate ---"
    # Kill the Python bridge server process
    if [ ! -z "$PYTHON_PID" ]; then
        echo "Stopping Python Bridge Server (PID: $PYTHON_PID)..."
        kill $PYTHON_PID
    fi
    echo "Shutdown complete."
    exit 0
}

# Trap signals for graceful shutdown
trap cleanup SIGINT SIGTERM

# 1. Kompilasi C++ Core menggunakan CMake
echo "--- Compiling C++ Core ---"
if [ ! -f "core/CMakeLists.txt" ]; then
    echo "Error: core/CMakeLists.txt not found!"
    exit 1
fi

mkdir -p $BUILD_DIR && cd $BUILD_DIR
cmake ../core
make

if [ $? -ne 0 ]; then
    echo "C++ compilation failed!"
    exit 1
fi

# Pindah kembali ke direktori root
cd ..
echo "C++ Core compiled successfully."

# 2. Check for C++ executable
if [ ! -f "$BUILD_DIR/$EXECUTABLE_NAME" ]; then
    echo "Error: C++ executable '$EXECUTABLE_NAME' not found in '$BUILD_DIR/' directory."
    exit 1
fi

# 3. Initialize the database (if it doesn't exist)
echo "--- Initializing Python Environment ---"
python3 intelligence/database_setup.py

# 4. Start the Python Bridge Server in the background
echo "Starting Python Bridge Server..."
python3 bridge/bridge_server.py > logs/bridge_server.log 2>&1 &
PYTHON_PID=$!

# Check if the Python server started successfully
sleep 2
if ! ps -p $PYTHON_PID > /dev/null; then
   echo "Error: Python Bridge Server failed to start. Check logs/bridge_server.log"
   exit 1
fi
echo "Python Bridge Server is running with PID: $PYTHON_PID"

# 5. Start the C++ Performance Core in the foreground
echo "--- Starting C++ Performance Core ---"
./$BUILD_DIR/$EXECUTABLE_NAME

# 6. Cleanup after the C++ application exits
cleanup
