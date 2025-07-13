"""
HAK-GAL Orchestrator V5 Integration für KAssistant
=================================================

Dieses Modul integriert den Orchestrator V5 als optionales Feature
in die bestehende KAssistant-Klasse.
"""

import os
import sys
import asyncio
from typing import List, Optional

# Füge tools zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

try:
    from hak_gal_orchestrator5 import (
        OrchestratingRelevanceManager,
        OrchestratorConfig,
        FilterStrategy,
        Fact
    )
    ORCHESTRATOR_V5_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_V5_AVAILABLE = False
    print("⚠️ Orchestrator V5 nicht verfügbar - Standard-Filter wird verwendet")


class OrchestrationMixin:
    """Mixin-Klasse für Orchestrator V5 Integration."""
    
    def __init__(self):
        self._orchestrator = None
        self._orchestrator_config = None
        
    def init_orchestrator_v5(self):
        """Initialisiert den Orchestrator V5 wenn verfügbar."""
        if not ORCHESTRATOR_V5_AVAILABLE:
            return False
            
        try:
            # Konfiguration für Orchestrator
            self._orchestrator_config = OrchestratorConfig(
                enable_semantic=True,
                enable_learning=False,  # Deaktiviert bis stabil
                enable_distributed=False,  # Deaktiviert bis stabil
                enable_ml=False,  # Deaktiviert bis ML-Modell trainiert
                enable_neuro_symbolic=False,  # Deaktiviert bis stabil
                structural_weight=0.8,
                semantic_weight=0.2,
                max_query_time=2.0,
                cache_size=10000
            )
            
            # Erstelle Orchestrator
            self._orchestrator = OrchestratingRelevanceManager(self._orchestrator_config)
            
            # Synchronisiere existierende Fakten
            if hasattr(self, 'permanentKnowledge'):
                facts_to_add = []
                for fact_str in self.permanentKnowledge:
                    # Konvertiere String-Fakten zu Fact-Objekten
                    # Format: "predicate(subject, object)"
                    try:
                        parts = self._parse_fact_string(fact_str)
                        if parts:
                            fact = Fact(
                                id=f"fact_{len(facts_to_add)}",
                                subject=parts['subject'],
                                predicate=parts['predicate'],
                                object=parts['object'],
                                confidence=0.95,
                                source="k_assistant"
                            )
                            facts_to_add.append(fact)
                    except:
                        pass
                
                if facts_to_add:
                    # Blockiere bis Fakten hinzugefügt sind
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._orchestrator.bulk_add_facts(facts_to_add))
                    loop.close()
                    
            print("✅ Orchestrator V5 initialisiert")
            return True
            
        except Exception as e:
            print(f"❌ Fehler bei Orchestrator V5 Initialisierung: {e}")
            self._orchestrator = None
            return False
    
    def query_orchestrator(self, query: str, strategy: Optional[str] = None) -> List[str]:
        """Führt eine Abfrage mit dem Orchestrator V5 aus."""
        if not self._orchestrator:
            return []
            
        try:
            # Konvertiere Strategy-String zu Enum
            filter_strategy = None
            if strategy:
                strategy_map = {
                    'structural': FilterStrategy.STRUCTURAL_ONLY,
                    'semantic': FilterStrategy.SEMANTIC_ONLY,
                    'hybrid': FilterStrategy.HYBRID_STRUCTURAL_SEMANTIC,
                    'adaptive': FilterStrategy.ADAPTIVE
                }
                filter_strategy = strategy_map.get(strategy.lower())
            
            # Führe asynchrone Abfrage aus
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            results = []
            async def run_query():
                async for fact in self._orchestrator.query(
                    query=query,
                    strategy=filter_strategy,
                    max_results=50
                ):
                    results.append(fact)
            
            loop.run_until_complete(run_query())
            loop.close()
            
            # Konvertiere Ergebnisse zu Strings
            fact_strings = []
            for fact in results:
                if hasattr(fact, 'predicate') and hasattr(fact, 'subject'):
                    if hasattr(fact, 'object') and fact.object:
                        fact_str = f"{fact.predicate}({fact.subject}, {fact.object})"
                    else:
                        fact_str = f"{fact.predicate}({fact.subject})"
                    fact_strings.append(fact_str)
            
            return fact_strings
            
        except Exception as e:
            print(f"❌ Fehler bei Orchestrator-Abfrage: {e}")
            return []
    
    def _parse_fact_string(self, fact_str: str) -> Optional[dict]:
        """Parst einen Fakt-String in seine Komponenten."""
        import re
        
        # Versuche verschiedene Formate
        patterns = [
            r'(\w+)\(([^,]+),\s*([^)]+)\)',  # predicate(subject, object)
            r'(\w+)\(([^)]+)\)',  # predicate(subject)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, fact_str.strip())
            if match:
                if len(match.groups()) == 3:
                    return {
                        'predicate': match.group(1),
                        'subject': match.group(2).strip(),
                        'object': match.group(3).strip()
                    }
                elif len(match.groups()) == 2:
                    return {
                        'predicate': match.group(1),
                        'subject': match.group(2).strip(),
                        'object': ''
                    }
        
        return None
    
    def get_orchestrator_metrics(self) -> dict:
        """Gibt Metriken des Orchestrators zurück."""
        if not self._orchestrator:
            return {'status': 'not_initialized'}
            
        try:
            return self._orchestrator.get_metrics()
        except:
            return {'status': 'error'}


# Erweiterte Befehle für KAssistant
ORCHESTRATOR_COMMANDS = {
    'orchestrator_init': {
        'description': 'Initialisiert Orchestrator V5',
        'handler': lambda assistant, args: assistant.init_orchestrator_v5()
    },
    'orchestrator_query': {
        'description': 'Führt Abfrage mit Orchestrator V5 aus',
        'handler': lambda assistant, args: assistant.orchestrator_query_command(args)
    },
    'orchestrator_status': {
        'description': 'Zeigt Orchestrator V5 Status',
        'handler': lambda assistant, args: assistant.orchestrator_status_command()
    }
}


def integrate_orchestrator_commands(k_assistant_instance):
    """Fügt Orchestrator-Befehle zu einer KAssistant-Instanz hinzu."""
    
    # Mixin-Methoden hinzufügen
    for method_name in dir(OrchestrationMixin):
        if not method_name.startswith('_') or method_name.startswith('_parse'):
            method = getattr(OrchestrationMixin, method_name)
            if callable(method):
                setattr(k_assistant_instance.__class__, method_name, method)
    
    # Command-Handler hinzufügen
    def orchestrator_query_command(self, args):
        if not args:
            print("Verwendung: orchestrator_query <Abfrage> [strategy]")
            print("Strategien: structural, semantic, hybrid, adaptive")
            return
            
        parts = args.split(' ', 1)
        query = parts[0]
        strategy = parts[1] if len(parts) > 1 else None
        
        print(f"\n🔍 Orchestrator V5 Abfrage: '{query}'")
        if strategy:
            print(f"   Strategie: {strategy}")
        
        results = self.query_orchestrator(query, strategy)
        if results:
            print(f"\n✅ {len(results)} Ergebnisse gefunden:")
            for i, result in enumerate(results[:10]):
                print(f"   [{i+1}] {result}")
            if len(results) > 10:
                print(f"   ... und {len(results) - 10} weitere")
        else:
            print("❌ Keine Ergebnisse gefunden")
    
    def orchestrator_status_command(self):
        metrics = self.get_orchestrator_metrics()
        print("\n📊 Orchestrator V5 Status:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
    
    # Methoden hinzufügen
    setattr(k_assistant_instance.__class__, 'orchestrator_query_command', orchestrator_query_command)
    setattr(k_assistant_instance.__class__, 'orchestrator_status_command', orchestrator_status_command)
    
    # Initialisierung
    OrchestrationMixin.__init__(k_assistant_instance)
    
    print("✅ Orchestrator V5 Integration bereit")
    print("   Verwenden Sie 'orchestrator_init' zum Aktivieren")
    

if __name__ == "__main__":
    # Test der Integration
    print("Testing Orchestrator V5 Integration...")
    print(f"Orchestrator V5 verfügbar: {ORCHESTRATOR_V5_AVAILABLE}")
