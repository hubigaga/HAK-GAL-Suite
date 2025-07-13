# -*- coding: utf-8 -*-
"""
Infrastructure Layer - Datenpersistenz, Caching und externe Ressourcen
"""

try:
    from .caching import ProofCache, PromptCache
    from .persistence import KnowledgeBasePersistence
    from .shell import ShellManager
except ImportError:
    from backend.infrastructure.caching import ProofCache, PromptCache
    from backend.infrastructure.persistence import KnowledgeBasePersistence
    from backend.infrastructure.shell import ShellManager

__all__ = [
    'ProofCache',
    'PromptCache',
    'KnowledgeBasePersistence',
    'ShellManager'
]
