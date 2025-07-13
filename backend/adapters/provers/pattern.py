# -*- coding: utf-8 -*-
"""
Pattern Matcher Prover - Einfacher Musterabgleich
"""

from typing import Optional, Tuple, List

from backend.api import BaseProver
from backend.core import HAKGALParser


class PatternProver(BaseProver):
    """
    Einfacher Prover der auf exakten Musterabgleich basiert.
    Findet direkte Übereinstimmungen und Widersprüche.
    """
    
    def __init__(self):
        """Initialisiert den Pattern Matcher."""
        super().__init__("Pattern Matcher")
    
    def prove(self, assumptions: List[str], goal: str) -> Tuple[Optional[bool], str]:
        """
        Sucht nach exakten Übereinstimmungen oder Widersprüchen.
        
        Args:
            assumptions: Liste von Annahmen
            goal: Das zu beweisende Ziel
            
        Returns:
            - (True, msg) wenn exakte Übereinstimmung gefunden
            - (False, msg) wenn Widerspruch gefunden
            - (None, msg) wenn keine Übereinstimmung
        """
        # Direkte Übereinstimmung?
        if goal in assumptions:
            return (True, f"{self.name} fand exakten Match für '{goal}'.")
        
        # Negation vorhanden?
        neg_goal = f"-{goal}" if not goal.startswith('-') else goal[1:]
        if neg_goal in assumptions:
            return (False, f"{self.name} fand Widerspruch für '{goal}'.")
        
        return (None, f"{self.name} fand keine Übereinstimmung.")
    
    def validate_syntax(self, formula: str) -> Tuple[bool, str]:
        """Verwendet den HAKGALParser für Syntaxvalidierung."""
        return HAKGALParser().parse(formula)[0::2]
