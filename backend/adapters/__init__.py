# -*- coding: utf-8 -*-
"""
Adapters Layer - Externe Integrationen und konkrete Implementierungen
"""

try:
    # LLM Providers
    from .llm_providers import (
        DeepSeekProvider,
        MistralProvider,
        GeminiProvider
    )
    
    # Prover Implementations - re-export from subpackage
    from .provers import (
        FunctionalConstraintProver,
        PatternProver,
        Z3Adapter,
        WolframProver
    )
except ImportError:
    # Fallback auf absolute Imports
    from backend.adapters.llm_providers import (
        DeepSeekProvider,
        MistralProvider,
        GeminiProvider
    )
    
    from backend.adapters.provers import (
        FunctionalConstraintProver,
        PatternProver,
        Z3Adapter,
        WolframProver
    )

__all__ = [
    # LLM Providers
    'DeepSeekProvider',
    'MistralProvider',
    'GeminiProvider',
    
    # Provers
    'FunctionalConstraintProver',
    'PatternProver',
    'Z3Adapter',
    'WolframProver'
]
