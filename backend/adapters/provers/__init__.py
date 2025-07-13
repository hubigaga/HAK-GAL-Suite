# -*- coding: utf-8 -*-
"""
Prover-Implementierungen für verschiedene Beweisstrategien
"""

try:
    from .functional_constraint import FunctionalConstraintProver
    from .pattern import PatternProver
    from .z3_adapter import Z3Adapter
    from .wolfram import WolframProver
except ImportError:
    from backend.adapters.provers.functional_constraint import FunctionalConstraintProver
    from backend.adapters.provers.pattern import PatternProver
    from backend.adapters.provers.z3_adapter import Z3Adapter
    from backend.adapters.provers.wolfram import WolframProver

__all__ = [
    'FunctionalConstraintProver',
    'PatternProver',
    'Z3Adapter',
    'WolframProver'
]
