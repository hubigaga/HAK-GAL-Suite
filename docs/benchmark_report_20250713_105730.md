# HAK-GAL Performance & Quality Benchmark Report

**Datum:** 2025-07-13 10:57:31

## 📊 Ergebnisse

| Testfall | Status | Semantische Validierung | Latenz (ms) | CPU-Nutzung (%) | Speicher-Delta (KB) | Generierte Formel |
|----------|--------|-------------------------|-------------|----------------|---------------------|-------------------|
| Simple Fact Lookup | proven | ✅ Valid | 3.83 | 0.00 | 17792.00 | `HauptstadtVon(Paris, France).` |
| Component Relationship | proven | ❌ Invalid | 0.85 | 0.00 | 0.00 | `Property(ai_system).` |
| Property Check | proven | ❌ Invalid | 1.68 | 0.00 | 0.00 | `Relation(ai_system, active).` |
| Complex Explanation | proven | ❌ Invalid | 1.01 | 0.00 | 0.00 | `Property(explain).` |
| Unknown Concept | proven | ❌ Invalid | 1.64 | 0.00 | 0.00 | `Relation(located_in, berlin).` |

## 🧠 Zusammenfassung der Engine-Statistiken

- **Gesamte Anfragen:** 5
- **Erfolgsrate (Proofs):** 100.0%
- **Semantische Validierungsrate:** 20.0%
- **Durchschnittliche Ausführungszeit:** 0.001s
- **Größe der Wissensbasis:** 9 Axiome
- **Ontologie geladen:** Ja
