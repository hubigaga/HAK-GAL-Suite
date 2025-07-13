# -*- coding: utf-8 -*-
"""
Services Layer - Geschäftslogik und Manager-Klassen
"""

try:
    # Relative imports (wenn als Paket geladen)
    from backend.services.complexity_analyzer import ComplexityAnalyzer
    from .prover_portfolio_manager import ProverPortfolioManager
    from backend.services.ensemble_manager import EnsembleManager
    from backend.services.wissensbasis_manager import WissensbasisManager
    from .k_assistant import KAssistant
except ImportError:
    # Absolute imports (Fallback)
    from backend.services.complexity_analyzer import ComplexityAnalyzer
    from backend.services.prover_portfolio_manager import ProverPortfolioManager
    from backend.services.ensemble_manager import EnsembleManager
    from backend.services.wissensbasis_manager import WissensbasisManager
    from backend.services.k_assistant import KAssistant

__all__ = [
    'ComplexityAnalyzer',
    'ProverPortfolioManager',
    'EnsembleManager',
    'WissensbasisManager',
    'KAssistant'
]
