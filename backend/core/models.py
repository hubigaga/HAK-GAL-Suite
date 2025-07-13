# -*- coding: utf-8 -*-
"""
Domain-Modelle für die HAK-GAL Architektur
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class QueryType(Enum):
    """Typen von Anfragen, die das System verarbeiten kann."""
    LOGIC = "logic"
    KNOWLEDGE = "knowledge"
    MATHEMATICAL = "mathematical"
    MIXED = "mixed"


class ComplexityLevel(Enum):
    """Komplexitätsstufen für Anfragen."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


@dataclass
class ComplexityReport:
    """
    Analyse-Bericht für Query-Komplexität und Ressourcen-Anforderungen.
    
    Attributes:
        query_type: Typ der Anfrage
        complexity_level: Geschätzte Komplexitätsstufe
        requires_oracle: Ob externe Wissensquellen benötigt werden
        estimated_time: Geschätzte Ausführungszeit in Sekunden
        confidence: Konfidenz der Analyse (0.0-1.0)
        reasoning: Begründung für die Analyse
        recommended_provers: Liste empfohlener Prover in Prioritätsreihenfolge
    """
    query_type: QueryType
    complexity_level: ComplexityLevel
    requires_oracle: bool
    estimated_time: float
    confidence: float
    reasoning: str
    recommended_provers: List[str]
