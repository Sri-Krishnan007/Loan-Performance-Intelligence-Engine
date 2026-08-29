import json
import logging
import requests
from src.config import settings

logger = logging.getLogger(__name__)

class GroqClient:
    """Manages raw REST HTTP requests to the Groq Chat Completions API."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_DEFAULT_MODEL
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        """Sends chat completion payload to Groq API endpoint."""
        if not self.api_key:
            logger.error("Groq API key is missing. Ensure GROQ_API_KEY is configured in .env.")
            raise ValueError("Groq API key is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 1024
        }
        
        logger.info(f"Sending request to Groq API using model '{self.model}'...")
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Groq API returned error: Code {response.status_code} - {response.text}")
                response.raise_for_status()
                
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.info("Successfully received completion from Groq API.")
            return content.strip()
            
        except Exception as e:
            logger.error(f"Exception during Groq API completion: {e}")
            raise e
