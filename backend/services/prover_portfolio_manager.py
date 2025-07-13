# -*- coding: utf-8 -*-
"""
Prover Portfolio Manager - Intelligente Prover-Auswahl
"""

from typing import List, Dict, Any

from backend.api import BaseProver
from backend.services.complexity_analyzer import ComplexityAnalyzer


class ProverPortfolioManager:
    """
    Intelligenter Manager für Prover-Auswahl basierend auf Komplexitätsanalyse.
    Implementiert Multi-Armed Bandit-ähnliche Strategien.
    """
    
    def __init__(self, complexity_analyzer: ComplexityAnalyzer):
        """
        Initialisiert den Manager mit einem Complexity Analyzer.
        
        Args:
            complexity_analyzer: Instanz des Complexity Analyzers
        """
        self.complexity_analyzer = complexity_analyzer
        self.prover_performance: Dict[str, Dict[str, float]] = {}
        self.prover_usage_count: Dict[str, int] = {}
    
    def select_prover_strategy(self, formula: str, available_provers: List[BaseProver]) -> List[BaseProver]:
        """
        Wählt optimale Prover-Reihenfolge basierend auf Komplexitätsanalyse.
        
        Args:
            formula: Zu analysierende Formel
            available_provers: Verfügbare Prover
            
        Returns:
            Geordnete Liste der Prover nach Priorität
        """
        # Komplexitätsanalyse durchführen
        report = self.complexity_analyzer.analyze(formula)
        
        print(f"   [Portfolio] Analyse: {report.reasoning}")
        print(f"   [Portfolio] Empfohlene Prover: {', '.join(report.recommended_provers)}")
        
        # Prover nach Empfehlung sortieren
        prover_by_name = {p.name: p for p in available_provers}
        ordered_provers = []
        
        # Zuerst empfohlene Prover in der empfohlenen Reihenfolge
        for recommended_name in report.recommended_provers:
            if recommended_name in prover_by_name:
                ordered_provers.append(prover_by_name[recommended_name])
        
        # Dann restliche Prover
        for prover in available_provers:
            if prover not in ordered_provers:
                ordered_provers.append(prover)
        
        return ordered_provers
    
    def update_performance(self, prover_name: str, formula: str, success: bool, duration: float):
        """
        Aktualisiert Performance-Metriken für adaptive Optimierung.
        
        Args:
            prover_name: Name des Provers
            formula: Verwendete Formel
            success: Erfolg des Beweises
            duration: Ausführungszeit
        """
        if prover_name not in self.prover_performance:
            self.prover_performance[prover_name] = {
                "success_rate": 0.0,
                "avg_duration": 0.0
            }
        
        if prover_name not in self.prover_usage_count:
            self.prover_usage_count[prover_name] = 0
        
        # Einfache gleitende Durchschnitte
        current_count = self.prover_usage_count[prover_name]
        current_success_rate = self.prover_performance[prover_name]["success_rate"]
        current_avg_duration = self.prover_performance[prover_name]["avg_duration"]
        
        # Update success rate
        new_success_rate = (current_success_rate * current_count + (1.0 if success else 0.0)) / (current_count + 1)
        
        # Update average duration
        new_avg_duration = (current_avg_duration * current_count + duration) / (current_count + 1)
        
        self.prover_performance[prover_name]["success_rate"] = new_success_rate
        self.prover_performance[prover_name]["avg_duration"] = new_avg_duration
        self.prover_usage_count[prover_name] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Gibt Performance-Bericht zurück.
        
        Returns:
            Dictionary mit Performance-Metriken und Nutzungsstatistiken
        """
        return {
            "performance": self.prover_performance.copy(),
            "usage_count": self.prover_usage_count.copy()
        }
