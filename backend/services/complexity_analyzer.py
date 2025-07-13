# -*- coding: utf-8 -*-
"""
Complexity Analyzer - Analysiert Komplexität von Anfragen
"""

import re
from typing import List

from backend.core import QueryType, ComplexityLevel, ComplexityReport
from backend.adapters import WolframProver


class ComplexityAnalyzer:
    """
    Erweiterte Komplexitätsanalyse für intelligente Oracle-Erkennung.
    Implementiert Pattern-basierte Erkennung für Wolfram-geeignete Queries.
    """
    
    def __init__(self):
        """Initialisiert den Analyzer mit bekannten Mustern."""
        # Oracle-Prädikate: Bekannte Wissensprädikate für externe Abfragen
        self.oracle_predicates = {
            "Bevölkerungsdichte", "HauptstadtVon", "WetterIn", "TemperaturIn",
            "Integral", "AbleitungVon", "WährungVon", "FlächeVon", "Bevölkerung",
            "ZeitzoneVon", "AktuelleZeit", "Umrechnung", "Einheit", "Lösung",
            "Faktorisierung", "IstGroesserAls", "IstKleinerAls",
            "Einwohner", "Hauptstadt"
        }
        
        # Pattern für Oracle-Erkennung via Regex
        self.oracle_patterns = [
            r'.*[Vv]on$',           # Endet mit "Von"
            r'.*[Ii]n$',            # Endet mit "In"
            r'Berechne.*',          # Startet mit "Berechne"
            r'.*temperatur.*',      # Enthält Temperatur
            r'.*wetter.*',          # Enthält Wetter
            r'.*hauptstadt.*',      # Enthält Hauptstadt
            r'.*währung.*',         # Enthält Währung
            r'.*bevölkerung.*',     # Enthält Bevölkerung
        ]
        
        # Komplexitätsmuster
        self.high_complexity_patterns = [
            r'all\s+\w+',          # Quantifizierte Formeln
            r'->\s*all',           # Verschachtelte Implikationen
            r'&.*&.*&',            # Mehrfache Konjunktionen
        ]
        
        self.mathematical_patterns = [
            r'[Ii]ntegral',        # Integration
            r'[Aa]bleitung',       # Differentiation
            r'[Ll]ösung',          # Gleichungslösung
            r'[Ff]aktor',          # Faktorisierung
            r'[Gg]renze',          # Grenzwerte
        ]
    
    def analyze(self, formula: str) -> ComplexityReport:
        """
        Hauptanalyse-Methode für Formeln.
        
        Args:
            formula: HAK-GAL Formel zur Analyse
            
        Returns:
            ComplexityReport mit detaillierter Analyse
        """
        # Prädikat extrahieren
        predicate_match = re.match(r'([A-ZÄÖÜ][a-zA-ZÄÖÜäöüß0-9_]*)', formula.strip())
        predicate = predicate_match.group(1) if predicate_match else ""
        
        # Oracle-Bedarf analysieren
        requires_oracle = self._requires_oracle_analysis(predicate, formula)
        
        # Query-Typ bestimmen
        query_type = self._determine_query_type(predicate, formula)
        
        # Komplexität schätzen
        complexity_level = self._estimate_complexity(formula)
        
        # Zeitschätzung
        estimated_time = self._estimate_time(complexity_level, requires_oracle)
        
        # Empfohlene Prover
        recommended_provers = self._recommend_provers(query_type, complexity_level, requires_oracle)
        
        # Konfidenz und Reasoning
        confidence = self._calculate_confidence(predicate, formula)
        reasoning = self._generate_reasoning(predicate, requires_oracle, query_type, complexity_level)
        
        return ComplexityReport(
            query_type=query_type,
            complexity_level=complexity_level,
            requires_oracle=requires_oracle,
            estimated_time=estimated_time,
            confidence=confidence,
            reasoning=reasoning,
            recommended_provers=recommended_provers
        )
    
    def _requires_oracle_analysis(self, predicate: str, formula: str) -> bool:
        """Analysiert, ob ein Oracle (Wolfram) benötigt wird."""
        # 1. Bekannte Oracle-Prädikate
        if predicate in self.oracle_predicates:
            return True
        
        # 2. Pattern-basierte Erkennung
        if any(re.match(pattern, predicate, re.IGNORECASE) for pattern in self.oracle_patterns):
            return True
        
        # 3. Einheiten und Maßangaben erkennen
        if re.search(r'\d+.*(?:km|kg|€|\$|°C|°F|%|meter|grad)', formula, re.IGNORECASE):
            return True
        
        # 4. Mathematische Ausdrücke
        if any(re.search(pattern, formula, re.IGNORECASE) for pattern in self.mathematical_patterns):
            return True
        
        return False
    
    def _determine_query_type(self, predicate: str, formula: str) -> QueryType:
        """Bestimmt den Typ der Anfrage."""
        if any(re.search(pattern, formula, re.IGNORECASE) for pattern in self.mathematical_patterns):
            return QueryType.MATHEMATICAL
        
        if self._requires_oracle_analysis(predicate, formula):
            return QueryType.KNOWLEDGE
        
        if any(op in formula for op in ['->', '&', '|', 'all ']):
            return QueryType.LOGIC
        
        return QueryType.MIXED
    
    def _estimate_complexity(self, formula: str) -> ComplexityLevel:
        """Schätzt die Komplexität der Formel."""
        # Hohe Komplexität
        if any(re.search(pattern, formula) for pattern in self.high_complexity_patterns):
            return ComplexityLevel.HIGH
        
        # Mittlere Komplexität
        if len(re.findall(r'[&|]|->|-', formula)) > 1:
            return ComplexityLevel.MEDIUM
        
        # Niedrige Komplexität für einfache atomare Formeln
        if re.match(r'^[A-ZÄÖÜ][a-zA-ZÄÖÜäöüß0-9_]*\([^)]*\)\.$', formula):
            return ComplexityLevel.LOW
        
        return ComplexityLevel.UNKNOWN
    
    def _estimate_time(self, complexity: ComplexityLevel, requires_oracle: bool) -> float:
        """Schätzt die Ausführungszeit in Sekunden."""
        base_time = {
            ComplexityLevel.LOW: 0.1,
            ComplexityLevel.MEDIUM: 0.5,
            ComplexityLevel.HIGH: 2.0,
            ComplexityLevel.UNKNOWN: 1.0
        }
        
        time_estimate = base_time[complexity]
        
        # Oracle-Anfragen dauern länger
        if requires_oracle:
            time_estimate += 1.5
        
        return time_estimate
    
    def _recommend_provers(self, query_type: QueryType, complexity: ComplexityLevel, 
                          requires_oracle: bool) -> List[str]:
        """Empfiehlt geeignete Prover für die Anfrage."""
        recommended = []
        
        # Oracle-Anfragen -> Wolfram zuerst
        if requires_oracle:
            # Prüfe ob Wolfram verfügbar ist
            try:
                wolfram = WolframProver()
                if wolfram.client:
                    recommended.append("Wolfram|Alpha Orakel")
            except:
                pass
        
        # Funktionale Constraints -> Spezialisierter Prover zuerst
        recommended.append("Functional Constraint Prover")
        
        # Logische Anfragen -> Z3
        if query_type in [QueryType.LOGIC, QueryType.MIXED]:
            recommended.append("Z3 SMT Solver")
        
        # Pattern Matcher als Fallback
        recommended.append("Pattern Matcher")
        
        return recommended
    
    def _calculate_confidence(self, predicate: str, formula: str) -> float:
        """Berechnet Konfidenz der Analyse (0.0 - 1.0)."""
        confidence = 0.5  # Basis-Konfidenz
        
        # Bekannte Prädikate erhöhen Konfidenz
        if predicate in self.oracle_predicates:
            confidence += 0.3
        
        # Klare Muster erhöhen Konfidenz
        if any(re.match(pattern, predicate, re.IGNORECASE) for pattern in self.oracle_patterns):
            confidence += 0.2
        
        # Einfache Strukturen sind sicherer
        if re.match(r'^[A-ZÄÖÜ][a-zA-ZÄÖÜäöüß0-9_]*\([^)]*\)\.$', formula):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, predicate: str, requires_oracle: bool, 
                          query_type: QueryType, complexity: ComplexityLevel) -> str:
        """Generiert Begründung für die Analyse."""
        reasons = []
        
        if requires_oracle:
            if predicate in self.oracle_predicates:
                reasons.append(f"'{predicate}' ist bekanntes Wissensprädikat")
            else:
                reasons.append("Pattern deutet auf Wissensabfrage hin")
        
        reasons.append(f"Query-Typ: {query_type.value}")
        reasons.append(f"Komplexität: {complexity.value}")
        
        return "; ".join(reasons)
