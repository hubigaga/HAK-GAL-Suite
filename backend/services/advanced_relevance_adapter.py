"""
Advanced Relevance Manager Adapter
==================================

Drop-in-Replacement für bestehende Filter-Systeme mit Orchestrator V5 Backend.
Behält vollständige Rückwärtskompatibilität bei.
"""

import asyncio
import inspect
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass
import logging

# Local imports
from .advanced_integration import get_integration

logger = logging.getLogger(__name__)

@dataclass
class LegacyFact:
    """Legacy Fact format für Rückwärtskompatibilität"""
    id: str
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    source: str = "manual"

@dataclass 
class LegacyRelevanceResult:
    """Legacy Result format"""
    fact: LegacyFact
    score: float
    reason: str

class AdvancedRelevanceManagerAdapter:
    """
    Adapter für Orchestrator V5 mit vollständiger Rückwärtskompatibilität.
    Fallback auf einfache Filter wenn Advanced Tools nicht verfügbar.
    """
    
    def __init__(self):
        self.integration = get_integration()
        self.orchestrator = None
        self.facts_storage = []  # Fallback storage
        self.use_advanced = False
        
        # Try to initialize advanced mode
        self._initialize_advanced_mode()
    
    def _initialize_advanced_mode(self):
        """Initialisiert Advanced Mode falls möglich"""
        try:
            self.orchestrator = self.integration.get_orchestrator()
            if self.orchestrator:
                self.use_advanced = True
                logger.info("✅ Advanced Relevance Manager aktiviert")
            else:
                logger.info("⚠️ Fallback auf Simple Relevance Manager")
        except Exception as e:
            logger.error(f"❌ Advanced Mode Initialisierung fehlgeschlagen: {e}")
            self.use_advanced = False
    
    def add_fact(self, fact: LegacyFact) -> bool:
        """Fügt Fakt hinzu - Kompatibel mit Legacy Interface"""
        try:
            if self.use_advanced and self.orchestrator:
                # Convert Legacy to Advanced format
                advanced_fact = self._convert_to_advanced_fact(fact)
                
                # Use asyncio to run async method with proper awaitable detection
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    add_result = self.orchestrator.add_fact(advanced_fact)
                    # CORRECTED: Use inspect.isawaitable for proper awaitable detection
                    if inspect.isawaitable(add_result):
                        loop.run_until_complete(add_result)
                    # If not awaitable, add_fact was synchronous
                    logger.debug(f"Advanced: Fakt {fact.id} hinzugefügt")
                    return True
                finally:
                    loop.close()
            else:
                # Fallback mode
                if fact not in self.facts_storage:
                    self.facts_storage.append(fact)
                    logger.debug(f"Fallback: Fakt {fact.id} hinzugefügt")
                    return True
                return False
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen von Fakt {fact.id}: {e}")
            return False
    
    def bulk_add_facts(self, facts: List[LegacyFact]) -> int:
        """Fügt mehrere Fakten hinzu - Batch Operation"""
        added_count = 0
        try:
            if self.use_advanced and self.orchestrator:
                # Convert all facts
                advanced_facts = [self._convert_to_advanced_fact(f) for f in facts]
                
                # Use asyncio for batch operation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Fix: Handle both sync and async bulk_add_facts methods
                    try:
                        bulk_result = self.orchestrator.bulk_add_facts(advanced_facts)
                        
                        # CORRECTED: Use inspect.isawaitable for proper awaitable detection
                        if inspect.isawaitable(bulk_result):
                            loop.run_until_complete(bulk_result)
                        # If it's not awaitable, it's already completed
                        
                        added_count = len(facts)
                        logger.info(f"Advanced: {added_count} Fakten hinzugefügt")
                    except Exception as e:
                        logger.error(f"Error in orchestrator bulk_add_facts: {e}")
                        # Fallback to individual add_fact calls
                        for fact in advanced_facts:
                            try:
                                self.orchestrator.add_fact(fact)
                                added_count += 1
                            except Exception as fact_error:
                                logger.error(f"Error adding individual fact: {fact_error}")
                finally:
                    loop.close()
            else:
                # Fallback batch mode
                for fact in facts:
                    if self.add_fact(fact):
                        added_count += 1
                logger.info(f"Fallback: {added_count} Fakten hinzugefügt")
                
        except Exception as e:
            logger.error(f"Fehler bei Batch-Operation: {e}")
        
        return added_count
    
    def query(self, query_string: str, max_results: int = 100, 
              user_id: Optional[str] = None) -> List[LegacyRelevanceResult]:
        """
        Führt Query aus - Hauptschnittstelle für Legacy Code
        """
        try:
            if self.use_advanced and self.orchestrator:
                return self._query_advanced(query_string, max_results, user_id)
            else:
                return self._query_fallback(query_string, max_results)
        except Exception as e:
            logger.error(f"Query fehlgeschlagen: {e}")
            return self._query_fallback(query_string, max_results)
    
    def _query_advanced(self, query_string: str, max_results: int, 
                       user_id: Optional[str]) -> List[LegacyRelevanceResult]:
        """Advanced Query mit Orchestrator V5"""
        results = []
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Async generator to list conversion
                async def collect_results():
                    result_list = []
                    # Fix: Handle both sync and async orchestrator methods
                    try:
                        query_results = self.orchestrator.query(
                            query_string, user_id=user_id, max_results=max_results
                        )
                        
                        # CORRECTED: Use inspect.isawaitable for proper awaitable detection
                        if inspect.isawaitable(query_results):
                            query_results = await query_results
                        
                        # Handle both list and async generator returns
                        if hasattr(query_results, '__aiter__'):
                            # If it's truly async iterable
                            async for fact in query_results:
                                legacy_fact = self._convert_to_legacy_fact(fact)
                                result_list.append(LegacyRelevanceResult(
                                    fact=legacy_fact,
                                    score=getattr(fact, 'confidence', 1.0),
                                    reason=f"Advanced orchestrator match"
                                ))
                        else:
                            # If it's a regular list/iterable
                            for fact in query_results:
                                legacy_fact = self._convert_to_legacy_fact(fact)
                                result_list.append(LegacyRelevanceResult(
                                    fact=legacy_fact,
                                    score=getattr(fact, 'confidence', 1.0),
                                    reason=f"Advanced orchestrator match"
                                ))
                    except Exception as e:
                        logger.error(f"Error in orchestrator query: {e}")
                        # Fallback to empty results
                        result_list = []
                        
                    return result_list
                
                results = loop.run_until_complete(collect_results())
                
                # If no results from advanced query, try fallback
                if not results:
                    logger.warning("Advanced query returned no results, falling back to simple query")
                    results = self._query_fallback(query_string, max_results)
                else:
                    logger.debug(f"Advanced Query: {len(results)} Ergebnisse")
                
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Advanced Query fehlgeschlagen: {e}")
            results = self._query_fallback(query_string, max_results)
        
        return results
    
    def _query_fallback(self, query_string: str, max_results: int) -> List[LegacyRelevanceResult]:
        """Fallback Query mit einfacher String-Matching"""
        results = []
        query_lower = query_string.lower()
        
        for fact in self.facts_storage:
            # Simple relevance scoring
            score = 0.0
            fact_text = f"{fact.subject} {fact.predicate} {fact.object}".lower()
            
            # Exact matches
            if query_lower in fact_text:
                score += 0.8
            
            # Word matches
            query_words = query_lower.split()
            fact_words = fact_text.split()
            matches = len(set(query_words) & set(fact_words))
            if matches > 0:
                score += 0.2 * (matches / len(query_words))
            
            if score > 0:
                results.append(LegacyRelevanceResult(
                    fact=fact,
                    score=score,
                    reason=f"Fallback match: {score:.2f}"
                ))
        
        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:max_results]
        
        logger.debug(f"Fallback Query: {len(results)} Ergebnisse")
        return results
    
    def _convert_to_advanced_fact(self, legacy_fact: LegacyFact):
        """Konvertiert Legacy Fact zu Advanced Format"""
        try:
            # Import Advanced Fact here to avoid circular imports
            import sys
            import importlib.util
            
            # Load the Fact class from tools directory
            tools_path = self.integration.tools_path
            fact_module_path = tools_path / 'hak_gal_relevance_filter.py'
            
            if fact_module_path.exists():
                # Setze sys.path vor dem Import
                sys.path.insert(0, str(tools_path))
                
                spec = importlib.util.spec_from_file_location("fact_module", fact_module_path)
                fact_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(fact_module)
                Fact = fact_module.Fact
            else:
                # Fallback to path insertion
                sys.path.insert(0, str(tools_path))
                from hak_gal_relevance_filter import Fact
            
            return Fact(
                id=legacy_fact.id,
                subject=legacy_fact.subject,
                predicate=legacy_fact.predicate,
                object=legacy_fact.object,
                confidence=legacy_fact.confidence,
                source=legacy_fact.source
            )
        except Exception:
            # Create a simple dict if import fails
            return {
                'id': legacy_fact.id,
                'subject': legacy_fact.subject,
                'predicate': legacy_fact.predicate,
                'object': legacy_fact.object,
                'confidence': legacy_fact.confidence,
                'source': legacy_fact.source
            }
    
    def _convert_to_legacy_fact(self, advanced_fact) -> LegacyFact:
        """Konvertiert Advanced Fact zu Legacy Format"""
        return LegacyFact(
            id=getattr(advanced_fact, 'id', str(hash(str(advanced_fact)))),
            subject=getattr(advanced_fact, 'subject', ''),
            predicate=getattr(advanced_fact, 'predicate', ''),
            object=getattr(advanced_fact, 'object', ''),
            confidence=getattr(advanced_fact, 'confidence', 1.0),
            source=getattr(advanced_fact, 'source', 'orchestrator')
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken zurück"""
        base_stats = {
            'mode': 'advanced' if self.use_advanced else 'fallback',
            'total_facts': len(self.facts_storage),
            'orchestrator_available': self.orchestrator is not None
        }
        
        if self.use_advanced and self.orchestrator:
            try:
                advanced_stats = self.orchestrator.get_metrics()
                base_stats.update(advanced_stats)
            except Exception as e:
                logger.error(f"Fehler beim Abrufen von Advanced Stats: {e}")
        
        return base_stats
    
    def enable_advanced_features(self) -> bool:
        """Versucht erweiterte Features zu aktivieren"""
        try:
            if self.integration.enable_advanced_features():
                self.orchestrator = self.integration.get_orchestrator()
                self.use_advanced = self.orchestrator is not None
                return self.use_advanced
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren von Advanced Features: {e}")
        return False
    
    def clear_cache(self):
        """Leert alle Caches"""
        if self.use_advanced and self.orchestrator:
            try:
                self.orchestrator.cache.clear()
                logger.info("Advanced Cache geleert")
            except Exception as e:
                logger.error(f"Fehler beim Leeren des Advanced Cache: {e}")
        
        # Clear fallback storage
        self.facts_storage.clear()
        logger.info("Fallback Storage geleert")

# Create global instance
_advanced_manager = None

def get_advanced_relevance_manager() -> AdvancedRelevanceManagerAdapter:
    """Singleton factory für Advanced Relevance Manager"""
    global _advanced_manager
    if _advanced_manager is None:
        _advanced_manager = AdvancedRelevanceManagerAdapter()
    return _advanced_manager

if __name__ == "__main__":
    # Test the adapter
    manager = get_advanced_relevance_manager()
    
    # Add test facts
    test_facts = [
        LegacyFact("f1", "Socrates", "is_a", "philosopher", 0.95),
        LegacyFact("f2", "Plato", "is_a", "philosopher", 0.95),
        LegacyFact("f3", "Philosophy", "studies", "wisdom", 0.8)
    ]
    
    print(f"Adding {len(test_facts)} test facts...")
    added = manager.bulk_add_facts(test_facts)
    print(f"Added: {added}")
    
    # Test queries
    queries = ["Socrates", "philosopher", "wisdom"]
    for query in queries:
        print(f"\nQuery: '{query}'")
        results = manager.query(query, max_results=5)
        for result in results:
            print(f"  - {result.fact.subject} {result.fact.predicate} {result.fact.object} (Score: {result.score:.2f})")
    
    # Show stats
    print(f"\nStats: {manager.get_stats()}")
