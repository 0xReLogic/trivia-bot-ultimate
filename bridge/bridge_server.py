import json
import time
import os
import sys

# Add intelligence directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'intelligence')))

from decision_engine import decide_answer

CPP_TO_PY_PIPE = os.path.join('temp', 'cpp_to_py.pipe')
PY_TO_CPP_PIPE = os.path.join('temp', 'py_to_cpp.pipe')

def handle_request(request_data):
    """
    Routes the request to the appropriate handler and returns the result.
    """
    request_type = request_data.get("type")
    
    if request_type == "GET_ANSWER":
        question = request_data.get("question")
        options = request_data.get("options")
        if question and options:
            return decide_answer(question, options)
        else:
            return {"error": "Missing question or options"}
    else:
        return {"error": f"Unknown request type: {request_type}"}

def main_loop():
    """
    The main loop for the bridge server.
    Listens for requests from C++ and sends back responses.
    """
    print("Python Bridge Server is running...")
    os.makedirs(os.path.dirname(CPP_TO_PY_PIPE), exist_ok=True)

    while True:
        if os.path.exists(CPP_TO_PY_PIPE):
            try:
                with open(CPP_TO_PY_PIPE, 'r') as f:
                    request_data = json.load(f)
                
                print(f"Received request from C++: {request_data}")
                
                # Process the request
                response_data = handle_request(request_data)
                
                # Write the response
                with open(PY_TO_CPP_PIPE, 'w') as f:
                    json.dump(response_data, f)
                
                # Clean up the request pipe to signal completion
                os.remove(CPP_TO_PY_PIPE)

            except Exception as e:
                print(f"Error processing request: {e}")
                # Clean up in case of error
                if os.path.exists(CPP_TO_PY_PIPE):
                    os.remove(CPP_TO_PY_PIPE)
        
        time.sleep(0.1) # Poll every 100ms

if __name__ == "__main__":
    main_loop()
