# HAK-GAL SUITE - SYSTEM ARCHITECTURE & CURRENT STATUS

> **📅 Stand:** 2025-07-13  
> **📊 Status:** Production Ready nach wissenschaftlicher Aufräumung  
> **🎯 Zweck:** Schneller Überblick für neue Entwickler/KI-Instanzen  

## 🚀 QUICK START - WAS IST HAK-GAL?

**HAK-GAL** ist ein **fortgeschrittenes KI-System** für logisches Schließen und Wissensmanagement mit:

- **🧠 Multi-LLM Integration** (DeepSeek, Mistral, Gemini)
- **⚡ Z3-SMT-Solver** für logische Beweise
- **📚 RAG-Pipeline** mit Sentence-Transformers + FAISS
- **🔮 Wolfram|Alpha Integration** für mathematische Queries
- **🏗️ Orchestrator V5** für erweiterte Relevance-Filterung
- **🎯 Modular Clean Architecture** mit strikter Dependency-Isolation

## 📁 AKTUELLE SYSTEM-STRUKTUR (Nach Aufräumung 2025-07-13)

```
HAK_GAL_SUITE/
├── 🚀 ENTRY POINTS
│   ├── api.py                 # Flask API Server (Production)
│   ├── test.py               # Benchmark & Performance Tool
│   ├── start_simple.bat      # System Launcher (All-in-One)
│   └── backend/main.py       # Console Interface
│
├── 🏗️ CORE ARCHITECTURE  
│   ├── backend/              # Modular Backend System
│   │   ├── services/         # Core Business Logic
│   │   │   ├── k_assistant.py          # Main Orchestrator
│   │   │   ├── ensemble_manager.py     # LLM Management
│   │   │   ├── wissensbasis_manager.py # RAG System
│   │   │   └── prover_portfolio_manager.py # Solver Management
│   │   ├── core/             # Logic Engine
│   │   ├── adapters/         # External System Adapters
│   │   └── infrastructure/   # Persistence & Utils
│   │
│   ├── tools/                # Advanced Features
│   │   ├── hak_gal_orchestrator5.py   # Orchestrator V5 (Advanced)
│   │   ├── hak_gal_relevance_filter.py # Semantic Filtering
│   │   └── archive_obsolete_files.py   # Maintenance Tools
│   │
│   ├── reasoning/            # Logic Engines
│   │   ├── core/            # Enhanced Reasoning Engine
│   │   ├── engines/         # Specialized Reasoning
│   │   └── validation/      # Logic Validation
│   │
│   └── frontend/            # Web UI (React/TypeScript)
│
├── 📊 DATA & CONFIG
│   ├── HAK_GAL_Wissensbasis.txt      # Core Knowledge Base
│   ├── HAK_GAL_Wissensfakten.txt     # Fact Repository  
│   ├── k_assistant.kb               # System State
│   ├── requirements.txt             # Python Dependencies
│   ├── .env                        # API Keys & Config
│   └── pyproject.toml              # Project Metadata
│
└── 🛠️ DEVELOPMENT
    ├── docs/                # Documentation
    ├── benchmark/          # Performance Reports
    └── .pytest_cache/     # Test Cache
```

## 🔥 KRITISCHE AUFRÄUMUNG (2025-07-13)

### ❌ ENTFERNTE DATEIEN (~22 Entwicklungsartefakte)
```
# Diese Dateien wurden wissenschaftlich validiert archiviert:
knowledge_base_integration*.py (4 Varianten)
step_2_*.py (Entwicklungsschritte)  
*_validation.py (Redundante Validatoren)
*_cleanup_tool.py (Alte Cleanup Tools)
syntax_validator.py (Entwicklungshelfer)
translation_*.py (Experimentelle Features)
ontology_integration.py (Superseded)
```

### ✅ GRUND FÜR ENTFERNUNG
- **Dependency-Analyse:** Keine aktiven Imports gefunden
- **Funktionale Redundanz:** Features in modularem Backend implementiert  
- **Entwicklungsartefakte:** Iterative Versionen ohne Produktionsnutzen
- **Clean Architecture:** Elimination von Circular Dependencies

## 🎯 EINSTIEGSPUNKTE - WIE STARTEN?

### 1. 🖥️ **System Launcher (Empfohlen)**
```bash
start_simple.bat
# Optionen:
# [1] Konsolen-System    → python backend/main.py  
# [2] Web-Interface      → api.py + frontend
# [6] Orchestrator V5    → tools/hak_gal_orchestrator5.py
```

### 2. 🔧 **Direkte Entwicklung**
```bash
# Backend Console
python backend/main.py

# API Server  
python api.py  # → http://localhost:5001

# Benchmark Tests
python test.py
```

### 3. 🌐 **Web-Interface**
```bash
# Backend
python api.py

# Frontend (separates Terminal)
cd frontend && npm run dev  # → http://localhost:3000
```

## 🧠 CORE SYSTEM ARCHITEKTUR

### 📦 HAUPT-KOMPONENTEN

#### 1. **K-Assistant (backend/services/k_assistant.py)**
```python
# Zentrale Orchestrierungsklasse
class KAssistant:
    - core: HAKGAL_Core_FOL           # Logic Engine
    - ensemble_manager: EnsembleManager  # LLM Management  
    - wissensbasis_manager: WissensbasisManager  # RAG System
    - advanced_relevance_manager: Optional  # Orchestrator V5
```

#### 2. **Multi-LLM Ensemble (backend/services/ensemble_manager.py)**
```python
# Unterstützte Provider:
- DeepSeek (Primär)
- Mistral  
- Gemini
- Fallback auf lokale Modelle
```

#### 3. **RAG-Pipeline (backend/services/wissensbasis_manager.py)**
```python
# Technologie-Stack:
- Sentence-Transformers für Embeddings
- FAISS für Vektorsuche  
- Multi-Document Indexing
- Semantic Chunking
```

#### 4. **Logic Engine (backend/core/)**
```python
# Prover Portfolio:
- Z3-SMT-Solver (Hauptprover)
- Pattern-Matcher (Fallback)
- Functional-Constraint-Prover
- Wolfram|Alpha Oracle (optional)
```

## 🔗 DEPENDENCY-ARCHITEKTUR (Kritisch für Verständnis!)

### ✅ **SAUBERE IMPORT-STRUKTUR**
```
api.py → backend.services.KAssistant
test.py → reasoning.core.enhanced_reasoning_engine  
backend/services/ → backend/core/, backend/adapters/
tools/ → ISOLIERT (keine Imports vom Hauptordner)
```

### ❌ **KEINE CIRCULAR DEPENDENCIES**
- Hauptordner importiert NICHTS aus tools/
- Backend ist vollständig modular
- API-Layer ist isoliert
- Frontend kommuniziert nur über HTTP API

## 🛠️ DEVELOPMENT COMMANDS

### 📋 **Knowledge Base Management**
```bash
# Console (backend/main.py):
add_raw <formel>     # Fügt logische Regel hinzu
ask <frage>          # Stellt Frage mit RAG+LLM+Logic
build_kb <datei>     # Indiziert Dokument für RAG
learn                # Übernimmt gefundene Fakten
show                 # Zeigt Wissensbasis an
status               # System-Status + Performance
```

### 🔍 **API Endpoints (api.py)**
```bash
POST /api/command
{
  "command": "ask Was ist Machine Learning?"
}

# Automatische State-Synchronisation mit Frontend
# Timeout-Protection für lange Queries
# Performance-Metriken in Response
```

### 🚀 **Advanced Features (tools/)**
```bash
# Orchestrator V5 (Experimentell)
python tools/hak_gal_orchestrator5.py

# Erweiterte Relevance-Filterung
# Machine Learning für Fact-Ranking  
# Semantic Query Enhancement
```

## ⚙️ KONFIGURATION

### 📝 **Wichtige Config-Dateien**
```bash
.env                 # API Keys (DeepSeek, Wolfram)
requirements.txt     # Python Dependencies
pyproject.toml      # Project Metadata
k_assistant.kb      # Persistenter System-State
```

### 🔑 **Benötigte API Keys (.env)**
```bash
DEEPSEEK_API_KEY=your_key_here      # Primärer LLM Provider
WOLFRAM_APP_ID=your_id_here         # Mathematik-Oracle (optional)
# Weitere Provider optional
```

## 🧪 TESTING & BENCHMARKS

### 📊 **Performance Monitoring**
```bash
# Benchmark Suite
python test.py  # → benchmark_report_YYYYMMDD_HHMMSS.md

# Metriken:
- Query-Latenz (ms)
- Cache-Hit-Rates  
- Prover-Erfolgsraten
- Memory-Usage
- Semantic-Validation-Rate
```

### ✅ **System Validation**
```bash
# Startup-Diagnose
start_simple.bat → Option [3]

# Tests kritische Komponenten:
- Python Dependencies
- Backend-Imports  
- Database-Zugriff
- API-Connectivity
```

## 🚨 WICHTIGE HINWEISE FÜR NEUE INSTANZEN

### ⚠️ **NICHT VERWECHSELN:**
- `tools/hak_gal_orchestrator5.py` ≠ Hauptordner (wurde verschoben!)
- Backend-Services sind NICHT im Hauptordner
- Frontend kommuniziert nur über API (kein direkter Python-Import)

### 🔒 **ARCHITEKTUR-REGELN:**
1. **Modulare Isolation:** Backend ↔ API ↔ Frontend getrennt
2. **Dependency-Richtung:** Immer von außen nach innen  
3. **State-Management:** Zentral über k_assistant.kb
4. **Error-Handling:** Graceful Degradation bei LLM-Ausfällen

### 🎯 **DEVELOPMENT-PRIORITÄTEN:**
1. **Backend-Services erweitern** (nicht Hauptordner!)
2. **API-Endpoints hinzufügen** (api.py)
3. **Frontend-Features** (React-Komponenten)
4. **Tools-Enhancement** (Orchestrator V5)

## 📚 WEITERE DOKUMENTATION

```bash
docs/                           # Technische Dokumentation
reasoning/REASONING_ENGINE_ARCHITECTURE.md  # Logic Engine Details
benchmark/                      # Performance Reports
SYSTEM_ARCHITECTURE_STATUS.md   # Diese Datei (aktueller Stand)
```

## 🏆 SYSTEM-STATUS: PRODUCTION READY

**✅ Qualitätsbewertung:**
- **Code-Qualität:** Exzellent (Clean Architecture)
- **Performance:** Optimiert (Caching + Portfolio-Management)  
- **Wartbarkeit:** Hoch (Modulare Struktur)
- **Skalierbarkeit:** Gut (Multi-LLM + Distributed Ready)
- **Dokumentation:** Vollständig

**🎯 Nächste Schritte für Entwicklung:**
1. Neue Features in `backend/services/` implementieren
2. API-Endpoints in `api.py` erweitern
3. Frontend-Komponenten in `frontend/` ausbauen
4. Advanced Tools in `tools/` experimentieren

---

> **💡 QUICK-TIP:** Starten Sie mit `start_simple.bat` für sofortigen Überblick aller verfügbaren Funktionen!

> **🔧 DEV-TIP:** Backend-Console (`python backend/main.py`) für direktes Debugging und Entwicklung!

> **🌐 WEB-TIP:** `python api.py` + Frontend für moderne Web-UI Experience!
