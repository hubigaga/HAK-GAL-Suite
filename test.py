# test.py (repariert und optimiert)

import sys
import os
import asyncio
import time
import psutil
from datetime import datetime
from typing import Dict, Any

# --- 1. Definition der Projektstruktur ---
# Das Root-Verzeichnis ist das Verzeichnis, in dem dieses Skript (test.py) liegt.
# Alle anderen Pfade werden relativ dazu aufgebaut.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ENGINE_PATH = os.path.join(PROJECT_ROOT, 'reasoning', 'core')

# --- 2. Dynamische Anpassung des Python-Suchpfads ---
# Dies muss VOR dem Importversuch der Engine geschehen.
if ENGINE_PATH not in sys.path:
    sys.path.insert(0, ENGINE_PATH)

print(f"ℹ️ Projekt-Root: {PROJECT_ROOT}")
print(f"ℹ️ Engine-Pfad zum Suchpfad hinzugefügt: {ENGINE_PATH}")

# --- 3. Sicherer Import der Engine ---
# Der try-except-Block fängt nun zwei mögliche Fehler ab:
# a) Das Modul wird nicht gefunden (ImportError)
# b) Das Modul wird gefunden, aber seine eigenen Abhängigkeiten fehlen (REASONING_ENGINE_AVAILABLE ist False)
try:
    from enhanced_reasoning_engine import EnhancedReasoningEngine, REASONING_ENGINE_AVAILABLE
    if not REASONING_ENGINE_AVAILABLE:
        # Dieser Fall tritt ein, wenn 'enhanced_reasoning_engine.py' gefunden wurde,
        # aber die 'reasoning_engine.py' (die Core-Komponente) nicht importieren konnte.
        print("❌ KRITISCHER FEHLER: Die Kernkomponente 'reasoning_engine' konnte nicht geladen werden.")
        print("   Bitte stellen Sie sicher, dass die Datei 'reasoning_engine.py' im selben Verzeichnis liegt wie 'enhanced_reasoning_engine.py'.")
        exit(1)
except ImportError as e:
    print(f"❌ KRITISCHER FEHLER: Konnte die 'enhanced_reasoning_engine.py' nicht finden oder importieren.")
    print(f"   Erwarteter Pfad: {ENGINE_PATH}")
    print(f"   Überprüfen Sie Ihre Verzeichnisstruktur.")
    print(f"   Fehlerdetails: {e}")
    exit(1)

# Der Dateiname für den Report wird einmalig beim Start generiert.
REPORT_FILE = os.path.join(PROJECT_ROOT, f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

class BenchmarkRunner:
    """Führt die Benchmark-Tests aus und generiert einen Report."""
    def __init__(self, engine: EnhancedReasoningEngine):
        self.engine = engine
        self.results = []
        # Testfälle bleiben unverändert
        self.test_cases: Dict[str, str] = {
            "Simple Fact Lookup": "What is the capital of France?",
            "Component Relationship": "Is machine learning an AI system?",
            "Property Check": "Show me active AI systems",
            "Complex Explanation": "explain IstSäugetier(Sokrates)",
            "Unknown Concept": "What is the weather like in Berlin?"
        }

    async def _run_single_test(self, test_name: str, query: str) -> Dict[str, Any]:
        """Führt einen einzelnen Testfall aus und misst die Performance."""
        print(f"  -> Teste: '{test_name}'...")
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        # CPU-Messung ist zuverlässiger, wenn sie über einen kurzen Zeitraum läuft
        process.cpu_percent(interval=None) 
        start_time = time.perf_counter()

        # Asynchroner Aufruf der Engine
        reasoning_result = await self.engine.enhanced_reason(query)

        latency = (time.perf_counter() - start_time) * 1000
        cpu_after = process.cpu_percent(interval=None)
        mem_after = process.memory_info().rss

        return {
            "name": test_name,
            "query": query,
            "status": reasoning_result.proof_status.value,
            "semantic_validation": "✅ Valid" if reasoning_result.semantic_validation else "❌ Invalid",
            "latency_ms": f"{latency:.2f}",
            "cpu_delta_percent": f"{cpu_after:.2f}", # CPU-Delta ist die Nutzung nach dem Aufruf
            "mem_delta_kb": f"{(mem_after - mem_before) / 1024:.2f}",
            "conclusion": reasoning_result.conclusion
        }

    async def run_benchmarks(self):
        """Führt alle definierten Testfälle nacheinander aus."""
        print(f"\n🚀 Starte HAK-GAL Benchmark-Lauf für {len(self.test_cases)} Testfälle...")
        for test_name, query in self.test_cases.items():
            result = await self._run_single_test(test_name, query)
            self.results.append(result)
            await asyncio.sleep(0.1) # Kurze Pause zwischen den Tests
        print("✅ Benchmark-Lauf abgeschlossen.")

    def generate_report(self):
        """Schreibt die gesammelten Ergebnisse in eine Markdown-Datei."""
        if not self.results:
            print("⚠️ Keine Ergebnisse zum Reporten vorhanden.")
            return

        print(f"\n📝 Generiere Report in '{REPORT_FILE}'...")
        try:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(f"# HAK-GAL Performance & Quality Benchmark Report\n\n")
                f.write(f"**Datum:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## 📊 Ergebnisse\n\n")
                f.write("| Testfall | Status | Semantische Validierung | Latenz (ms) | CPU-Nutzung (%) | Speicher-Delta (KB) | Generierte Formel |\n")
                f.write("|----------|--------|-------------------------|-------------|----------------|---------------------|-------------------|\n")
                for res in self.results:
                    # Bereinigung der Formel für die Markdown-Tabelle
                    conclusion_md = res['conclusion'].replace('|', '\|')
                    f.write(f"| {res['name']} | {res['status']} | {res['semantic_validation']} | {res['latency_ms']} | {res['cpu_delta_percent']} | {res['mem_delta_kb']} | `{conclusion_md}` |\n")

                f.write("\n## 🧠 Zusammenfassung der Engine-Statistiken\n\n")
                engine_stats = self.engine.get_enhanced_statistics()
                f.write(f"- **Gesamte Anfragen:** {engine_stats['total_queries']}\n")
                f.write(f"- **Erfolgsrate (Proofs):** {engine_stats['success_rate']:.1%}\n")
                f.write(f"- **Semantische Validierungsrate:** {engine_stats['semantic_validation_rate']:.1%}\n")
                f.write(f"- **Durchschnittliche Ausführungszeit:** {engine_stats['average_time']:.3f}s\n")
                f.write(f"- **Größe der Wissensbasis:** {engine_stats['knowledge_base_size']} Axiome\n")
                f.write(f"- **Ontologie geladen:** {'Ja' if engine_stats['ontology_loaded'] else 'Nein'}\n")

            print(f"✅ Report wurde erfolgreich gespeichert.")
        except IOError as e:
            print(f"❌ FEHLER: Konnte den Report nicht schreiben. Grund: {e}")

async def main():
    """
    Hauptfunktion: Initialisiert die Engine und den Benchmark-Runner und startet den Prozess.
    """
    print("\n--- Initialisierung der HAK-GAL Reasoning Engine ---")
    # Die Engine wird mit dem PROJECT_ROOT initialisiert.
    # So weiß sie, wo sie nach den JSON-Dateien suchen muss.
    engine = EnhancedReasoningEngine(project_root=PROJECT_ROOT)
    
    runner = BenchmarkRunner(engine=engine)
    await runner.run_benchmarks()
    runner.generate_report()

if __name__ == "__main__":
    # Der Haupt-Einstiegspunkt des Skripts.
    # Die kritischen Prüfungen sind bereits am Anfang des Skripts erfolgt.
    asyncio.run(main())