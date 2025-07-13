# -*- coding: utf-8 -*-
#
# DATEI: dynamic_belief_revision_module.py
# PROJEKT: HAK-GAL / ArchonOS
# ZUSTANDSSYNTHESE: 12.07.2025
# VERSION: 1.0
#
# BESCHREIBUNG:
# Implementiert das DynamicBeliefRevisionModule für rationale Wissensaktualisierung
# nach AGM-Theorie. Verwaltet eine Wissensbasis und führt Revisionen durch, die
# Konsistenzprüfungen und Governance-Entscheidungen berücksichtigen.

import asyncio
from typing import Set, Optional
from dataclasses import dataclass
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Belief:
    fact: str
    source: str
    entrenchment: float
    timestamp: float

class DynamicBeliefRevisionModule:
    """Modul für dynamische Wissensrevision nach AGM-Theorie"""
    
    def __init__(self, governance_engine):
        self.governance_engine = governance_engine
        self.knowledge_base = set()  # Initialize knowledge base as a set
        logger.info("DynamicBeliefRevisionModule initialisiert")

    async def revise(self, new_belief: Belief) -> Set[Belief]:
        """
        Führt eine Revision der Wissensbasis durch basierend auf einer neuen Überzeugung.
        Implementiert die Levi-Identität: K * p = (K ~ ¬p) + p
        """
        logger.info(f"Revidiere Wissensbasis mit neuer Überzeugung: {new_belief.fact}")
        
        # Step 1: Check consistency with governance engine
        facts = {belief.fact for belief in self.knowledge_base} | {new_belief.fact}
        is_consistent, inconsistent_set = await self.governance_engine.check_consistency(facts)
        
        if is_consistent:
            # Simple expansion: add the new belief
            self.knowledge_base.add(new_belief)
            logger.info(f"Einfache Expansion: {new_belief.fact} hinzugefügt")
            return self.knowledge_base
        
        # Step 2: Contraction (remove conflicting beliefs with lower entrenchment)
        conflicting_beliefs = {b for b in self.knowledge_base if b.fact in inconsistent_set}
        if not conflicting_beliefs:
            self.knowledge_base.add(new_belief)
            logger.info(f"Keine Konflikte gefunden, {new_belief.fact} hinzugefügt")
            return self.knowledge_base
        
        # Remove belief with lowest entrenchment if new belief has higher entrenchment
        min_entrenchment = min(b.entrenchment for b in conflicting_beliefs)
        if new_belief.entrenchment > min_entrenchment:
            beliefs_to_remove = {b for b in conflicting_beliefs if b.entrenchment == min_entrenchment}
            self.knowledge_base.difference_update(beliefs_to_remove)
            self.knowledge_base.add(new_belief)
            logger.info(f"Kontraktion: Entfernt {len(beliefs_to_remove)} Überzeugungen, {new_belief.fact} hinzugefügt")
        else:
            logger.info(f"Neue Überzeugung {new_belief.fact} hat zu niedrige Verankerung, wird verworfen")
        
        return self.knowledge_base