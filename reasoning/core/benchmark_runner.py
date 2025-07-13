# benchmark_runner.py

import asyncio
import time
import os
import psutil
from datetime import datetime
from typing import Dict, Any

# Importiere die Kernkomponente direkt aus deinem bestehenden Skript
try:
    from enhanced_reasoning_engine import EnhancedReasoningEngine, REASONING_ENGINE_AVAILABLE
except ImportError as e:
    print(f"❌ KRITISCHER FEHLER: Konnte die 'enhanced_reasoning_engine.py' nicht finden oder importieren.")
    print(f"   Stellen Sie sicher, dass dieses Skript im selben Verzeichnis liegt.")
    print(f"   Fehlerdetails: {e}")
    exit()

# --- Konfiguration ---
REPORT_FILE = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

class BenchmarkRunner:
    """
    Führt einen Satz von vordefinierten Testfällen gegen die 
    EnhancedReasoningEngine aus und misst dabei Performance-Metriken.
    """
    def __init__(self, engine: EnhancedReasoningEngine):
        if not REASONING_ENGINE_AVAILABLE:
            raise RuntimeError("Core reasoning engine ist nicht verfügbar. Benchmark kann nicht gestartet werden.")
        
        self.engine = engine
        self.results = []
        
        # Testfälle, die die verschiedenen Aspekte des Systems abdecken
        self.test_cases: Dict[str, str] = {
            "Simple Fact Lookup": "What is the capital of France?",
            "Component Relationship": "Is machine learning an AI system?",
            "Property Check": "Show me active AI systems",
            "Complex Explanation": "explain IstSäugetier(Sokrates)", # Angenommene komplexe Query
            "Unknown Concept": "What is the weather like in Berlin?" # Testet Fallback-Verhalten
        }

    async def _run_single_test(self, test_name: str, query: str) -> Dict[str, Any]:
        """Führt einen einzelnen Testfall aus und erfasst die Metriken."""
        print(f"  -> Teste: '{test_name}'...")
        
        # Ressourcenmessung vor dem Lauf
        process = psutil.Process(os.getpid())
        cpu_before = process.cpu_percent(interval=None)
        mem_before = process.memory_info().rss

        start_time = time.perf_counter()
        
        # Führe die Reasoning-Pipeline aus
        reasoning_result = await self.engine.enhanced_reason(query)
        
        latency = (time.perf_counter() - start_time) * 1000  # in Millisekunden

        # Ressourcenmessung nach dem Lauf
        cpu_after = process.cpu_percent(interval=None)
        mem_after = process.memory_info().rss

        # Sammle die Ergebnisse in einem strukturierten Format
        return {
            "name": test_name,
            "query": query,
            "status": reasoning_result.proof_status.value,
            "semantic_validation": "✅ Valid" if reasoning_result.semantic_validation else "❌ Invalid",
            "latency_ms": f"{latency:.2f}",
            "cpu_delta_percent": f"{cpu_after - cpu_before:.2f}",
            "mem_delta_kb": f"{(mem_after - mem_before) / 1024:.2f}",
            "conclusion": reasoning_result.conclusion
        }

    async def run_benchmarks(self):
        """Führt alle definierten Benchmark-Testfälle aus."""
        print(f"\n🚀 Starte HAK-GAL Benchmark-Lauf für {len(self.test_cases)} Testfälle...")
        
        for test_name, query in self.test_cases.items():
            result = await self._run_single_test(test_name, query)
            self.results.append(result)
            # Kurze Pause, um die CPU-Messung nicht zu verfälschen
            await asyncio.sleep(0.1)

        print("✅ Benchmark-Lauf abgeschlossen.")

    def generate_report(self):
        """Erstellt einen Markdown-Report mit den Ergebnissen."""
        if not self.results:
            print("Keine Ergebnisse zum Reporten vorhanden.")
            return

        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"# HAK-GAL Performance & Quality Benchmark Report\n\n")
            f.write(f"**Datum:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 📊 Ergebnisse\n\n")
            f.write("| Testfall | Status | Semantische Validierung | Latenz (ms) | CPU-Delta (%) | Speicher-Delta (KB) | Generierte Formel |\n")
            f.write("|----------|--------|-------------------------|-------------|---------------|---------------------|-------------------|\n")
            for res in self.results:
                f.write(f"| {res['name']} | {res['status']} | {res['semantic_validation']} | {res['latency_ms']} | {res['cpu_delta_percent']} | {res['mem_delta_kb']} | `{res['conclusion']}` |\n")
            
            f.write("\n## 🧠 Zusammenfassung der Engine-Statistiken\n\n")
            engine_stats = self.engine.get_enhanced_statistics()
            f.write(f"- **Gesamte Anfragen:** {engine_stats['total_queries']}\n")
            f.write(f"- **Erfolgsrate (Proofs):** {engine_stats['success_rate']:.1%}\n")
            f.write(f"- **Semantische Validierungsrate:** {engine_stats['semantic_validation_rate']:.1%}\n")
            f.write(f"- **Durchschnittliche Ausführungszeit:** {engine_stats['average_time']:.3f}s\n")
            f.write(f"- **Größe der Wissensbasis:** {engine_stats['knowledge_base_size']} Axiome\n")
            f.write(f"- **Ontologie geladen:** {'Ja' if engine_stats['ontology_loaded'] else 'Nein'}\n")

        print(f"\n📝 Report wurde erfolgreich in '{REPORT_FILE}' gespeichert.")

async def main():
    # Initialisiere die Engine, die wir testen wollen
    engine = EnhancedReasoningEngine()
    
    # Erstelle und starte den Benchmark-Runner
    runner = BenchmarkRunner(engine)
    await runner.run_benchmarks()
    runner.generate_report()

if __name__ == "__main__":
    # Prüfe, ob die Kern-Engine überhaupt verfügbar ist
    if not REASONING_ENGINE_AVAILABLE:
        print("❌ Benchmark kann nicht gestartet werden, da die Kernkomponenten fehlen.")
        exit(1)
        
    # Führe den asynchronen Benchmark aus
    asyncio.run(main())