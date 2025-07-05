import os
from utils.logger import log
from utils.config_manager import config

# Conditional import for llama-cpp-python
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class TinyLLMEngine:
    def __init__(self):
        self.model = None
        self.model_path = config.get("ai_tiers.TinyLLM.model_path", "models/tinyllm.bin")
        
        if not Llama:
            log.warning("llama-cpp-python not found. TinyLLM will be disabled. `pip install llama-cpp-python`")
            return

        if os.path.exists(self.model_path):
            try:
                log.info(f"Initializing TinyLLM from: {self.model_path} using llama-cpp-python")
                # n_gpu_layers=-1 akan mencoba offload semua layer ke GPU jika memungkinkan
                self.model = Llama(
                    model_path=self.model_path,
                    n_ctx=2048,      # Konteks yang cukup untuk prompt trivia
                    n_threads=8,     # Sesuaikan dengan CPU Anda
                    n_gpu_layers=-1, # Offload semua layer ke GPU jika ada
                    verbose=False
                )
                log.info("TinyLLM Engine (llama-cpp-python) initialized successfully.")
            except Exception as e:
                log.error(f"Failed to load TinyLLM model with llama-cpp: {e}")
        else:
            log.warning(f"TinyLLM model file not found at {self.model_path}. The engine will be disabled.")

    def process_question(self, question_text, options_list):
        if not self.model:
            return None

        options_formatted = "\n".join([f"- {opt}" for opt in options_list])
        system_prompt = "You are an expert trivia assistant. Your task is to identify the most likely correct answer from the given options. Respond with only the text of the correct option and nothing else."
        user_prompt = f"Question: {question_text}\n\nOptions:\n{options_formatted}"

        try:
            log.debug(f"Sending prompt to TinyLLM (llama-cpp): {user_prompt}")
            
            response = self.model.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=50, # Jawaban seharusnya pendek
                temperature=0.1
            )
            
            response_text = response['choices'][0]['message']['content'].strip()
            log.info(f"Received response from TinyLLM: {response_text}")

            # Cari jawaban yang paling cocok dari opsi yang ada
            # Ini lebih andal daripada fuzzy matching biasa
            best_match = None
            highest_score = -1

            for option in options_list:
                if option.lower() in response_text.lower():
                    score = len(option)
                    if score > highest_score:
                        highest_score = score
                        best_match = option

            if best_match:
                log.info(f"TinyLLM chose: '{best_match}' from response.")
                return {"answer": best_match, "confidence": 0.75} # Confidence is higher due to better prompting
            else:
                log.warning(f"TinyLLM response '{response_text}' did not clearly match any option.")
                return None

        except Exception as e:
            log.error(f"Error during TinyLLM inference with llama-cpp: {e}")
            return None

# Create a single instance
tiny_llm_engine_instance = TinyLLMEngine()
