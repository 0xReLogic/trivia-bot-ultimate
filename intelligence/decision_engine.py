from intelligence.question_hasher import generate_hash
from intelligence.cache_db import check_cache, save_to_cache
from intelligence.learning_db import find_similar_question, save_learned_answer
from intelligence.embedding_engine import generate_embedding
from intelligence.tinyllm_engine import tiny_llm_engine_instance
from intelligence.api_client import gemini_client_instance
import json

# Load settings
with open('config/settings.json', 'r') as f:
    settings = json.load()

SIMILARITY_THRESHOLD = settings['learning']['similarity_threshold']

def decide_answer(question_text, options_list):
    """
    The core decision-making function.
    It follows a waterfall logic from the fastest/cheapest to the slowest/most expensive source.
    """
    # 1. Check Cache (Fastest)
    cached_answer = check_cache(question_text)
    if cached_answer:
        return {"answer": cached_answer, "source": "cache", "confidence": 1.0}

    # 2. Check Learned Database (Semantic Search)
    question_embedding = generate_embedding(question_text)
    similar_question = find_similar_question(question_text, threshold=SIMILARITY_THRESHOLD)
    if similar_question:
        return {
            "answer": similar_question['correct_answer'], 
            "source": "learned_db", 
            "confidence": similar_question['similarity']
        }

    # 3. Use Local TinyLLM Engine (Fast, Local Inference)
    if settings['ai_tiers']['TinyLLM']['enabled']:
        tinyllm_result = tiny_llm_engine_instance.process_question(question_text, options_list)
        if tinyllm_result:
            return {
                "answer": tinyllm_result['answer'], 
                "source": "tinyllm", 
                "confidence": tinyllm_result['confidence']
            }

    # 4. Use External Gemini API (Most Powerful, Slowest/Most Expensive)
    if gemini_client_instance and settings['ai_tiers']['GeminiAPI']['enabled']:
        gemini_result = gemini_client_instance.ask_gemini(question_text, options_list)
        if gemini_result:
            # When we get a high-confidence answer from the API, we should cache it.
            save_to_cache(question_text, gemini_result['answer'])
            # And also save it to our learning database for future semantic searches.
            save_learned_answer(question_text, gemini_result['answer'], gemini_result['confidence'])
            return {
                "answer": gemini_result['answer'], 
                "source": "gemini_api", 
                "confidence": gemini_result['confidence']
            }

    # If no source could provide an answer
    return {"answer": None, "source": "none", "confidence": 0.0}
