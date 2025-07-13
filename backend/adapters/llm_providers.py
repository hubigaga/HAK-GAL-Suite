# -*- coding: utf-8 -*-
"""
LLM Provider Implementierungen
"""

from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("❌ FEHLER: 'openai' nicht gefunden. Bitte mit 'pip install openai' installieren.")
    OpenAI = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from backend.api import BaseLLMProvider


class DeepSeekProvider(BaseLLMProvider):
    """
    Provider für DeepSeek LLM API.
    Verwendet OpenAI-kompatible API mit angepasster Base-URL.
    """
    
    def __init__(self, api_key: str, model_name: str = "deepseek-chat"):
        """
        Initialisiert den DeepSeek Provider.
        
        Args:
            api_key: API-Schlüssel für DeepSeek
            model_name: Name des zu verwendenden Modells
        """
        super().__init__(model_name)
        if not OpenAI:
            raise ImportError("OpenAI-Bibliothek nicht verfügbar")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
    
    def query(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """Sendet eine Anfrage an DeepSeek."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()


class MistralProvider(BaseLLMProvider):
    """
    Provider für Mistral AI API.
    Verwendet OpenAI-kompatible API mit angepasster Base-URL.
    """
    
    def __init__(self, api_key: str, model_name: str = "mistral-large-latest"):
        """
        Initialisiert den Mistral Provider.
        
        Args:
            api_key: API-Schlüssel für Mistral
            model_name: Name des zu verwendenden Modells
        """
        super().__init__(model_name)
        if not OpenAI:
            raise ImportError("OpenAI-Bibliothek nicht verfügbar")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1/"
        )
    
    def query(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """Sendet eine Anfrage an Mistral."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()


class GeminiProvider(BaseLLMProvider):
    """
    Provider für Google Gemini API.
    Verwendet die native Google Generative AI Bibliothek.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro-latest"):
        """
        Initialisiert den Gemini Provider.
        
        Args:
            api_key: API-Schlüssel für Gemini
            model_name: Name des zu verwendenden Modells
        """
        super().__init__(model_name)
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Gemini Bibliothek nicht installiert.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def query(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """Sendet eine Anfrage an Gemini."""
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = self.model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        return response.text.strip()
