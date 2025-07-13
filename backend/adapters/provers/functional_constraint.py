# -*- coding: utf-8 -*-
"""
Functional Constraint Prover - Spezialisiert auf funktionale Abhängigkeiten
"""

import re
from typing import Optional, Tuple, List

from backend.api import BaseProver
from backend.core import HAKGALParser


class FunctionalConstraintProver(BaseProver):
    """
    Spezialisierter Prover für funktionale Constraints.
    Behandelt Fälle wie Einwohner(X, Y) wo Y eindeutig sein muss.
    """
    
    def __init__(self):
        """Initialisiert den Prover mit bekannten funktionalen Prädikaten."""
        super().__init__("Functional Constraint Prover")
        self.functional_predicates = {
            'Einwohner', 'Hauptstadt', 'Bevölkerung', 'Fläche',
            'Temperatur', 'Geburtsjahr', 'LiegtIn'
        }
    
    def prove(self, assumptions: List[str], goal: str) -> Tuple[Optional[bool], str]:
        """
        Prüft funktionale Widersprüche.
        
        Ein funktionaler Widerspruch liegt vor, wenn für die gleichen
        Eingabeparameter unterschiedliche Ausgabewerte existieren.
        """
        # Extrahiere Prädikat und Argumente aus dem Ziel
        goal_clean = goal.strip().rstrip('.')
        goal_match = re.match(r'([A-ZÄÖÜ][\w]*)\(([^)]+)\)', goal_clean)
        if not goal_match:
            return None, f"{self.name}: Kein atomares Prädikat erkannt in '{goal_clean}'"
        
        goal_predicate, goal_args = goal_match.groups()
        goal_arg_list = [arg.strip() for arg in goal_args.split(',')]
        
        # Nur funktionale Prädikate behandeln
        if goal_predicate not in self.functional_predicates:
            return None, f"{self.name}: '{goal_predicate}' ist nicht funktional"
        
        # Suche nach widersprüchlichen Fakten in Assumptions
        for assumption in assumptions:
            assume_clean = assumption.strip().rstrip('.')
            assume_match = re.match(r'([A-ZÄÖÜ][\w]*)\(([^)]+)\)', assume_clean)
            if not assume_match:
                continue
            
            assume_predicate, assume_args = assume_match.groups()
            assume_arg_list = [arg.strip() for arg in assume_args.split(',')]
            
            # Gleicher Prädikatname und gleiche erste Argumente?
            if (assume_predicate == goal_predicate and
                len(assume_arg_list) == len(goal_arg_list) and
                len(assume_arg_list) >= 2):
                
                # Prüfe ob erste n-1 Argumente gleich sind, aber letztes unterschiedlich
                if (assume_arg_list[:-1] == goal_arg_list[:-1] and
                    assume_arg_list[-1] != goal_arg_list[-1]):
                    
                    # FUNKTIONALER WIDERSPRUCH!
                    return False, (
                        f"{self.name}: Funktionaler Widerspruch - "
                        f"{goal_predicate} kann für {assume_arg_list[:-1]} "
                        f"nicht sowohl {assume_arg_list[-1]} als auch "
                        f"{goal_arg_list[-1]} sein"
                    )
        
        return None, f"{self.name}: Kein funktionaler Widerspruch gefunden"
    
    def validate_syntax(self, formula: str) -> Tuple[bool, str]:
        """Verwendet den HAKGALParser für Syntaxvalidierung."""
        return HAKGALParser().parse(formula)[0::2]
