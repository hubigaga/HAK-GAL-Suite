# -*- coding: utf-8 -*-
"""
Wolfram Alpha Integration
"""

import os
import re
from typing import Optional, Tuple, List, Dict, Any

try:
    import wolframalpha
    WOLFRAM_AVAILABLE = True
except ImportError:
    WOLFRAM_AVAILABLE = False
    wolframalpha = None

from backend.api import BaseProver


class WolframProver(BaseProver):
    """
    Prover der Wolfram Alpha als externes Orakel für Faktenwissen nutzt.
    Spezialisiert auf Faktenfragen zu Geographie, Mathematik, etc.
    """
    
    def __init__(self):
        """Initialisiert den Wolfram-Prover mit API-Client."""
        super().__init__("Wolfram|Alpha Orakel")
        
        app_id = os.getenv("WOLFRAM_APP_ID")
        if not app_id or app_id == "your_wolfram_app_id_here":
            self.client = None
            return
        
        # Debug-Modus aus .env lesen
        self.debug = os.getenv("WOLFRAM_DEBUG", "false").lower() == "true"
        
        if not WOLFRAM_AVAILABLE:
            self.client = None
            print("⚠️ wolframalpha nicht verfügbar")
            return
        
        try:
            self.client = wolframalpha.Client(app_id)
            self.cache: Dict[str, Tuple[bool, str, float]] = {}
            self.cache_timeout = 3600
            print("✅ WolframProver erfolgreich initialisiert")
            if self.debug:
                print(f"   🐛 Debug-Modus aktiviert für Wolfram-Prover")
        except Exception as e:
            self.client = None
            print(f"⚠️ Wolfram-Initialisierung fehlgeschlagen: {e}")
    
    def prove(self, assumptions: List[str], goal: str) -> Tuple[Optional[bool], str]:
        """
        Versucht eine Faktenfrage mit Wolfram Alpha zu beantworten.
        
        Unterstützt nur atomare Fakten, keine logischen Operatoren.
        """
        if not self.client:
            return None, "WolframProver ist nicht konfiguriert."
        
        # Logische Operatoren werden nicht unterstützt
        if any(op in goal for op in ["->", "&", "|", "all "]):
            return None, "WolframProver unterstützt nur atomare Fakten."
        
        # Einfache Übersetzung
        query = self._simple_translate(goal)
        if not query:
            return None, "Konnte Formel nicht übersetzen."
        
        # Cache-Check
        if query in self.cache:
            import time
            cached_result, cached_reason, cached_time = self.cache[query]
            if time.time() - cached_time < self.cache_timeout:
                return cached_result, f"{cached_reason} (aus Cache)"
        
        # OPTIMIERT: Direkt HTTP-Aufruf
        try:
            import urllib.parse
            import urllib.request
            import xml.etree.ElementTree as ET
            
            app_id = os.getenv("WOLFRAM_APP_ID")
            encoded_query = urllib.parse.quote(query)
            url = f"http://api.wolframalpha.com/v2/query?input={encoded_query}&appid={app_id}&format=plaintext"
            
            # Schneller HTTP-Aufruf mit kurzem Timeout
            with urllib.request.urlopen(url, timeout=5) as response:
                xml_data = response.read().decode('utf-8')
                root = ET.fromstring(xml_data)
                
                # Extrahiere erste brauchbare Antwort
                for pod in root.findall('.//pod'):
                    for subpod in pod.findall('.//subpod'):
                        plaintext_elem = subpod.find('plaintext')
                        if plaintext_elem is not None and plaintext_elem.text:
                            answer = plaintext_elem.text.strip()
                            if answer and len(answer) > 2:
                                # Intelligente Interpretation
                                answer_lower = answer.lower()
                                query_lower = query.lower()
                                
                                # Hauptstadt-Anfragen
                                if 'capital' in query_lower:
                                    if any(city in answer_lower for city in [
                                        'london', 'berlin', 'paris', 'madrid', 'rome', 'moscow'
                                    ]):
                                        result = (True, f"Hauptstadt: {answer}")
                                        self._cache_result(query, result)
                                        return result
                                
                                # Bevölkerungs-Anfragen
                                if 'population' in query_lower:
                                    if any(char.isdigit() for char in answer):
                                        result = (True, f"Bevölkerung: {answer}")
                                        self._cache_result(query, result)
                                        return result
                                
                                # Allgemeine Datenantworten
                                if len(answer) > 5:
                                    result = (True, f"Wolfram: {answer}")
                                    self._cache_result(query, result)
                                    return result
                
                return None, "Keine verwertbare Antwort von Wolfram Alpha"
                
        except Exception as e:
            return None, f"Wolfram-Fehler: {type(e).__name__}"
    
    def validate_syntax(self, formula: str) -> Tuple[bool, str]:
        """Validiert Syntax für Wolfram-Anfragen."""
        if not formula.strip().endswith('.'):
            return False, "Formel muss mit '.' enden"
        if any(op in formula for op in ["->", "&", "|", "all "]):
            return False, "Wolfram unterstützt keine logischen Operatoren"
        return True, "Syntax für Wolfram-Anfrage OK"
    
    def _cache_result(self, query: str, result: Tuple[Optional[bool], str]):
        """Speichert ein Ergebnis im Cache."""
        import time
        self.cache[query] = (result[0], result[1], time.time())
    
    def clear_cache(self):
        """Leert den Wolfram-Cache."""
        self.cache.clear()
    
    def _simple_translate(self, formula: str) -> str:
        """
        Einfache HAK-GAL zu natürlicher Sprache Übersetzung.
        
        Args:
            formula: HAK-GAL Formel
            
        Returns:
            Natürlichsprachliche Anfrage für Wolfram
        """
        formula = formula.strip().removesuffix('.')
        
        # Variable-Handling für Wolfram
        if ', x)' in formula or ', y)' in formula or ', z)' in formula:
            # Einwohner(Wien, x) -> "population of Vienna"
            if 'Einwohner(' in formula:
                match = re.search(r'Einwohner\(([^,]+),', formula)
                if match:
                    city = match.group(1).lower()
                    return f"population of {city}"
            
            # Hauptstadt(x, Berlin) -> "country with capital Berlin"
            if 'Hauptstadt(' in formula and 'Hauptstadt(x' in formula:
                match = re.search(r'Hauptstadt\(x,\s*([^)]+)\)', formula)
                if match:
                    city = match.group(1)
                    return f"country with capital {city}"
        
        # Bekannte Muster
        patterns = {
            'HauptstadtVon': r'HauptstadtVon\(([^)]+)\)',
            'Bevölkerung': r'Bevölkerung\(([^)]+)\)',
            'WetterIn': r'WetterIn\(([^)]+)\)',
            'WährungVon': r'WährungVon\(([^)]+)\)',
            'FlächeVon': r'FlächeVon\(([^)]+)\)',
            'ZeitzoneVon': r'ZeitzoneVon\(([^)]+)\)',
            'Integral': r'Integral\(([^)]+)\)'
        }
        
        queries = {
            'HauptstadtVon': "capital of {}",
            'Bevölkerung': "population of {}",
            'WetterIn': "weather in {}",
            'WährungVon': "currency of {}",
            'FlächeVon': "area of {}",
            'ZeitzoneVon': "timezone of {}",
            'Integral': "integral of {}"
        }
        
        for pred, pattern in patterns.items():
            if pred in formula:
                match = re.search(pattern, formula)
                if match:
                    arg = match.group(1).lower()
                    # Übersetze deutsche Länder
                    arg = self._translate_german_terms(arg)
                    return queries[pred].format(arg)
        
        # Fallback
        clean_formula = formula.replace('(', ' of ').replace(')', '').replace(',', ' and ')
        clean_formula = re.sub(r'(?<!^)(?=[A-Z])', ' ', clean_formula).lower()
        return self._translate_german_terms(clean_formula)
    
    def _translate_german_terms(self, text: str) -> str:
        """Übersetzt deutsche Begriffe ins Englische."""
        translations = {
            'bevölkerung': 'population',
            'hauptstadt': 'capital',
            'wetter': 'weather',
            'währung': 'currency',
            'fläche': 'area',
            'temperatur': 'temperature',
            'zeitzone': 'timezone',
            'deutschland': 'germany',
            'frankreich': 'france',
            'italien': 'italy',
            'spanien': 'spain',
            'großbritannien': 'united kingdom',
            'england': 'england',
            'österreich': 'austria',
            'schweiz': 'switzerland'
        }
        
        for german, english in translations.items():
            text = text.replace(german, english)
        
        return text
