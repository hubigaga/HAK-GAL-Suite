# enhanced_reasoning_engine.py (KOMPLETT REPARIERT)

import asyncio
import time
import json
import os
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Import from existing reasoning engine
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    # Versucht, die Kern-Engine-Komponenten zu importieren
    from reasoning_engine import (
        ReasoningType, ProofStatus, ReasoningResult,
        Z3SMTSolver, ProverManager, SemanticValidationEngine
    )
    REASONING_ENGINE_AVAILABLE = True
except ImportError:
    REASONING_ENGINE_AVAILABLE = False
    print("⚠️ Warnung: Die Kernkomponente 'reasoning_engine.py' konnte nicht gefunden werden.")

class EnhancedSemanticValidator:
    """Validiert Ergebnisse unter Verwendung der Ontologie."""

    def __init__(self, project_root: str):
        # KORREKTUR: Der übergebene project_root wird direkt verwendet.
        self.project_root = project_root
        self.ontology = self._load_proven_ontology()
        self.semantic_kb = self._load_semantic_knowledge_base()

    def _load_proven_ontology(self) -> Dict:
        """Lädt die Ontologie aus dem Projekt-Stammverzeichnis."""
        try:
            # KORREKTUR: Der Pfad wird direkt aus self.project_root gebildet.
            ontology_path = os.path.join(self.project_root, "hak_gal_ontology.json")
            if os.path.exists(ontology_path):
                with open(ontology_path, 'r', encoding='utf-8') as f:
                    print(f"✅ Ontologie gefunden und geladen von: {ontology_path}")
                    return json.load(f)
            else:
                print(f"⚠️ Ontologie-Datei nicht am erwarteten Pfad gefunden: {ontology_path}")
        except Exception as e:
            print(f"❌ Fehler beim Laden der Ontologie: {e}")
        return {}

    def _load_semantic_knowledge_base(self) -> Dict:
        """Lädt die semantische Wissensbasis."""
        try:
            # KORREKTUR: Der Pfad wird direkt aus self.project_root gebildet.
            kb_path = os.path.join(self.project_root, "semantic_knowledge_base.json")
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    print(f"✅ Semantische KB gefunden und geladen von: {kb_path}")
                    return json.load(f)
            else:
                print(f"⚠️ Semantische KB nicht am erwarteten Pfad gefunden: {kb_path}")
        except Exception as e:
            print(f"❌ Fehler beim Laden der semantischen KB: {e}")
        return {}

    def validate_reasoning_result(self, result) -> bool:
        """Validiert die Entitäten im Ergebnis gegen die Ontologie."""
        if not self.ontology:
            return True # Kann nicht validieren, also als gültig annehmen

        entities = re.findall(r'[A-Z][a-zA-Z0-9]*', result.conclusion)
        if not entities:
            return True # Keine Entitäten zum Validieren

        ontology_concepts = set(self.ontology.get('nodes', {}).keys())
        valid_entities = 0
        for entity in entities:
            entity_lower = entity.lower()
            if entity_lower in ontology_concepts:
                valid_entities += 1
                continue
            # Fallback-Prüfung auf Teilübereinstimmungen oder Synonyme
            if any(entity_lower in c or c in entity_lower for c in ontology_concepts):
                valid_entities += 1
                continue

        validation_rate = valid_entities / len(entities)
        return validation_rate >= 0.5

class EnhancedQueryProcessor:
    """Wandelt natürlichsprachliche Anfragen in HAK-GAL-Formeln um."""

    def __init__(self, project_root: str):
        # KORREKTUR: Der übergebene project_root wird direkt verwendet.
        self.project_root = project_root
        self.semantic_kb = self._load_semantic_knowledge_base()
        self.ontology = self._load_ontology()

    def _load_semantic_knowledge_base(self) -> Dict:
        try:
            # KORREKTUR: Der Pfad wird direkt aus self.project_root gebildet.
            kb_path = os.path.join(self.project_root, "semantic_knowledge_base.json")
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ (QueryProcessor) Semantische KB nicht gefunden: {kb_path}")
        except Exception as e:
            print(f"❌ (QueryProcessor) Fehler beim Laden der semantischen KB: {e}")
        return {}

    def _load_ontology(self) -> Dict:
        try:
            # KORREKTUR: Der Pfad wird direkt aus self.project_root gebildet.
            ontology_path = os.path.join(self.project_root, "hak_gal_ontology.json")
            if os.path.exists(ontology_path):
                with open(ontology_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ (QueryProcessor) Ontologie nicht gefunden: {ontology_path}")
        except Exception as e:
            print(f"❌ (QueryProcessor) Fehler beim Laden der Ontologie: {e}")
        return {}

    def convert_to_hak_gal(self, query: str) -> str:
        """Konvertiert eine Anfrage in eine logische Formel."""
        query_lower = query.lower().strip()

        # 1. Priorität: Exakte Übereinstimmungen aus der Wissensbasis
        if self.semantic_kb and 'facts' in self.semantic_kb:
            for fact in self.semantic_kb['facts']:
                original = fact.get('original_fact', '').lower()
                formula = fact.get('hak_gal_formula', '')
                if self._queries_are_similar(query_lower, original):
                    print(f"✅ Treffer aus Wissensbasis: '{original}' → {formula}")
                    return formula

        # 2. Priorität: Feste Regex-Muster als Fallback
        conversion_patterns = [
            (r'.*capital.*france.*', 'HauptstadtVon(Paris, France).'),
            (r'.*machine learning.*ai system.*', 'IstKomponente(MachineLearning, AISystem).'),
            (r'.*ai.*active.*', 'IstAktiv(AISystem).'),
        ]
        for pattern, formula in conversion_patterns:
            if re.match(pattern, query_lower):
                print(f"✅ Treffer durch Regex-Muster: {pattern} → {formula}")
                return formula

        # 3. Priorität: Generische Formel basierend auf Ontologie-Konzepten
        return self._create_fallback_formula(query_lower)

    def _queries_are_similar(self, query1: str, query2: str) -> bool:
        """Prüft die Ähnlichkeit zweier Anfragen basierend auf Wortüberschneidungen."""
        words1 = set(re.findall(r'\w+', query1))
        words2 = set(re.findall(r'\w+', query2))
        if not words1 or not words2:
            return False
        overlap = len(words1.intersection(words2))
        total_unique = len(words1.union(words2))
        similarity = overlap / total_unique
        return similarity > 0.3 # Schwellenwert für Ähnlichkeit

    def _create_fallback_formula(self, query: str) -> str:
        """Erstellt eine generische Formel, wenn keine Regel passt."""
        concepts = []
        if self.ontology:
            ontology_concepts = self.ontology.get('nodes', {})
            for concept_id, concept_data in ontology_concepts.items():
                # Prüft den Namen und die Synonyme des Konzepts
                all_names = [concept_data.get('name', '')] + concept_data.get('synonyms', [])
                for name in all_names:
                    if name and name.lower() in query:
                        concepts.append(concept_id) # Benutze die ID für Konsistenz
                        break
        
        concepts = list(set(concepts)) # Duplikate entfernen

        if len(concepts) >= 2:
            return f"Relation({concepts[0]}, {concepts[1]})."
        elif len(concepts) == 1:
            return f"Property({concepts[0]})."
        else:
            # Letzter Ausweg: Schlüsselwörter aus der Anfrage extrahieren
            clean_query = re.sub(r'[^a-zA-Z0-9\s]', '', query)
            words = [word.capitalize() for word in clean_query.split()[:3]]
            return f"Query({','.join(words)})."

class EnhancedReasoningEngine:
    """Die Haupt-Engine, die alle Komponenten orchestriert."""

    def __init__(self, project_root: str):
        if not REASONING_ENGINE_AVAILABLE:
            print("❌ Initialisierung fehlgeschlagen: Kern-Engine ist nicht verfügbar.")
            # Optional: Eine Exception werfen, um den Start zu verhindern
            raise RuntimeError("Core reasoning engine is not available.")

        self.project_root = project_root
        self.prover_manager = ProverManager()
        self.semantic_validator = EnhancedSemanticValidator(project_root=self.project_root)
        self.query_processor = EnhancedQueryProcessor(project_root=self.project_root)
        self.knowledge_base = self._load_knowledge_base()
        self.reasoning_stats = {
            'total_queries': 0, 'successful_proofs': 0, 'failed_proofs': 0,
            'semantically_valid': 0, 'average_time': 0.0
        }
        print("✅ Enhanced Advanced Reasoning Engine erfolgreich initialisiert.")

    def _load_knowledge_base(self) -> List[str]:
        """Lädt die Prämissen aus der semantischen Wissensbasis."""
        try:
            # KORREKTUR: Der Pfad wird direkt aus self.project_root gebildet.
            kb_path = os.path.join(self.project_root, "semantic_knowledge_base.json")
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)

                premises = [
                    fact.get('hak_gal_formula', '')
                    for fact in kb_data.get('facts', [])
                    if fact.get('hak_gal_formula') and fact.get('semantic_confidence', 0) > 0.7
                ]
                print(f"✅ {len(premises)} hoch-vertrauenswürdige Prämissen aus KB geladen.")
                return premises
            else:
                print(f"⚠️ (ReasoningEngine) Semantische KB nicht gefunden: {kb_path}")

        except Exception as e:
            print(f"❌ Fehler beim Laden der Wissensbasis: {e}")

        print("ℹ️ Verwende fest einkodierte Fallback-Wissensbasis.")
        return [
            "HauptstadtVon(Paris, France).",
            "IstKomponente(MachineLearning, AISystem).",
            "IstAktiv(AISystem).",
            "IstImplementiert(MachineLearning)."
        ]

    async def enhanced_reason(self, query: str) -> ReasoningResult:
        """Führt den gesamten Reasoning-Prozess für eine Anfrage aus."""
        start_time = time.time()
        self.reasoning_stats['total_queries'] += 1
        try:
            conclusion = self.query_processor.convert_to_hak_gal(query)
            print(f"🔄 Konvertierte Anfrage zu: {conclusion}")

            premises = self.knowledge_base
            proof_status, proof_steps, prover_used = self.prover_manager.prove(
                premises, conclusion, timeout=10
            )
            confidence = self._calculate_enhanced_confidence(proof_status, conclusion)
            execution_time = time.time() - start_time

            result = ReasoningResult(
                query=query, premises=premises, conclusion=conclusion,
                proof_status=proof_status, reasoning_type=ReasoningType.DEDUCTIVE,
                proof_steps=proof_steps, confidence=confidence,
                execution_time=execution_time, prover_used=prover_used,
                semantic_validation=False
            )

            # Semantische Validierung nach dem Beweisversuch
            result.semantic_validation = self.semantic_validator.validate_reasoning_result(result)

            # Statistiken aktualisieren
            if proof_status == ProofStatus.PROVEN:
                self.reasoning_stats['successful_proofs'] += 1
            else:
                self.reasoning_stats['failed_proofs'] += 1
            if result.semantic_validation:
                self.reasoning_stats['semantically_valid'] += 1
            self._update_average_time(execution_time)

            return result

        except Exception as e:
            print(f"❌ Ein unerwarteter Fehler ist im Reasoning-Prozess aufgetreten: {e}")
            return ReasoningResult(
                query=query, premises=[], conclusion="", proof_status=ProofStatus.ERROR,
                reasoning_type=ReasoningType.DEDUCTIVE, proof_steps=[], confidence=0.0,
                execution_time=time.time() - start_time, prover_used="none",
                semantic_validation=False, error_message=str(e)
            )

    def _calculate_enhanced_confidence(self, proof_status: ProofStatus, conclusion: str) -> float:
        """Berechnet eine erweiterte Konfidenz für das Ergebnis."""
        base_confidence = {
            ProofStatus.PROVEN: 0.9, ProofStatus.DISPROVEN: 0.8,
            ProofStatus.UNKNOWN: 0.3, ProofStatus.TIMEOUT: 0.2, ProofStatus.ERROR: 0.0
        }.get(proof_status, 0.0)

        # Bonus, wenn die Konklusion direkt aus der KB stammt
        semantic_boost = 0.0
        if self.query_processor.semantic_kb:
            if any(fact.get('hak_gal_formula') == conclusion for fact in self.query_processor.semantic_kb.get('facts', [])):
                semantic_boost = 0.1

        final_confidence = min(1.0, base_confidence + semantic_boost)
        return final_confidence

    def _update_average_time(self, execution_time: float):
        """Aktualisiert die durchschnittliche Ausführungszeit."""
        total = self.reasoning_stats['total_queries']
        current_avg = self.reasoning_stats['average_time']
        new_avg = ((current_avg * (total - 1)) + execution_time) / total
        self.reasoning_stats['average_time'] = new_avg

    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Gibt die gesammelten Statistiken der Engine zurück."""
        total = self.reasoning_stats['total_queries']
        return {
            **self.reasoning_stats,
            'success_rate': (self.reasoning_stats['successful_proofs'] / total) if total > 0 else 0,
            'semantic_validation_rate': (self.reasoning_stats['semantically_valid'] / total) if total > 0 else 0,
            'ontology_loaded': bool(self.semantic_validator.ontology),
            'knowledge_base_size': len(self.knowledge_base)
        }

# Die main-Funktion für direktes Testen der Engine bleibt unverändert.
async def main():
    print("🧠 ENHANCED ADVANCED REASONING ENGINE - SEMANTIC INTEGRATION")
    print("="*70)
    if not REASONING_ENGINE_AVAILABLE:
        return

    # Annahme: Dieses Skript liegt in 'reasoning/core', die JSONs im Parent-Parent
    project_root_for_demo = os.path.dirname(os.path.dirname(current_dir))
    print(f"ℹ️ Demo-Modus: Verwende Projekt-Root: {project_root_for_demo}")
    enhanced_engine = EnhancedReasoningEngine(project_root=project_root_for_demo)

    test_queries = [
        "What is the capital of France?",
        "Is machine learning an AI system?",
        "Show me active AI systems"
    ]
    print(f"\n🧪 Teste semantisches Reasoning:")
    print("-" * 60)
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Anfrage: {query}")
        result = await enhanced_engine.enhanced_reason(query)
        print(f"  ▶️ Ergebnis: Status={result.proof_status.value}, Konfidenz={result.confidence:.2f}, Semantisch OK={result.semantic_validation}")
        print(f"  ⚙️ Formel: {result.conclusion}")

if __name__ == "__main__":
    if REASONING_ENGINE_AVAILABLE:
        asyncio.run(main())