# -*- coding: utf-8 -*-
"""
Cache-Implementierungen für Performance-Optimierung
"""

import time
from typing import Optional, Tuple, Any

from backend.api import BaseCache


class ProofCache(BaseCache):
    """
    Spezialisierter Cache für logische Beweise.
    Speichert Beweisergebnisse mit Zeitstempeln.
    """
    
    def get(self, query_str: str, key: Tuple) -> Optional[Tuple[bool, str, float]]:
        """
        Holt ein Beweisergebnis aus dem Cache.
        
        Args:
            query_str: Die Anfrage (für Logging)
            key: Der Cache-Schlüssel
            
        Returns:
            Tuple aus (Erfolg, Begründung, Zeitstempel) oder None
        """
        return super().get(key)
    
    def put(self, query_str: str, key: Tuple, success: bool, reason: str):
        """
        Speichert ein Beweisergebnis im Cache.
        
        Args:
            query_str: Die Anfrage (für Logging)
            key: Der Cache-Schlüssel
            success: Ob der Beweis erfolgreich war
            reason: Die Begründung
        """
        super().put(key, (success, reason, time.time()))


class PromptCache(BaseCache):
    """
    Cache für LLM-Prompts und deren Antworten.
    Vermeidet redundante API-Aufrufe.
    """
    
    def get(self, prompt: str) -> Optional[str]:
        """
        Holt eine gecachte LLM-Antwort.
        
        Args:
            prompt: Der Prompt als Schlüssel
            
        Returns:
            Die gecachte Antwort oder None
        """
        return super().get(prompt)
    
    def put(self, prompt: str, response: str):
        """
        Speichert eine LLM-Antwort im Cache.
        
        Args:
            prompt: Der Prompt als Schlüssel
            response: Die zu cachende Antwort
        """
        super().put(prompt, response)
