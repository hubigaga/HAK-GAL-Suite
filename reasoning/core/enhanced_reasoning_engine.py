# enhanced_reasoning_engine.py (FINALE, OPTIMIERTE VERSION)

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
    from reasoning_engine import (
        ReasoningType, ProofStatus, ReasoningResult,
        Z3SMTSolver, ProverManager, SemanticValidationEngine
    )
    REASONING_ENGINE_AVAILABLE = True
except ImportError:
    REASONING_ENGINE_AVAILABLE = False
    print("⚠️ Warnung: Die Kernkomponente 'reasoning_engine.py' konnte nicht gefunden werden.")

class EnhancedSemanticValidator:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.ontology = self._load_ontology()
        self.normalized_concept_ids = self._get_normalized_concept_ids()

    def _load_ontology(self) -> Dict:
        ontology_path = os.path.join(self.project_root, "hak_gal_ontology.json")
        try:
            if os.path.exists(ontology_path):
                with open(ontology_path, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception as e: print(f"❌ Fehler beim Laden der Ontologie: {e}")
        return {}

    def _get_normalized_concept_ids(self) -> set:
        if not self.ontology: return set()
        concept_ids = self.ontology.get('nodes', {}).keys()
        return {cid.lower().replace('_', '') for cid in concept_ids}

    def validate_reasoning_result(self, result) -> bool:
        if not self.normalized_concept_ids: return True
        match = re.search(r'\((.*?)\)', result.conclusion)
        if not match: return True
        arguments = [arg.strip() for arg in match.group(1).split(',') if arg.strip()]
        if not arguments: return True
        valid_args = 0
        for arg in arguments:
            normalized_arg = arg.lower().replace('_', '')
            if normalized_arg in self.normalized_concept_ids:
                valid_args += 1
        return (valid_args / len(arguments)) >= 0.5

class EnhancedQueryProcessor:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.semantic_kb = self._load_json(os.path.join(project_root, "semantic_knowledge_base.json"))
        self.ontology = self._load_json(os.path.join(project_root, "hak_gal_ontology.json"))

    def _load_json(self, path: str) -> Dict:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f: return json.load(f)
        except Exception: pass
        return {}

    def convert_to_hak_gal(self, query: str) -> str:
        query_lower = query.lower().strip()
        if self.semantic_kb and 'facts' in self.semantic_kb:
            # OPTIMIERUNG: Findet den besten Treffer, nicht nur den ersten
            best_match = None
            highest_similarity = 0.0
            for fact in self.semantic_kb['facts']:
                original = fact.get('original_fact', '').lower()
                similarity = self._queries_are_similar(query_lower, original)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = fact
            
            if highest_similarity > 0.4: # Finaler, optimierter Schwellenwert
                formula = best_match.get('hak_gal_formula', '')
                print(f"✅ Bester Treffer aus Wissensbasis (Ähnlichkeit: {highest_similarity:.2f}): '{best_match.get('original_fact')}' → {formula}")
                return formula

        return self._create_fallback_formula(query)

    def _queries_are_similar(self, query1: str, query2: str) -> float:
        # Ignoriert häufige, bedeutungslose Wörter für besseren Vergleich
        stop_words = {'is', 'an', 'a', 'the', 'of', 'what', 'show', 'me', 'which', 'are'}
        words1 = set(re.findall(r'\w+', query1)) - stop_words
        words2 = set(re.findall(r'\w+', query2)) - stop_words
        if not words1 or not words2: return 0.0
        overlap = len(words1.intersection(words2))
        return overlap / len(words1.union(words2))

    def _create_fallback_formula(self, original_query: str) -> str:
        query_lower = original_query.lower()
        concepts = []
        if self.ontology:
            query_words = set(re.findall(r'\b\w+\b', query_lower))
            ontology_nodes = self.ontology.get('nodes', {})
            for concept_id, concept_data in ontology_nodes.items():
                all_names = [concept_data.get('name', '')] + concept_data.get('synonyms', [])
                for name in all_names:
                    if not name: continue
                    concept_words = set(name.lower().split())
                    if concept_words.issubset(query_words):
                        concepts.append(concept_id)
                        break
        # OPTIMIERUNG: Sortiert die Konzepte, um eine deterministische Ausgabe zu gewährleisten
        concepts = sorted(list(set(concepts)))
        print(f"  ℹ️ Fallback-Analyse: Gefundene Konzepte in Anfrage: {concepts}")
        if len(concepts) >= 2: return f"Relation({concepts[0]}, {concepts[1]})."
        elif len(concepts) == 1: return f"Property({concepts[0]})."
        else:
            words = [word.capitalize() for word in re.sub(r'[^a-zA-Z0-9\s]', '', original_query).split()[:3]]
            return f"Query({','.join(words)})."

class EnhancedReasoningEngine:
    def __init__(self, project_root: str):
        if not REASONING_ENGINE_AVAILABLE: raise RuntimeError("Core reasoning engine is not available.")
        self.project_root = project_root
        self.prover_manager = ProverManager()
        self.semantic_validator = EnhancedSemanticValidator(project_root=self.project_root)
        self.query_processor = EnhancedQueryProcessor(project_root=self.project_root)
        self.knowledge_base = self._load_knowledge_base()
        self.reasoning_stats = {'total_queries': 0, 'successful_proofs': 0, 'failed_proofs': 0, 'semantically_valid': 0, 'average_time': 0.0}
        print("✅ Enhanced Advanced Reasoning Engine erfolgreich initialisiert.")

    def _load_knowledge_base(self) -> List[str]:
        kb_path = os.path.join(self.project_root, "semantic_knowledge_base.json")
        try:
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f: kb_data = json.load(f)
                premises = [fact.get('hak_gal_formula') for fact in kb_data.get('facts', []) if fact.get('hak_gal_formula') and fact.get('semantic_confidence', 0) > 0.7]
                print(f"✅ {len(premises)} hoch-vertrauenswürdige Prämissen aus KB geladen.")
                return premises
        except Exception as e: print(f"❌ Fehler beim Laden der Wissensbasis: {e}")
        return []

    async def enhanced_reason(self, query: str) -> ReasoningResult:
        start_time = time.time()
        self.reasoning_stats['total_queries'] += 1
        try:
            conclusion = self.query_processor.convert_to_hak_gal(query)
            print(f"🔄 Konvertierte Anfrage zu: {conclusion}")
            premises = self.knowledge_base
            proof_status, proof_steps, prover_used = self.prover_manager.prove(premises, conclusion, timeout=10)
            result = ReasoningResult(
                query=query, premises=premises, conclusion=conclusion, proof_status=proof_status,
                reasoning_type=ReasoningType.DEDUCTIVE, proof_steps=proof_steps,
                confidence=0.9 if proof_status == ProofStatus.PROVEN else 0.3,
                execution_time=time.time() - start_time, prover_used=prover_used, semantic_validation=False
            )
            result.semantic_validation = self.semantic_validator.validate_reasoning_result(result)
            if result.proof_status == ProofStatus.PROVEN: self.reasoning_stats['successful_proofs'] += 1
            else: self.reasoning_stats['failed_proofs'] += 1
            if result.semantic_validation: self.reasoning_stats['semantically_valid'] += 1
            self._update_average_time(result.execution_time)
            return result
        except Exception as e:
            return ReasoningResult(
                query=query, premises=[], conclusion="", proof_status=ProofStatus.ERROR,
                reasoning_type=ReasoningType.DEDUCTIVE, proof_steps=[], confidence=0.0,
                execution_time=time.time() - start_time, prover_used="none",
                semantic_validation=False, error_message=str(e)
            )

    def _update_average_time(self, execution_time: float):
        total = self.reasoning_stats['total_queries']
        current_avg = self.reasoning_stats['average_time']
        self.reasoning_stats['average_time'] = ((current_avg * (total - 1)) + execution_time) / total if total > 0 else 0

    def get_enhanced_statistics(self) -> Dict[str, Any]:
        total = self.reasoning_stats['total_queries']
        return {**self.reasoning_stats, 'success_rate': (self.reasoning_stats['successful_proofs'] / total) if total > 0 else 0, 'semantic_validation_rate': (self.reasoning_stats['semantically_valid'] / total) if total > 0 else 0, 'ontology_loaded': bool(self.semantic_validator.ontology), 'knowledge_base_size': len(self.knowledge_base)}

# Main-Funktion für direktes Testen bleibt unverändert
if __name__ == "__main__":
    if REASONING_ENGINE_AVAILABLE: asyncio.run(main())