# -*- coding: utf-8 -*-
"""
Abstrakte Basisklasse für LLM-Provider
"""

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Abstrakte Basisklasse für alle LLM-Provider.
    Definiert das Interface für die Kommunikation mit Large Language Models.
    """
    
    def __init__(self, model_name: str):
        """
        Initialisiert den Provider mit einem Modellnamen.
        
        Args:
            model_name: Name des zu verwendenden Modells
        """
        self.model_name = model_name
    
    @abstractmethod
    def query(self, prompt: str, system_prompt: str, temperature: float) -> str:
        """
        Sendet eine Anfrage an das LLM und gibt die Antwort zurück.
        
        Args:
            prompt: Die Benutzeranfrage
            system_prompt: Der System-Prompt für das LLM
            temperature: Temperatur-Parameter für die Generierung (0.0-1.0)
            
        Returns:
            Die Antwort des LLMs als String
        """
        pass
