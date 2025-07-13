# -*- coding: utf-8 -*-
"""
HAK-GAL Parser-Implementierung
"""

import re
from typing import Optional, Tuple, List

try:
    import lark
    LARK_AVAILABLE = True
except ImportError:
    LARK_AVAILABLE = False

from .grammar import HAKGAL_GRAMMAR


class HAKGALParser:
    """
    Parser für HAK-GAL Formeln.
    Unterstützt sowohl Lark-Parser als auch Regex-Fallback.
    """
    
    def __init__(self):
        """Initialisiert den Parser mit Lark wenn verfügbar."""
        self.parser_available = LARK_AVAILABLE
        if self.parser_available:
            try:
                self.parser = lark.Lark(HAKGAL_GRAMMAR, parser='lalr', debug=False)
                print("✅ Lark-Parser initialisiert")
            except Exception as e:
                print(f"❌ Parser-Initialisierung fehlgeschlagen: {e}")
                self.parser_available = False
        else:
            print("⚠️ Lark-Parser nicht verfügbar, nutze Regex-Fallback")
    
    def parse(self, formula: str) -> Tuple[bool, Optional['lark.Tree'], str]:
        """
        Parst eine HAK-GAL Formel.
        
        Args:
            formula: Die zu parsende Formel
            
        Returns:
            Tuple aus:
            - bool: True wenn erfolgreich geparst
            - Optional[lark.Tree]: Der Parse-Baum (nur bei Lark)
            - str: Status-/Fehlermeldung
        """
        if not self.parser_available:
            return self._regex_fallback(formula)
        
        try:
            tree = self.parser.parse(formula)
            return (True, tree, "Syntax OK")
        except lark.exceptions.LarkError as e:
            return (False, None, f"Parser-Fehler: {e}")
    
    def _regex_fallback(self, formula: str) -> Tuple[bool, None, str]:
        """
        Fallback-Parser mit Regex für grundlegende Syntaxprüfung.
        
        Args:
            formula: Die zu prüfende Formel
            
        Returns:
            Tuple aus Erfolg, None (kein Tree), und Nachricht
        """
        # Grundlegende Syntaxprüfungen
        if not formula.strip().endswith('.'):
            return (False, None, "Formel muss mit '.' enden")
        
        # Prüfe auf ungültige Zeichen
        if not re.match(r'^[A-Za-zÄÖÜäöüß0-9\s\(\),\->&|._-]+$', formula):
            return (False, None, "Ungültige Zeichen")
        
        # Prüfe balancierte Klammern
        if formula.count('(') != formula.count(')'):
            return (False, None, "Unbalancierte Klammern")
        
        return (True, None, "Syntax OK (Regex-Fallback)")
    
    def extract_predicates(self, tree: 'lark.Tree') -> List[str]:
        """
        Extrahiert alle Prädikate aus einem Parse-Baum.
        
        Args:
            tree: Der Lark Parse-Baum
            
        Returns:
            Liste der eindeutigen Prädikate
        """
        if not tree:
            return []
        
        predicates = []
        for node in tree.find_data('atom'):
            if node.children and isinstance(node.children[0], lark.Token) and node.children[0].type == 'PREDICATE':
                predicates.append(str(node.children[0]))
        
        # Duplikate entfernen und Reihenfolge erhalten
        return list(dict.fromkeys(predicates))
