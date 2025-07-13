# HAK-GAL Performance & Quality Benchmark Report

**Datum:** 2025-07-13 11:01:46

## 📊 Ergebnisse

| Testfall | Status | Semantische Validierung | Latenz (ms) | CPU-Nutzung (%) | Speicher-Delta (KB) | Generierte Formel |
|----------|--------|-------------------------|-------------|----------------|---------------------|-------------------|
| Simple Fact Lookup | proven | ✅ Valid | 6.85 | 0.00 | 17848.00 | `HauptstadtVon(Paris, France).` |
| Component Relationship | proven | ❌ Invalid | 1.81 | 0.00 | 4.00 | `Property(ai_system).` |
| Property Check | proven | ✅ Valid | 2.47 | 0.00 | 0.00 | `IstAktiv(AISystem).` |
| Complex Explanation | proven | ✅ Valid | 1.47 | 0.00 | 0.00 | `Property(explain).` |
| Unknown Concept | proven | ✅ Valid | 2.72 | 0.00 | 0.00 | `Relation(located_in, berlin).` |

## 🧠 Zusammenfassung der Engine-Statistiken

- **Gesamte Anfragen:** 5
- **Erfolgsrate (Proofs):** 100.0%
- **Semantische Validierungsrate:** 80.0%
- **Durchschnittliche Ausführungszeit:** 0.003s
- **Größe der Wissensbasis:** 9 Axiome
- **Ontologie geladen:** Ja
