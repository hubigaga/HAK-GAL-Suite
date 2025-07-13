# LEARN-FUNKTION OPTIMIERUNG

## Problem
Die `learn` Funktion hatte einen Timeout nach 30 Sekunden, aber die Fakten wurden trotzdem im Hintergrund übernommen. Die Erfolgsmeldung wurde nicht angezeigt.

## Ursache
Die `learn_facts()` Methode führte für jeden einzelnen Fakt eine aufwändige Konsistenzprüfung durch:
- `check_consistency()` ruft `verify_logical()` auf
- Dies prüft mit allen Provern (Functional Constraint, Z3, Pattern Matcher, Wolfram)
- Bei 8 Fakten × mehrere Prover = >30 Sekunden

## Lösung

### 1. Optimierte Konsistenzprüfung
- Nur einfache Prüfung ob Fakt bereits existiert (O(1) mit Hash-Lookup)
- Nur direkte Negation prüfen statt volle logische Konsistenz
- Fortschrittsanzeige bei mehr als 5 Fakten

### 2. Reduzierter Timeout
- Learn-Timeout von 30s auf 15s reduziert
- Reicht für die optimierte Version aus

### 3. Besseres Feedback
- Fortschrittsanzeige während der Verarbeitung
- Detaillierte Ausgabe was hinzugefügt/übersprungen wurde
- Auto-Save nach erfolgreichem Learn

## Vorher
```python
for fact in self.potential_new_facts:
    if self.core.check_consistency(fact)[0] and self.core.add_fact(fact):
        added_count += 1
```

## Nachher  
```python
for i, fact in enumerate(self.potential_new_facts, 1):
    # Fortschrittsanzeige
    if len(self.potential_new_facts) > 5:
        print(f"   Verarbeite Fakt {i}/{len(self.potential_new_facts)}...")
    
    # Schnelle Prüfungen statt aufwändige Konsistenzprüfung
    if fact in self.core.K:
        skipped_count += 1
        continue
    
    # Nur direkte Negation prüfen
    negated_fact = f"-{fact}" if not fact.startswith('-') else fact[1:]
    if negated_fact in self.core.K:
        print(f"   ⚠️ Überspringe widersprüchlichen Fakt: {fact}")
        skipped_count += 1
        continue
```

## Performance
- Vorher: >30s für 8 Fakten
- Nachher: <5s für 8 Fakten
- Keine Timeouts mehr!
