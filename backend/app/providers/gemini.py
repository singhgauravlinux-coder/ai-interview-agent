import json
from google import genai
from google.genai import types
from app.config import settings
from app.providers.base import AIProvider

class GeminiProvider(AIProvider):
    def __init__(self):
        if not settings.google_api_key:
            raise RuntimeError("GOOGLE_API_KEY is required when AI_PROVIDER=gemini")
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.gemini_model

    def generate_json(self, *, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> dict:
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=temperature,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response")
        return json.loads(response.text)
