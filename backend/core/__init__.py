# -*- coding: utf-8 -*-
"""
Core Logic Layer - Domain-Modelle und Geschäftslogik
"""

# Verwende absolute Imports für bessere Kompatibilität
try:
    # Versuche relative Imports (wenn als Paket geladen)
    from .models import QueryType, ComplexityLevel, ComplexityReport
    from .grammar import HAKGAL_GRAMMAR
    from .parser import HAKGALParser
    from .fol_core import HAKGAL_Core_FOL
except ImportError:
    # Fallback auf absolute Imports
    from backend.core.models import QueryType, ComplexityLevel, ComplexityReport
    from backend.core.grammar import HAKGAL_GRAMMAR
    from backend.core.parser import HAKGALParser
    from backend.core.fol_core import HAKGAL_Core_FOL

__all__ = [
    'QueryType',
    'ComplexityLevel', 
    'ComplexityReport',
    'HAKGAL_GRAMMAR',
    'HAKGALParser',
    'HAKGAL_Core_FOL'
]
