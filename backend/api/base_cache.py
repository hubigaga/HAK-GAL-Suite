# -*- coding: utf-8 -*-
"""
Abstrakte Basisklasse für Cache-Implementierungen
"""

from abc import ABC
from typing import Dict, Any, Optional


class BaseCache(ABC):
    """
    Abstrakte Basisklasse für Cache-Implementierungen.
    Bietet grundlegende Cache-Funktionalität mit Hit/Miss-Statistiken.
    """
    
    def __init__(self):
        """Initialisiert einen leeren Cache mit Statistiken."""
        self.cache: Dict[Any, Any] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: Any) -> Optional[Any]:
        """
        Holt einen Wert aus dem Cache.
        
        Args:
            key: Der Schlüssel des zu holenden Werts
            
        Returns:
            Der gecachte Wert oder None wenn nicht vorhanden
        """
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: Any, value: Any):
        """
        Fügt einen Wert in den Cache ein.
        
        Args:
            key: Der Schlüssel für den Wert
            value: Der zu cachende Wert
        """
        self.cache[key] = value
    
    def clear(self):
        """Leert den Cache und setzt Statistiken zurück."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        print("   [Cache] Cache geleert.")
    
    @property
    def size(self) -> int:
        """Gibt die Anzahl der gecachten Einträge zurück."""
        return len(self.cache)
    
    @property
    def hit_rate(self) -> float:
        """
        Berechnet die Cache-Hit-Rate in Prozent.
        
        Returns:
            Hit-Rate als Prozentwert (0.0-100.0)
        """
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
