# HAK-GAL Suite: A Hybrid Reasoning Framework

![PyPI](https://img.shields.io/pypi/v/hak-gal)
![Build Status](https://github.com/sookoothaii/HAK-GAL-Suite/actions/workflows/ci.yml/badge.svg)
![Sentry](https://img.shields.io/badge/Sentry-Monitor-green)

HAK-GAL is a scalable AI-reasoning framework that integrates neural flexibility with symbolic verification and real-time monitoring.

## 1. Abstract

HAK-GAL (Hybrid Assertion Knowledge & Grounded Assertion Logic) is a modular software framework designed to integrate the semantic processing capabilities of Large Language Models (LLMs) with the formal rigor of symbolic logic. The primary objective is to facilitate robust, verifiable, and explainable reasoning. This is achieved by grounding all inferences in a formally consistent knowledge base, which is managed and validated by a portfolio of specialized logical and computational provers. This architecture is explicitly engineered to mitigate the risk of factual inaccuracies inherent in purely generative models.

This repository contains the source code for the HAK-GAL engine, its backend API, and a reference web application.

## 2. Current Implemented State (What is "Ready to Run")

This section details the features and components that are currently implemented, tested, and functional in the main branch.

### 2.1. Core Reasoning Engine

* **Hybrid Prover Portfolio:** A manager that delegates queries to a portfolio of provers:

  * **Pattern Matcher:** For O(1) lookup of existing facts and direct contradictions.
  * **Z3 SMT Solver Integration:** For formal proofs of first-order logic formulas.
  * **Wolfram|Alpha API Integration:** As an external "oracle" for real-world data and mathematical computations.
  * **Functional Constraint Prover:** A specialized component to enforce uniqueness constraints (e.g., a city has only one population count), implementing a subset of Description Logic with functional properties.
* **High-Performance RelevanceFilter:** A pre-processing module that significantly reduces the search space for a given query. It employs keyword indexing and N-hop graph expansion to construct a minimal, relevant subset of the knowledge base, enabling efficient reasoning on large fact sets.

### 2.2. Knowledge Management

* **Persistent Knowledge Base:** Storage and management of axioms and facts in a verifiable, consistent manner.
* **Supervised Ingestion Pipeline:** A multi-stage process to support the creation of the knowledge base from unstructured text (PDF, TXT):

  * **RAG for Context Retrieval:** Utilizes a FAISS-based vector index for semantic search in documents.
  * **LLM-based Fact Extraction:** An LLM ensemble proposes candidate facts from the retrieved context.
  * **Mandatory Human-in-the-Loop Review:** All automatically extracted facts are placed in a review queue and require explicit human approval before being added to the core knowledge base. This ensures 100% human oversight over the ground truth.

### 2.3. Formal Integrity

* **Lark-based LALR Parser:** Enforces a strict, custom-defined grammar (HAKGAL\_GRAMMAR) for all logical inputs, ensuring syntactic correctness.
* **Consistency Checks:** Utilizes the Z3 prover to validate that new facts do not introduce logical contradictions into the existing knowledge base.

---

## 3. Theoretical Vision & Research Roadmap (The "Archon-Prime" Concept)

This section outlines the long-term research vision that guides the project's development. These concepts are **not yet fully implemented** but represent the architectural blueprint for future work.

### 3.1. The Governance-Driven Architecture

The long-term goal is to structure the system's internal processes according to a "separation of powers" model to enhance security and robustness. This involves formalizing the roles of the `Knowledge Base` (Legislative), the `Prover Portfolio` (Judiciary), and the `Execution Engine` (Executive) to create a system of "checks and balances."

### 3.2. Meta-Reasoning and Self-Reflection

The "Archon-Prime" vision aims to evolve the framework into a system that reasons not only about external data but also about its own reasoning processes. Key research areas include:

* **Abductive Reasoning:** Implementing a formal engine to generate a minimal hypothesis `H` required to prove a currently unprovable goal `Q` (`KB ∧ H ⊨ Q`).
* **Dynamic Belief Revision:** Moving from a monotonic to a non-monotonic logic, allowing the system to rationally revise or retract previously held beliefs based on new, more credible evidence, guided by the AGM postulates.
* **Learned Relevance:** Enhancing the `RelevanceFilter` with machine learning models that adapt and improve its performance based on user interactions and feedback (e.g., via click-through rates).

### 3.3. Towards a Computational Theory of Emotion

A highly theoretical research track explores the formalization of emotional and cognitive processes. This involves synthesizing a) AGM Belief Revision Theory to model belief changes, b) Fuzzy Logic to represent a-rational states, and c) a concept of "Gödelian states" to handle non-resolvable emotional contradictions. This is a purely exploratory part of the project's long-term vision.

---

## 4. Getting Started

### 4.1. Prerequisites

* Python 3.9+ (for backend, parsing, and core logic)
* Node.js (for the reference frontend)
* Docker & Docker Compose (optional, recommended for reproducibility)
* API keys for external services (Wolfram|Alpha, OpenAI, Mistral, Anthropic, etc.)

### 4.2. Installation

**1. Clone the repository**

```bash
git clone https://github.com/sookoothaii/HAK-GAL-Suite.git
cd HAK-GAL-Suite
```

**2. Set up Python environment**

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# or
.venv\Scripts\activate           # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

**3. Configure API Keys**

Copy the template `.env.example` to `.env` and add your API credentials.

```bash
cp .env.example .env
# Edit .env and add your API keys
```

**4. (Optional) Start with Docker**

For a reproducible environment:

```bash
docker-compose up --build
```

This will build and launch the backend, frontend, and all supporting services.

**5. Start backend and frontend manually**

*Backend:*

```bash
cd backend
python -m app.main
```

*Frontend:*

```bash
cd frontend
npm install
npm run dev
```

### 4.3. Basic Usage

* Access the web interface at `http://localhost:3000` (or your configured port).
* The backend API is available at `http://localhost:8000`.
* Use the web UI or CLI to upload documents, review proposed facts, and run logical queries.

### 4.4. First Steps

* Ingest a document (PDF/TXT) via the UI or CLI.
  The system extracts candidate facts using RAG and LLMs.
* Review facts in the human-in-the-loop queue before they are added to the knowledge base.
* Run logical queries:
  Enter natural language or formal logic formulas. All queries are parsed, normalized, and validated by the prover portfolio.

### 4.5. Testing

```bash
pytest              # Runs the test suite (unit and integration tests)
```

### 4.6. Documentation

* **Core API documentation:** `docs/`
* **Contribution guidelines:** `docs/CONTRIBUTING.md`
* **System architecture:** See `docs/architecture.md` and the code comments in `backend/` and `frontend/`

---

**If you encounter issues:**

* Check the logs in `backend/logs/` for diagnostics.
* Review the troubleshooting section in `docs/TROUBLESHOOTING.md`.
* Open an issue in the GitHub repository if the problem persists.

---

**Summary:**
The HAK-GAL Suite is ready to run out-of-the-box with these steps. All core features described in section 2 are implemented and tested. For advanced usage and research features, consult the documentation and roadmap.

---

