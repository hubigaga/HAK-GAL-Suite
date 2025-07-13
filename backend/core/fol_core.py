# -*- coding: utf-8 -*-
"""
HAK-GAL Core First-Order Logic Implementation
"""

from typing import List, Tuple, Optional, Dict, Any
import time

from backend.api import BaseProver
from backend.infrastructure import ProofCache


class HAKGAL_Core_FOL:
    """
    Kern-Implementierung für HAK-GAL First-Order Logic.
    Verwaltet die Wissensbasis und führt logische Schlussfolgerungen durch.
    """
    
    def __init__(self):
        """Initialisiert den FOL-Kern mit leerer Wissensbasis."""
        # Wissensbasis als Liste von logischen Formeln
        self.K: List[str] = []
        
        # Prover werden später von außen injiziert
        self.provers: List[BaseProver] = []
        
        # Archon-Prime Komponenten werden später gesetzt
        self.complexity_analyzer = None
        self.portfolio_manager = None
        
        # Statistiken
        self.parser_stats = {"total": 0, "success": 0, "failed": 0}
        
        # Cache für Beweise
        self.proof_cache = ProofCache()
    
    def set_complexity_analyzer(self, analyzer):
        """Setzt den Complexity Analyzer."""
        self.complexity_analyzer = analyzer
    
    def set_portfolio_manager(self, manager):
        """Setzt den Portfolio Manager."""
        self.portfolio_manager = manager
    
    def set_provers(self, provers: List[BaseProver]):
        """
        Setzt die verfügbaren Prover.
        
        Args:
            provers: Liste von Prover-Instanzen
        """
        self.provers = provers
        prover_names = ', '.join([p.name for p in self.provers])
        print(f"--- Prover-Portfolio: {prover_names} ---")
    
    def add_fact(self, formula_str: str) -> bool:
        """
        Fügt einen Fakt zur Wissensbasis hinzu.
        
        Args:
            formula_str: Die hinzuzufügende logische Formel
            
        Returns:
            True wenn erfolgreich hinzugefügt, False wenn bereits vorhanden
        """
        if formula_str not in self.K:
            self.K.append(formula_str)
            self.proof_cache.clear()  # Cache invalidieren
            return True
        return False
    
    def retract_fact(self, fact_to_remove: str) -> bool:
        """
        Entfernt einen Fakt aus der Wissensbasis.
        
        Args:
            fact_to_remove: Die zu entfernende Formel
            
        Returns:
            True wenn erfolgreich entfernt, False wenn nicht gefunden
        """
        if fact_to_remove in self.K:
            self.K.remove(fact_to_remove)
            self.proof_cache.clear()  # Cache invalidieren
            return True
        return False
    
    def check_consistency(self, new_fact: str) -> Tuple[bool, Optional[str]]:
        """
        Prüft ob ein neuer Fakt konsistent mit der Wissensbasis ist.
        
        Args:
            new_fact: Der zu prüfende Fakt
            
        Returns:
            Tuple aus:
            - bool: True wenn konsistent, False wenn inkonsistent
            - Optional[str]: Begründung bei Inkonsistenz
        """
        # 1. Prüfe ob Negation bereits beweisbar ist
        negated_fact = f"-{new_fact}" if not new_fact.startswith('-') else new_fact[1:]
        is_contradictory, reason = self.verify_logical(negated_fact, self.K)
        if is_contradictory:
            return (False, f"Widerspruch! Neuer Fakt '{new_fact}' widerspricht KB ({reason})")
        
        # 2. Teste funktionale Widersprüche direkt
        functional_prover = next((p for p in self.provers if p.name == "Functional Constraint Prover"), None)
        if functional_prover:
            success, reason = functional_prover.prove(self.K, new_fact)
            if success is False:  # Funktionaler Widerspruch erkannt
                return (False, f"Funktionaler Widerspruch! {reason}")
        
        return (True, None)
    
    def verify_logical(self, query_str: str, full_kb: List[str]) -> Tuple[Optional[bool], str]:
        """
        Versucht eine logische Formel aus der Wissensbasis zu beweisen.
        
        Args:
            query_str: Die zu beweisende Formel
            full_kb: Die vollständige Wissensbasis
            
        Returns:
            Tuple aus:
            - Optional[bool]: True wenn bewiesen, False wenn widerlegt, None wenn unbestimmt
            - str: Begründung
        """
        # Cache-Lookup
        cache_key = (tuple(sorted(full_kb)), query_str)
        if cached_result := self.proof_cache.get(query_str, cache_key):
            print("   [Cache] ✅ Treffer im Proof-Cache!")
            return cached_result[0], cached_result[1]
        
        # Wenn Portfolio Manager nicht gesetzt, verwende einfache Reihenfolge
        if self.portfolio_manager:
            # Archon-Prime: Intelligente Prover-Auswahl
            ordered_provers = self.portfolio_manager.select_prover_strategy(query_str, self.provers)
        else:
            # Fallback: Verwende Prover in gegebener Reihenfolge
            ordered_provers = self.provers
        
        # Sequenzielle Ausführung nach Priorität
        for prover in ordered_provers:
            start_time = time.time()
            try:
                success, reason = prover.prove(full_kb, query_str)
                duration = time.time() - start_time
                
                # Performance-Update für Portfolio-Manager (wenn vorhanden)
                if self.portfolio_manager:
                    self.portfolio_manager.update_performance(
                        prover.name, query_str, success is not None, duration
                    )
                
                if success is not None:
                    if success:
                        self.proof_cache.put(query_str, cache_key, success, reason)
                        print(f"   [✅ Erfolg] {prover.name} nach {duration:.2f}s")
                    return success, reason
                else:
                    print(f"   [⏭️ Weiter] {prover.name} nach {duration:.2f}s - {reason}")
                    
            except Exception as e:
                duration = time.time() - start_time
                if self.portfolio_manager:
                    self.portfolio_manager.update_performance(prover.name, query_str, False, duration)
                print(f"   [❌ Fehler] {prover.name}: {e}")
        
        return (None, "Kein Prover konnte eine definitive Antwort finden.")
    
    def update_parser_stats(self, success: bool):
        """
        Aktualisiert Parser-Statistiken.
        
        Args:
            success: Ob das Parsen erfolgreich war
        """
        self.parser_stats["total"] += 1
        if success:
            self.parser_stats["success"] += 1
        else:
            self.parser_stats["failed"] += 1
    
    def get_portfolio_stats(self) -> Dict[str, Any]:
        """
        Gibt Portfolio-Performance-Statistiken zurück.
        
        Returns:
            Dictionary mit Performance-Metriken
        """
        if self.portfolio_manager:
            return self.portfolio_manager.get_performance_report()
        else:
            return {"performance": {}, "usage_count": {}}
