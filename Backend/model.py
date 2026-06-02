import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_URL = "https://ollama.com/api/generate"

def generate_llm_response(prompt: str):

    payload = {
        "model": "qwen3-vl:235b-instruct-cloud",
        "prompt": prompt,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

        return response.json()["response"]

    except Exception as e:
        return f"LLM Error: {str(e)}"

