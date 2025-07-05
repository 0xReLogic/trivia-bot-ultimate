import requests
import json
import time

# Load API settings from the main config file
with open('config/settings.json', 'r') as f:
    settings = json.load()

GEMINI_CONFIG = settings['ai_tiers']['GeminiAPI']

class GeminiClient:
    def __init__(self, api_key, endpoint, max_retries=3, backoff_factor=1):
        self.api_key = api_key
        self.endpoint = endpoint
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def ask_gemini(self, question, options, context=""):
        """
        Asks a question to the Gemini API with retry logic.
        """
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY":
            print("Gemini API key is not configured.")
            return None

        prompt = self._construct_prompt(question, options, context)
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.endpoint}?key={self.api_key}",
                    headers=headers,
                    json=data
                )
                response.raise_for_status() # Raise an exception for bad status codes
                return self._parse_response(response.json())
            except requests.exceptions.RequestException as e:
                print(f"Gemini API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_factor * (2 ** attempt))
                else:
                    return None

    def _construct_prompt(self, question, options, context):
        options_str = "\n".join([f"- {opt}" for opt in options])
        return f"Context: {context}\n\nQuestion: {question}\n\nOptions:\n{options_str}\n\nWhich is the correct option?"

    def _parse_response(self, response):
        # This parsing is based on a hypothetical Gemini response structure.
        # It needs to be adapted to the actual API response format.
        try:
            # Assuming the response is in a structure like: {"candidates": [{"content": {"parts": [{"text": "C"}]}}]}
            answer = response['candidates'][0]['content']['parts'][0]['text']
            return {"answer": answer.strip(), "confidence": 0.95} # High confidence for API
        except (KeyError, IndexError) as e:
            print(f"Error parsing Gemini response: {e}")
            return None

# Create a single client instance
if GEMINI_CONFIG['enabled']:
    gemini_client_instance = GeminiClient(GEMINI_CONFIG['api_key'], GEMINI_CONFIG['endpoint'])
else:
    gemini_client_instance = None
