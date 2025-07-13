# -*- coding: utf-8 -*-
"""
K-Assistant - Hauptklasse die alle Komponenten orchestriert
ERWEITERT mit Orchestrator V5 Integration
"""

import re
import os
import sys
import logging
from typing import List, Dict, Any, Optional

from backend.core import HAKGAL_Core_FOL, HAKGALParser
from backend.infrastructure import KnowledgeBasePersistence, ShellManager
from backend.adapters import (
    FunctionalConstraintProver, PatternProver, 
    Z3Adapter, WolframProver
)
from backend.services.ensemble_manager import EnsembleManager
from backend.services.wissensbasis_manager import WissensbasisManager
from backend.services.complexity_analyzer import ComplexityAnalyzer
from backend.services.prover_portfolio_manager import ProverPortfolioManager

# NEW: Advanced Tools Integration
try:
    from backend.services.advanced_integration import bootstrap_advanced_tools
    from backend.services.advanced_relevance_adapter import (
        get_advanced_relevance_manager, 
        LegacyFact, 
        LegacyRelevanceResult
    )
    ADVANCED_TOOLS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Advanced Tools nicht verfügbar: {e}")
    ADVANCED_TOOLS_AVAILABLE = False

logger = logging.getLogger(__name__)

class KAssistant:
    """
    Hauptklasse des K-Assistant Systems.
    Orchestriert alle Komponenten für logisches Schließen und Wissensmanagement.
    ERWEITERT mit Orchestrator V5 Integration für erweiterte Relevance-Filterung.
    """
    
    def __init__(self, kb_filepath: str = "k_assistant.kb", enable_advanced_tools: bool = True):
        """
        Initialisiert den K-Assistant.
        
        Args:
            kb_filepath: Pfad zur Wissensbasis-Datei
            enable_advanced_tools: Aktiviert erweiterte Tools (Orchestrator V5)
        """
        self.kb_filepath = kb_filepath
        self.enable_advanced_tools = enable_advanced_tools and ADVANCED_TOOLS_AVAILABLE
        
        # Core-Komponenten
        self.core = HAKGAL_Core_FOL()
        self.parser = HAKGALParser()
        
        # Service-Komponenten
        self.ensemble_manager = EnsembleManager()
        self.wissensbasis_manager = WissensbasisManager()
        
        # Infrastructure
        self.shell_manager = ShellManager()
        self.persistence = KnowledgeBasePersistence()
        
        # Advanced Tools Integration
        self.advanced_relevance_manager = None
        if self.enable_advanced_tools:
            self._initialize_advanced_tools()
        
        # Temporäre Fakten aus RAG
        self.potential_new_facts: List[str] = []
        
        # Initialisiere Prover
        self._initialize_provers()
        
        # Lade existierende Wissensbasis
        self.load_kb(kb_filepath)
        
        # Füge System-Fakten hinzu
        self._add_system_facts()
        
        # Füge funktionale Constraints hinzu
        self._add_functional_constraints()
        
        print(f"--- Parser-Modus: {'Lark' if self.parser.parser_available else 'Regex-Fallback'} ---")
        if any(isinstance(p, WolframProver) and p.client for p in self.core.provers):
            print("--- Wolfram|Alpha Integration: Aktiv ---")
        
        if self.advanced_relevance_manager:
            stats = self.advanced_relevance_manager.get_stats()
            print(f"--- Advanced Tools: {stats['mode'].title()} Mode ---")
    
    def _initialize_advanced_tools(self):
        """Initialisiert Advanced Tools falls verfügbar"""
        try:
            logger.info("🚀 Initialisiere Advanced Tools...")
            
            # Bootstrap Advanced Tools
            if bootstrap_advanced_tools():
                self.advanced_relevance_manager = get_advanced_relevance_manager()
                logger.info("✅ Advanced Relevance Manager verfügbar")
                
                # Transfer existing facts to advanced manager
                self._transfer_facts_to_advanced_manager()
            else:
                logger.warning("⚠️ Advanced Tools Bootstrap fehlgeschlagen")
                self.enable_advanced_tools = False
                
        except Exception as e:
            logger.error(f"❌ Advanced Tools Initialisierung fehlgeschlagen: {e}")
            self.enable_advanced_tools = False
    
    def _transfer_facts_to_advanced_manager(self):
        """Überträgt bestehende Fakten zum Advanced Manager"""
        if not self.advanced_relevance_manager:
            return
        
        try:
            # Convert core facts to legacy format for transfer
            legacy_facts = []
            for i, fact_str in enumerate(self.core.K):
                # Simple parsing to extract subject, predicate, object
                # This is a basic implementation - could be enhanced
                fact_id = f"core_fact_{i}"
                legacy_fact = LegacyFact(
                    id=fact_id,
                    subject=self._extract_subject(fact_str),
                    predicate=self._extract_predicate(fact_str),
                    object=self._extract_object(fact_str),
                    confidence=1.0,
                    source="core_kb"
                )
                legacy_facts.append(legacy_fact)
            
            if legacy_facts:
                added = self.advanced_relevance_manager.bulk_add_facts(legacy_facts)
                logger.info(f"✅ {added} Fakten zu Advanced Manager übertragen")
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Übertragen der Fakten: {e}")
    
    def _extract_subject(self, fact_str: str) -> str:
        """Extrahiert Subject aus Fakt-String (vereinfacht)"""
        # Basic extraction - can be enhanced with proper parsing
        if '(' in fact_str:
            predicate_part = fact_str.split('(')[1]
            if ',' in predicate_part:
                return predicate_part.split(',')[0].strip()
            elif ')' in predicate_part:
                return predicate_part.split(')')[0].strip()
        return ""
    
    def _extract_predicate(self, fact_str: str) -> str:
        """Extrahiert Predicate aus Fakt-String (vereinfacht)"""
        if '(' in fact_str:
            return fact_str.split('(')[0].strip()
        return fact_str.strip()
    
    def _extract_object(self, fact_str: str) -> str:
        """Extrahiert Object aus Fakt-String (vereinfacht)"""
        if '(' in fact_str and ',' in fact_str:
            parts = fact_str.split('(')[1].split(',')
            if len(parts) >= 2:
                return parts[1].split(')')[0].strip()
        return ""
    
    def _initialize_provers(self):
        """Initialisiert verfügbare Prover."""
        provers = [
            FunctionalConstraintProver(),
            PatternProver(),
            Z3Adapter()
        ]
        
        # Wolfram-Prover hinzufügen wenn verfügbar
        try:
            wolfram_prover = WolframProver()
            if wolfram_prover.client:
                provers.append(wolfram_prover)
                print("✅ WolframProver zum Portfolio hinzugefügt")
        except Exception as e:
            print(f"⚠️ Wolfram-Prover Initialisierung fehlgeschlagen: {e}")
        
        self.core.set_provers(provers)
        
        # Archon-Prime Komponenten initialisieren und setzen
        complexity_analyzer = ComplexityAnalyzer()
        portfolio_manager = ProverPortfolioManager(complexity_analyzer)
        
        self.core.set_complexity_analyzer(complexity_analyzer)
        self.core.set_portfolio_manager(portfolio_manager)
    
    def _add_system_facts(self):
        """Fügt Systemfakten zur Wissensbasis hinzu."""
        system_facts = self.shell_manager.analyze_system_facts()
        added = 0
        for fact in system_facts:
            if fact not in self.core.K:
                self.core.K.append(fact)
                added += 1
        if added > 0:
            print(f"   ✅ {added} Systemfakten hinzugefügt.")
    
    def _add_functional_constraints(self):
        """Fügt funktionale Constraints für eindeutige Relationen hinzu."""
        functional_constraints = [
            # Eine Stadt hat nur EINE Einwohnerzahl
            "all x (all y (all z ((Einwohner(x, y) & Einwohner(x, z)) -> (y = z)))).",
            # Ein Land hat nur EINE Hauptstadt
            "all x (all y (all z ((Hauptstadt(x, y) & Hauptstadt(x, z)) -> (y = z)))).",
            # Eine Stadt liegt nur in EINEM Land
            "all x (all y (all z ((LiegtIn(x, y) & LiegtIn(x, z)) -> (y = z)))).",
            # Ein Objekt hat nur EINE Fläche
            "all x (all y (all z ((Fläche(x, y) & Fläche(x, z)) -> (y = z)))).",
            # Bevölkerung ist auch funktional
            "all x (all y (all z ((Bevölkerung(x, y) & Bevölkerung(x, z)) -> (y = z)))).",
            # Eine Person hat nur EIN Geburtsjahr
            "all x (all y (all z ((Geburtsjahr(x, y) & Geburtsjahr(x, z)) -> (y = z)))).",
            # Eine Stadt hat nur EINE Temperatur (zu einem Zeitpunkt)
            "all x (all y (all z ((Temperatur(x, y) & Temperatur(x, z)) -> (y = z))))."
        ]
        
        added = 0
        for constraint in functional_constraints:
            if constraint not in self.core.K:
                self.core.K.append(constraint)
                added += 1
        
        if added > 0:
            print(f"   ✅ {added} funktionale Constraints hinzugefügt.")
    
    def _normalize_and_correct_syntax(self, formula: str) -> str:
        """
        Normalisiert und korrigiert die Syntax einer Formel.
        
        Args:
            formula: Die zu normalisierende Formel
            
        Returns:
            Normalisierte Formel
        """
        original_formula = formula
        
        # Bindestriche in Entitäten entfernen
        corrected = re.sub(
            r'\b([A-ZÄÖÜ][a-zA-ZÄÖÜ0-9]*)-([a-zA-ZÄÖÜ0-9]+)\b',
            r'\1\2',
            formula
        )
        
        # Synonym-Mapping
        synonym_map = {
            r'IstTechnischesLegacy(System)?': 'IstLegacy',
            r'SollteRefactoringInBetrachtGezo[h|e]genWerden': 'SollteRefactoredWerden',
            r'SollteIdentifiziertUndRefactoredWerden': 'SollteRefactoredWerden',
            r'IstBasierendAufCobolMainframe': 'IstCobolMainframe',
            r'BasiertAufCobolMainframe': 'IstCobolMainframe',
            r'BasiertAufModernerJavaMicroservice': 'IstJavaMicroservice',
            r'IstBasierendAufJavaMicroservice': 'IstJavaMicroservice',
            r'HatGeringeBetriebskosten': 'HatNiedrigeBetriebskosten',
        }
        
        for pattern, canonical in synonym_map.items():
            corrected = re.sub(pattern, canonical, corrected)
        
        # Weitere Normalisierungen
        corrected = corrected.strip().replace(':-', '->').replace('~', '-')
        while corrected.startswith('--'):
            corrected = corrected[2:]
        
        # Fehlende Klammern ergänzen
        if re.match(r"^[A-ZÄÖÜ][a-zA-Z0-9_]*\.$", corrected):
            corrected = corrected.replace('.', '().')
        
        if corrected != original_formula:
            print(f"   [Normalisierung] '{original_formula.strip()}' -> '{corrected.strip()}'")
        
        return corrected
    
    def ask(self, question: str):
        """
        Beantwortet eine natürlichsprachliche Frage.
        ERWEITERT mit Advanced Relevance Manager Integration.
        
        Args:
            question: Die zu beantwortende Frage
        """
        self._ask_or_explain(question, explain=False, is_raw=False)
    
    def explain(self, question: str):
        """
        Erklärt die Antwort auf eine Frage.
        
        Args:
            question: Die zu erklärende Frage
        """
        self._ask_or_explain(question, explain=True, is_raw=False)
    
    def ask_raw(self, formula: str):
        """
        Beantwortet eine Frage in logischer Form.
        
        Args:
            formula: Die logische Formel
        """
        self._ask_or_explain(formula, explain=False, is_raw=True)
    
    def _ask_or_explain(self, q: str, explain: bool, is_raw: bool):
        """Interne Methode für Fragen und Erklärungen - ERWEITERT."""
        print(f"\n> {'Erklärung für' if explain else 'Frage'}{' (roh)' if is_raw else ''}: '{q}'")
        
        self.potential_new_facts = []
        temp_assumptions = []
        
        logical_form = ""
        
        if is_raw:
            logical_form = self._normalize_and_correct_syntax(q)
        else:
            # ENHANCED: Advanced Relevance Search
            if self.advanced_relevance_manager:
                print("🔮 Advanced Relevance Manager: Suche nach relevanten Fakten...")
                try:
                    relevant_results = self.advanced_relevance_manager.query(
                        q, max_results=10, user_id="current_user"
                    )
                    
                    if relevant_results:
                        print(f"   [Advanced] {len(relevant_results)} relevante Fakten gefunden")
                        for result in relevant_results[:5]:  # Top 5
                            fact_str = f"{result.fact.predicate}({result.fact.subject},{result.fact.object})."
                            if fact_str not in temp_assumptions:
                                temp_assumptions.append(fact_str)
                                print(f"   [Advanced] Fakt: {fact_str} (Score: {result.score:.2f})")
                    else:
                        print("   [Advanced] Keine spezifisch relevanten Fakten gefunden")
                        
                except Exception as e:
                    logger.error(f"Advanced Relevance Search fehlgeschlagen: {e}")
            
            # RAG-Pipeline (bestehend)
            if self.wissensbasis_manager.get_statistics()['enabled'] and \
               self.wissensbasis_manager.get_statistics()['chunk_count'] > 0:
                print("🧠 RAG-Pipeline wird für Kontext angereichert...")
                relevant_chunks = self.wissensbasis_manager.retrieve_relevant_chunks(q)
                
                if relevant_chunks:
                    context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
                    print(f"   [RAG] Relevanter Kontext gefunden. Extrahiere Fakten...")
                    extracted_facts = self.ensemble_manager.extract_facts_with_ensemble(context)
                    
                    for fact in extracted_facts:
                        corrected_fact = self._normalize_and_correct_syntax(fact)
                        is_valid, _, _ = self.parser.parse(corrected_fact)
                        if is_valid:
                            temp_assumptions.append(corrected_fact)
                            if corrected_fact not in self.core.K and \
                               corrected_fact not in self.potential_new_facts:
                                self.potential_new_facts.append(corrected_fact)
                    
                    if temp_assumptions:
                        print(f"   [RAG] {len(temp_assumptions)} temporäre Fakten hinzugefügt.")
            
            # LLM-Übersetzung
            print("🔮 Übersetze Anfrage in Logik...")
            logical_form_raw = self.ensemble_manager.logicalize(q)
            
            if not logical_form_raw or not isinstance(logical_form_raw, str) or \
               " " in logical_form_raw.split("(")[0]:
                print(f"   ❌ FEHLER: LLM hat eine ungültige Antwort gegeben.")
                print("   ℹ️ Tipp: Versuchen Sie, die Frage präziser zu formulieren.")
                return
            
            logical_form = self._normalize_and_correct_syntax(logical_form_raw)
        
        print(f"   -> Logische Form: '{logical_form}'")
        
        # Syntax-Validierung
        is_valid, _, msg = self.parser.parse(logical_form)
        self.core.update_parser_stats(is_valid)
        if not is_valid:
            print(f"   ❌ FEHLER: Ungültige Syntax. {msg}")
            return
        
        # Logische Verifikation
        print(f"🧠 Archon-Prime Portfolio-Manager übernimmt...")
        success, reason = self.core.verify_logical(
            logical_form,
            self.core.K + temp_assumptions
        )
        
        # Ergebnis ausgeben
        print("\n--- ERGEBNIS ---")
        if not explain:
            print("✅ Antwort: Ja." if success else "❔ Antwort: Nein/Unbekannt.")
            print(f"   [Begründung] {reason}")
        else:
            success_text = "Ja (bewiesen)" if success else "Nein (nicht bewiesen)"
            if not self.ensemble_manager.providers:
                print("   ❌ Keine Erklärung (keine LLMs).")
                return
            
            print("🗣️  Generiere einfache Erklärung...")
            explanation_prompt = (
                f"Anfrage: '{q}', Ergebnis: {success_text}, "
                f"Grund: '{reason}'. Übersetze dies in eine einfache Erklärung."
            )
            
            explanation = self.ensemble_manager.providers[0].query(
                explanation_prompt,
                "Du bist ein Logik-Experte, der formale Beweise in einfache Sprache übersetzt.",
                0.2
            )
            print(f"--- Erklärung ---\n{explanation}\n-------------------\n")
        
        if self.potential_new_facts:
            print(f"💡 INFO: {len(self.potential_new_facts)} neue Fakten gefunden. "
                  "Benutze 'learn', um sie zu speichern.")
    
    def add_raw(self, formula: str):
        """Fügt eine logische Formel zur Wissensbasis hinzu - ERWEITERT."""
        print(f"\n> Füge KERNREGEL hinzu: '{formula}'")
        normalized_formula = self._normalize_and_correct_syntax(formula)
        
        # Syntax-Prüfung
        is_valid, _, msg = self.parser.parse(normalized_formula)
        self.core.update_parser_stats(is_valid)
        if not is_valid:
            print(f"   ❌ FEHLER: Ungültige Syntax. {msg}")
            return
        
        # Konsistenz-Prüfung
        is_consistent, reason = self.core.check_consistency(normalized_formula)
        if not is_consistent:
            print(f"   🛡️  WARNUNG: {reason}")
            return
        
        if self.core.add_fact(normalized_formula):
            print("   -> Erfolgreich hinzugefügt.")
            
            # ENHANCED: Add to Advanced Manager too
            if self.advanced_relevance_manager:
                try:
                    legacy_fact = LegacyFact(
                        id=f"manual_{len(self.core.K)}",
                        subject=self._extract_subject(normalized_formula),
                        predicate=self._extract_predicate(normalized_formula),
                        object=self._extract_object(normalized_formula),
                        confidence=1.0,
                        source="manual_add"
                    )
                    self.advanced_relevance_manager.add_fact(legacy_fact)
                    print("   -> Auch zu Advanced Manager hinzugefügt.")
                except Exception as e:
                    logger.error(f"Fehler beim Hinzufügen zu Advanced Manager: {e}")
        else:
            print("   -> Fakt bereits vorhanden.")
    
    def retract(self, formula_to_retract: str):
        """Entfernt eine Formel aus der Wissensbasis."""
        print(f"\n> Entferne KERNREGEL: '{formula_to_retract}'")
        normalized_target = self._normalize_and_correct_syntax(formula_to_retract)
        
        if self.core.retract_fact(normalized_target):
            print(f"   -> Fakt '{normalized_target}' entfernt.")
        else:
            print(f"   -> Fakt '{normalized_target}' nicht gefunden.")
    
    def learn_facts(self):
        """Übernimmt gefundene Fakten in die Wissensbasis - ERWEITERT."""
        if not self.potential_new_facts:
            print("🧠 Nichts Neues zu lernen.")
            return
        
        print(f"🧠 Lerne {len(self.potential_new_facts)} neue Fakten...")
        added_count = 0
        skipped_count = 0
        
        # Schnellere Batch-Verarbeitung
        legacy_facts_to_add = []
        
        for i, fact in enumerate(self.potential_new_facts, 1):
            # Fortschrittsanzeige
            if len(self.potential_new_facts) > 5:
                print(f"   Verarbeite Fakt {i}/{len(self.potential_new_facts)}...")
            
            # Prüfe zuerst ob Fakt bereits existiert (schnell)
            if fact in self.core.K:
                skipped_count += 1
                continue
            
            # Vereinfachte Konsistenzprüfung für RAG-Fakten
            # Nur prüfen ob direkte Negation bereits in KB
            negated_fact = f"-{fact}" if not fact.startswith('-') else fact[1:]
            if negated_fact in self.core.K:
                print(f"   ⚠️ Überspringe widersprüchlichen Fakt: {fact}")
                skipped_count += 1
                continue
            
            # Füge Fakt hinzu
            if self.core.add_fact(fact):
                added_count += 1
                
                # ENHANCED: Prepare for Advanced Manager
                if self.advanced_relevance_manager:
                    legacy_fact = LegacyFact(
                        id=f"learned_{added_count}",
                        subject=self._extract_subject(fact),
                        predicate=self._extract_predicate(fact),
                        object=self._extract_object(fact),
                        confidence=0.8,  # Lower confidence for learned facts
                        source="learned"
                    )
                    legacy_facts_to_add.append(legacy_fact)
        
        # ENHANCED: Batch add to Advanced Manager
        if self.advanced_relevance_manager and legacy_facts_to_add:
            try:
                advanced_added = self.advanced_relevance_manager.bulk_add_facts(legacy_facts_to_add)
                print(f"   ✅ {advanced_added} Fakten auch zu Advanced Manager hinzugefügt.")
            except Exception as e:
                logger.error(f"Fehler beim Batch-Add zu Advanced Manager: {e}")
        
        # Ergebnis ausgeben
        if added_count > 0:
            print(f"✅ {added_count} neue Fakten gespeichert.")
        if skipped_count > 0:
            print(f"ℹ️ {skipped_count} Fakten übersprungen (bereits bekannt oder widersprüchlich).")
        if added_count == 0 and skipped_count == 0:
            print("ℹ️ Keine neuen Fakten hinzugefügt.")
        
        # Liste leeren
        self.potential_new_facts = []
    
    def clear_cache(self):
        """Leert alle Caches - ERWEITERT."""
        self.core.proof_cache.clear()
        self.ensemble_manager.prompt_cache.clear()
        
        # Wolfram-Cache leeren wenn verfügbar
        for prover in self.core.provers:
            if hasattr(prover, 'clear_cache'):
                prover.clear_cache()
        
        # ENHANCED: Clear Advanced Manager Cache
        if self.advanced_relevance_manager:
            self.advanced_relevance_manager.clear_cache()
            print("   ✅ Advanced Tools Cache geleert.")
    
    def status(self):
        """Zeigt den System-Status an - ERWEITERT."""
        print(f"\n--- System Status ---")
        
        # Parser-Statistiken
        stats = self.core.parser_stats
        success_rate = (stats["success"] / stats["total"] * 100) \
                      if stats["total"] > 0 else 0
        
        # Cache-Statistiken
        pc = self.core.proof_cache
        pmc = self.ensemble_manager.prompt_cache
        
        print(f"  Parser: {'Lark' if self.parser.parser_available else 'Regex'} | "
              f"Versuche: {stats['total']} | Erfolg: {success_rate:.1f}%")
        print(f"  Wissen: {len(self.core.K)} Kernfakten | "
              f"{len(self.potential_new_facts)} lernbare Fakten")
        print(f"  Caches: Beweise={pc.size} (Rate {pc.hit_rate:.1f}%) | "
              f"Prompts={pmc.size} (Rate {pmc.hit_rate:.1f}%)")
        
        # ENHANCED: Advanced Tools Status
        if self.advanced_relevance_manager:
            advanced_stats = self.advanced_relevance_manager.get_stats()
            print(f"  Advanced: {advanced_stats['mode'].title()} Mode | "
                  f"Orchestrator: {'✅' if advanced_stats['orchestrator_available'] else '❌'}")
            if 'total_queries' in advanced_stats:
                print(f"    Queries: {advanced_stats.get('total_queries', 0)} | "
                      f"Cache Hit Rate: {advanced_stats.get('cache_hit_rate', 0):.1%}")
        
        # RAG-Statistiken
        rag_stats = self.wissensbasis_manager.get_statistics()
        if rag_stats['enabled']:
            print(f"  RAG: {rag_stats['chunk_count']} Chunks aus "
                  f"{rag_stats['doc_count']} Docs")
        
        # Portfolio-Performance
        portfolio_stats = self.core.get_portfolio_stats()
        if portfolio_stats["performance"]:
            print(f"\n--- Portfolio Performance ---")
            for prover_name, perf in portfolio_stats["performance"].items():
                usage = portfolio_stats["usage_count"].get(prover_name, 0)
                print(f"  {prover_name}: {perf['success_rate']:.1%} Erfolg, "
                      f"{perf['avg_duration']:.2f}s ⌀, {usage}x verwendet")
    
    def show(self) -> Dict[str, Any]:
        """Gibt die Wissensbasis zurück - ERWEITERT."""
        permanent_knowledge = sorted(self.core.K)
        learnable_facts = sorted(self.potential_new_facts)
        
        rag_chunks_summary = []
        if self.wissensbasis_manager.chunks:
            for i, chunk_info in enumerate(self.wissensbasis_manager.chunks[:5]):
                rag_chunks_summary.append({
                    "id": i,
                    "source": chunk_info.get('source', 'Unbekannt'),
                    "text_preview": chunk_info.get('text', '')[:80] + "..."
                })
        
        result = {
            "permanent_knowledge": permanent_knowledge,
            "learnable_facts": learnable_facts,
            "rag_chunks": rag_chunks_summary,
            "rag_stats": self.wissensbasis_manager.get_statistics(),
            "portfolio_stats": self.core.get_portfolio_stats()
        }
        
        # ENHANCED: Add Advanced Tools Info
        if self.advanced_relevance_manager:
            result["advanced_tools"] = self.advanced_relevance_manager.get_stats()
        
        return result
    
    def save_kb(self, filepath: str):
        """Speichert die Wissensbasis - ERWEITERT."""
        rag_data = {
            'chunks': self.wissensbasis_manager.chunks,
            'doc_paths': self.wissensbasis_manager.doc_paths
        } if self.wissensbasis_manager.get_statistics()['enabled'] else {}
        
        data = {
            'facts': self.core.K,
            'rag_data': rag_data,
            'parser_stats': self.core.parser_stats,
            'proof_cache': dict(self.core.proof_cache.cache),
            'portfolio_stats': self.core.get_portfolio_stats(),
            'advanced_tools_enabled': self.enable_advanced_tools  # NEW
        }
        
        # ENHANCED: Save Advanced Tools Stats
        if self.advanced_relevance_manager:
            data['advanced_tools_stats'] = self.advanced_relevance_manager.get_stats()
        
        self.persistence.save(filepath, data)
    
    def load_kb(self, filepath: str):
        """Lädt die Wissensbasis - ERWEITERT."""
        data = self.persistence.load(filepath)
        
        if not data:
            return
        
        # Lade Kernfakten
        self.core.K = data.get('facts', [])
        self.core.parser_stats = data.get('parser_stats', {
            "total": 0, "success": 0, "failed": 0
        })
        self.core.proof_cache.cache = data.get('proof_cache', {})
        
        # Portfolio-Daten
        if 'portfolio_stats' in data:
            portfolio_data = data['portfolio_stats']
            if 'performance' in portfolio_data:
                self.core.portfolio_manager.prover_performance = portfolio_data['performance']
            if 'usage_count' in portfolio_data:
                self.core.portfolio_manager.prover_usage_count = portfolio_data['usage_count']
            print(f"✅ Portfolio-Performance geladen")
        
        # ENHANCED: Load Advanced Tools preference
        if 'advanced_tools_enabled' in data:
            self.enable_advanced_tools = data['advanced_tools_enabled'] and ADVANCED_TOOLS_AVAILABLE
            if self.enable_advanced_tools and not self.advanced_relevance_manager:
                self._initialize_advanced_tools()
        
        # RAG-Daten
        if self.wissensbasis_manager.get_statistics()['enabled'] and \
           'rag_data' in data and data['rag_data']:
            
            # Migriere alte Formate
            data = self.persistence.migrate_old_format(data)
            
            self.wissensbasis_manager.chunks = data['rag_data'].get('chunks', [])
            self.wissensbasis_manager.doc_paths = data['rag_data'].get('doc_paths', {})
            
            # Baue Index neu auf
            if self.wissensbasis_manager.chunks:
                self.wissensbasis_manager.rebuild_index_from_chunks(
                    self.wissensbasis_manager.chunks
                )
    
    # NEW: Advanced Tools Control Methods
    def enable_advanced_features(self) -> bool:
        """Aktiviert erweiterte Features des Advanced Relevance Managers"""
        if not self.advanced_relevance_manager:
            print("❌ Advanced Relevance Manager nicht verfügbar")
            return False
        
        try:
            success = self.advanced_relevance_manager.enable_advanced_features()
            if success:
                print("✅ Erweiterte Features aktiviert (Semantic + ML + Learning)")
            else:
                print("⚠️ Erweiterte Features konnten nicht vollständig aktiviert werden")
            return success
        except Exception as e:
            print(f"❌ Fehler beim Aktivieren erweiterter Features: {e}")
            return False
    
    def advanced_tools_status(self):
        """Zeigt detaillierten Status der Advanced Tools"""
        if not self.advanced_relevance_manager:
            print("❌ Advanced Tools nicht verfügbar")
            return
        
        stats = self.advanced_relevance_manager.get_stats()
        print(f"\n--- Advanced Tools Status ---")
        print(f"  Mode: {stats['mode'].title()}")
        print(f"  Orchestrator: {'Verfügbar' if stats['orchestrator_available'] else 'Nicht verfügbar'}")
        print(f"  Total Facts: {stats.get('total_facts', 0)}")
        
        if 'available_filters' in stats:
            print(f"  Verfügbare Filter: {', '.join(stats['available_filters'])}")
        if 'total_queries' in stats:
            print(f"  Queries: {stats['total_queries']}")
            print(f"  Cache Hit Rate: {stats.get('cache_hit_rate', 0):.1%}")
        if 'strategy_usage' in stats:
            print(f"  Strategie-Nutzung: {stats['strategy_usage']}")
    
    # Bestehende Methoden bleiben unverändert...
    def what_is(self, entity: str):
        """Analysiert eine Entität."""
        normalized_entity = self._normalize_and_correct_syntax(entity)\
            .replace('.', '').replace('(', '').replace(')', '')
        
        print(f"\n> Analysiere Wissen über Entität: '{normalized_entity}'")
        
        # Explizite Fakten
        explicit_facts = [
            fact for fact in self.core.K
            if f"({normalized_entity})" in fact or
               f",{normalized_entity})" in fact or
               f"({normalized_entity}," in fact
        ]
        
        # Abgeleitete Eigenschaften
        unary_predicates = [
            "IstLegacy", "IstKritisch", "IstOnline", "IstStabil",
            "HatHoheBetriebskosten", "SollteRefactoredWerden", "MussÜberwacht"
        ]
        
        derived_properties = []
        print("🧠 Leite Eigenschaften ab...")
        
        for pred in unary_predicates:
            positive_goal = f"{pred}({normalized_entity})."
            is_positive, _ = self.core.verify_logical(positive_goal, self.core.K)
            if is_positive and positive_goal not in explicit_facts:
                derived_properties.append(positive_goal)
                continue
            
            negative_goal = f"-{pred}({normalized_entity})."
            is_negative, _ = self.core.verify_logical(negative_goal, self.core.K)
            if is_negative and negative_goal not in explicit_facts:
                derived_properties.append(negative_goal)
        
        # Ausgabe
        print("\n" + f"--- Profil für: {normalized_entity} ---".center(60, "-"))
        print("\n  [Explizite Fakten]")
        if explicit_facts:
            for f in sorted(explicit_facts):
                print(f"   - {f}")
        else:
            print("   (Keine)")
        
        print("\n  [Abgeleitete Eigenschaften]")
        if derived_properties:
            for p in sorted(derived_properties):
                print(f"   - {p}")
        else:
            print("   (Keine)")
        print("-" * 60)
    
    # Zusätzliche Methoden bleiben unverändert...
    def build_kb_from_file(self, filepath: str):
        """Fügt ein Dokument zur RAG-Wissensbasis hinzu."""
        self.wissensbasis_manager.add_document(filepath)
    
    def search(self, query: str):
        """Sucht in der RAG-Wissensbasis."""
        if not self.wissensbasis_manager.get_statistics()['enabled']:
            print("   ❌ RAG-Funktionen sind deaktiviert.")
            return
        
        print(f"\n> Suche Kontext für: '{query}'")
        chunks = self.wissensbasis_manager.retrieve_relevant_chunks(query)
        
        if not chunks:
            print("   [RAG] Keine relevanten Informationen gefunden.")
            return
        
        print(f"   [RAG] Relevanter Kontext:\n---")
        for i, chunk in enumerate(chunks, 1):
            print(f"[{i} from {chunk['source']}] {chunk['text']}\n")
    
    def sources(self):
        """Zeigt indizierte Wissensquellen."""
        if not self.wissensbasis_manager.get_statistics()['enabled']:
            print("   ❌ RAG-Funktionen sind deaktiviert.")
            return
        
        print("\n📑 Indizierte Wissensquellen:")
        docs = self.wissensbasis_manager.get_indexed_documents()
        
        if not docs:
            print("   (Keine)")
        else:
            for doc_id, path in docs.items():
                print(f"   - {doc_id} (aus {path})")
    
    def execute_shell(self, command: str):
        """Führt einen Shell-Befehl aus."""
        success, stdout, stderr = self.shell_manager.execute(command)
        if success:
            print(f"✅ Befehl erfolgreich:\n{stdout}")
        else:
            print(f"❌ Befehl fehlgeschlagen:\n{stderr}")
    
    def test_parser(self, formula: str):
        """Testet den Parser mit einer Formel."""
        print(f"\n> Parser-Test für: '{formula}'")
        normalized_formula = self._normalize_and_correct_syntax(formula)
        success, tree, msg = self.parser.parse(normalized_formula)
        self.core.update_parser_stats(success)
        
        if success:
            print(f"✅ Parse erfolgreich: {msg}")
            if tree:
                predicates = self.parser.extract_predicates(tree)
                if predicates:
                    print(f"   Gefundene Prädikate: {', '.join(predicates)}")
        else:
            print(f"❌ Parse fehlgeschlagen: {msg}")
    
    # Wolfram-spezifische Methoden bleiben unverändert...
    def add_oracle_predicate(self, predicate: str):
        """Fügt ein Oracle-Prädikat hinzu."""
        if self.core.complexity_analyzer:
            self.core.complexity_analyzer.oracle_predicates.add(predicate)
            print(f"✅ Oracle-Prädikat '{predicate}' hinzugefügt")
        else:
            print("❌ ComplexityAnalyzer nicht initialisiert")
    
    def test_wolfram(self, query: str = "HauptstadtVon(Deutschland)."):
        """Testet die Wolfram-Integration."""
        wolfram_prover = next(
            (p for p in self.core.provers if p.name == "Wolfram|Alpha Orakel"),
            None
        )
        
        if not wolfram_prover:
            print("❌ Wolfram-Prover nicht im Portfolio gefunden")
            return
        
        if not hasattr(wolfram_prover, 'client') or not wolfram_prover.client:
            print("❌ Wolfram-Client nicht konfiguriert")
            return
        
        print(f"🧪 Teste Wolfram mit: {query}")
        try:
            success, reason = wolfram_prover.prove([], query)
            if success is True:
                print(f"✅ Wolfram-Test erfolgreich: {reason}")
            elif success is False:
                print(f"❌ Wolfram-Test negativ: {reason}")
            else:
                print(f"⚠️ Wolfram-Test unbestimmt: {reason}")
        except Exception as e:
            print(f"❌ Wolfram-Test fehlgeschlagen: {e}")
    
    def wolfram_stats(self):
        """Zeigt Wolfram-Statistiken."""
        wolfram_prover = next(
            (p for p in self.core.provers if p.name == "Wolfram|Alpha Orakel"),
            None
        )
        
        if wolfram_prover and hasattr(wolfram_prover, 'client') and wolfram_prover.client:
            print(f"\n--- Wolfram|Alpha Statistiken ---")
            print(f"  Client: Aktiv")
            print(f"  Cache-Einträge: {len(getattr(wolfram_prover, 'cache', {}))}")
            print(f"  Cache-Timeout: {getattr(wolfram_prover, 'cache_timeout', 3600)}s")
            print(f"  App ID: Konfiguriert")
        else:
            print("⚠️ Wolfram|Alpha nicht verfügbar oder nicht konfiguriert")
            print("   Lösungsvorschläge:")
            print("   1. Wolfram App ID in .env konfigurieren")
            print("   2. 'pip install wolframalpha' ausführen")
            print("   3. Backend neu starten")
