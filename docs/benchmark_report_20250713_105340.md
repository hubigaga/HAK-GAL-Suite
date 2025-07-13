# HAK-GAL Performance & Quality Benchmark Report

**Datum:** 2025-07-13 10:53:40

## 📊 Ergebnisse

| Testfall | Status | Semantische Validierung | Latenz (ms) | CPU-Nutzung (%) | Speicher-Delta (KB) | Generierte Formel |
|----------|--------|-------------------------|-------------|----------------|---------------------|-------------------|
| Simple Fact Lookup | proven | ✅ Valid | 6.07 | 0.00 | 18020.00 | `HauptstadtVon(Paris, France).` |
| Component Relationship | proven | ❌ Invalid | 5.41 | 0.00 | 0.00 | `IstKomponente(MachineLearning, AISystem).` |
| Property Check | proven | ❌ Invalid | 2.45 | 0.00 | 0.00 | `IstAktiv(AISystem).` |
| Complex Explanation | proven | ❌ Invalid | 5.17 | 0.00 | 0.00 | `Relation(located_in, ai_system).` |
| Unknown Concept | proven | ❌ Invalid | 0.75 | 0.00 | 0.00 | `Relation(located_in, explain).` |

## 🧠 Zusammenfassung der Engine-Statistiken

- **Gesamte Anfragen:** 5
- **Erfolgsrate (Proofs):** 100.0%
- **Semantische Validierungsrate:** 20.0%
- **Durchschnittliche Ausführungszeit:** 0.004s
- **Größe der Wissensbasis:** 9 Axiome
- **Ontologie geladen:** Ja
