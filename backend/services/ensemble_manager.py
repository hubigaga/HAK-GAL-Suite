# -*- coding: utf-8 -*-
"""
Ensemble Manager - Verwaltet mehrere LLM-Provider
"""

import os
import re
import json
import threading
from typing import List, Optional, Dict, Any
from collections import Counter

from backend.api import BaseLLMProvider
from backend.infrastructure import PromptCache
from backend.adapters import DeepSeekProvider, MistralProvider, GeminiProvider


class EnsembleManager:
    """
    Verwaltet ein Ensemble von LLM-Providern für robuste Antworten.
    Implementiert Voting-Mechanismen und Fallback-Strategien.
    """
    
    def __init__(self):
        """Initialisiert das Ensemble mit verfügbaren Providern."""
        self.providers: List[BaseLLMProvider] = []
        self._initialize_providers()
        self.prompt_cache = PromptCache()
        
        # System-Prompts
        self.system_prompt_logicalize = """
        You are a hyper-precise, non-conversational logic translator. Your ONLY function is to translate user input into a single HAK/GAL first-order logic formula. You MUST adhere to these rules without exception.

        **HAK/GAL SYNTAX RULES:**
        1.  **Structure:** `Predicate(Argument).` or `all x (...)`.
        2.  **Predicates & Constants:** `PascalCase`. Examples: `IstUrgent`, `UserManagement`.
        3.  **Variables:** `lowercase`. Example: `x`.
        4.  **Operators:** `&` (AND), `|` (OR), `->` (IMPLIES), `-` (NOT).
        5.  **Termination:** Every formula MUST end with a period `.`.
        6.  **NO CONVERSATION:** Do not ask for clarification. Do not explain yourself. Do not add any text before or after the formula. Your response must contain ONLY the formula.
        7.  **VAGUE INPUT RULE:** If the user input is short, vague, or a single word (like "system", "test", "help"), translate it to a generic query about its properties.
            - "system" -> `Eigenschaften(System).`
            - "hakgal" -> `Eigenschaften(HAKGAL).`
            - "test" -> `IstTest().`
        8.  **IDEMPOTENCY:** If the input is already a valid formula, return it UNCHANGED. `IstKritisch(X).` -> `IstKritisch(X).`

        **Translate the following sentence into a single HAK/GAL formula and nothing else:**
        """
        
        self.fact_extraction_prompt = """
        You are a precise logic extractor. Your task is to extract all facts and rules from the provided text and format them as a Python list of strings. Each string must be a valid HAK/GAL first-order logic formula.

        **HAK/GAL SYNTAX RULES (MUST BE FOLLOWED EXACTLY):**
        1.  **Structure:** `Predicate(Argument).` or `all x (Rule(x)).`
        2.  **Predicates & Constants:** `PascalCase`. (e.g., `IstLegacy`, `UserManagement`)
        3.  **Variables:** Lowercase. (e.g., `x`)
        4.  **Quantifiers:** Rules with variables MUST use `all x (...)`.
        5.  **Operators:** `&` (AND), `|` (OR), `->` (IMPLIES), `-` (NOT).
        6.  **Termination:** Every formula MUST end with a period `.`.
        7.  **Output Format:** A single Python list of strings, and nothing else.

        **Example Extraction:**
        - Text: "The billing system is a legacy system. All legacy systems are critical."
        - Output: `["IstLegacySystem(BillingSystem).", "all x (IstLegacySystem(x) -> IstKritisch(x))."]`

        - Text: "The server is not responding."
        - Output: `["-IstErreichbar(Server)."]`

        **Text to analyze:**
        {context}

        **Output (Python list of strings only):**
        """
    
    def _initialize_providers(self):
        """Initialisiert verfügbare LLM-Provider aus Umgebungsvariablen."""
        print("🤖 Initialisiere LLM-Provider-Ensemble...")
        
        # DeepSeek
        if api_key := os.getenv("DEEPSEEK_API_KEY"):
            try:
                self.providers.append(DeepSeekProvider(api_key=api_key))
                print("   ✅ DeepSeek")
            except Exception as e:
                print(f"   ❌ DeepSeek: {e}")
        
        # Mistral
        if api_key := os.getenv("MISTRAL_API_KEY"):
            try:
                self.providers.append(MistralProvider(api_key=api_key))
                print("   ✅ Mistral")
            except Exception as e:
                print(f"   ❌ Mistral: {e}")
        
        # Gemini
        if api_key := os.getenv("GEMINI_API_KEY"):
            try:
                self.providers.append(GeminiProvider(api_key=api_key))
                print("   ✅ Gemini")
            except Exception as e:
                print(f"   ❌ Gemini: {e}")
        
        if not self.providers:
            print("   ⚠️ Keine LLM-Provider aktiv.")
    
    def logicalize(self, sentence: str) -> Optional[str]:
        """
        Übersetzt eine natürlichsprachliche Anfrage in HAK-GAL Logik.
        
        Args:
            sentence: Die zu übersetzende Anfrage
            
        Returns:
            HAK-GAL Formel oder None bei Fehler
        """
        if not self.providers:
            return None
        
        full_prompt = f"{self.system_prompt_logicalize}\n\n{sentence}"
        
        # Cache-Lookup
        if cached_response := self.prompt_cache.get(full_prompt):
            print("   [Cache] ✅ Treffer im Prompt-Cache!")
            try:
                return json.loads(cached_response)
            except json.JSONDecodeError:
                return cached_response
        
        try:
            # Verwende ersten verfügbaren Provider
            response_text = self.providers[0].query(
                sentence,
                self.system_prompt_logicalize,
                0
            )
            
            # Cache speichern
            self.prompt_cache.put(full_prompt, response_text)
            
            # Versuche JSON zu parsen
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return response_text
                
        except Exception as e:
            print(f"   [Warnung] Logik-Übersetzung: {e}")
            return None
    
    def extract_facts_with_ensemble(self, context: str) -> List[str]:
        """
        Extrahiert Fakten aus Text mit Ensemble-Voting.
        
        Args:
            context: Der zu analysierende Text
            
        Returns:
            Liste von extrahierten HAK-GAL Fakten
        """
        if not self.providers:
            return []
        
        results: List[Optional[List[str]]] = [None] * len(self.providers)
        
        def worker(provider: BaseLLMProvider, index: int):
            """Worker-Funktion für parallele Ausführung."""
            try:
                prompt = self.fact_extraction_prompt.format(context=context)
                raw_output = provider.query(prompt, "", 0.1)
                
                # Extrahiere Python-Liste aus Antwort
                if match := re.search(r'\[.*\]', raw_output, re.DOTALL):
                    try:
                        fact_list = eval(match.group(0))
                        if isinstance(fact_list, list):
                            # Duplikate entfernen
                            results[index] = list(dict.fromkeys(fact_list))
                    except:
                        pass
            except Exception as e:
                print(f"   [Warnung] {provider.model_name}: {e}")
        
        # Parallele Ausführung
        threads = [
            threading.Thread(target=worker, args=(p, i))
            for i, p in enumerate(self.providers)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Mistral-Veto Mechanismus
        mistral_result = next((
            results[i] for i, p in enumerate(self.providers)
            if isinstance(p, MistralProvider) and results[i]
        ), None)
        
        if mistral_result:
            print(f"   [Ensemble] ✅ Mistral-Veto: {len(mistral_result)} Fakten.")
            return mistral_result
        
        # Fallback: Mehrheitsentscheid
        other_results = [
            res for i, res in enumerate(results)
            if res and not isinstance(self.providers[i], MistralProvider)
        ]
        
        if not other_results:
            return []
        
        print("   [Ensemble] ⚠️ Fallback auf Mehrheitsentscheid...")
        
        # Zähle Vorkommen jedes Fakts
        fact_counts = Counter(
            fact for res in other_results for fact in res
        )
        
        # Schwellwert für Konsens
        threshold = len(other_results) // 2 + 1 if len(other_results) > 1 else 1
        
        # Fakten die den Schwellwert erreichen
        consistent_facts = [
            fact for fact, count in fact_counts.items()
            if count >= threshold
        ]
        
        if consistent_facts:
            print(f"   [Ensemble] Konsens für {len(consistent_facts)} Fakten.")
        
        return consistent_facts
    
    def get_providers_status(self) -> Dict[str, bool]:
        """
        Gibt den Status der Provider zurück.
        
        Returns:
            Dictionary mit Provider-Namen und deren Verfügbarkeit
        """
        return {
            provider.__class__.__name__: True
            for provider in self.providers
        }
