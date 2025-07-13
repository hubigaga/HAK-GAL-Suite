# -*- coding: utf-8 -*-
"""
Abstrakte Basisklasse für Prover
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List


class BaseProver(ABC):
    """
    Abstrakte Basisklasse für alle Prover-Implementierungen.
    Definiert das Interface für logische Beweisführung.
    """
    
    def __init__(self, name: str):
        """
        Initialisiert den Prover mit einem Namen.
        
        Args:
            name: Name des Provers für Logging und Identifikation
        """
        self.name = name
    
    @abstractmethod
    def prove(self, assumptions: List[str], goal: str) -> Tuple[Optional[bool], str]:
        """
        Versucht, ein Ziel aus gegebenen Annahmen zu beweisen.
        
        Args:
            assumptions: Liste von logischen Formeln als Annahmen
            goal: Die zu beweisende Zielformel
            
        Returns:
            Tuple aus:
            - Optional[bool]: True wenn bewiesen, False wenn widerlegt, None wenn unbestimmt
            - str: Begründung oder Fehlermeldung
        """
        pass
    
    @abstractmethod
    def validate_syntax(self, formula: str) -> Tuple[bool, str]:
        """
        Validiert die Syntax einer logischen Formel.
        
        Args:
            formula: Die zu validierende Formel
            
        Returns:
            Tuple aus:
            - bool: True wenn Syntax gültig, False sonst
            - str: Nachricht über den Validierungsstatus
        """
        pass
