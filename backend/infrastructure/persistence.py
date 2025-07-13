# -*- coding: utf-8 -*-
"""
Persistenz-Verwaltung für die Wissensbasis
"""

import pickle
import os
from typing import Dict, Any, List


class KnowledgeBasePersistence:
    """
    Verwaltet das Speichern und Laden der Wissensbasis.
    Verwendet Pickle für die Serialisierung.
    """
    
    @staticmethod
    def save(filepath: str, data: Dict[str, Any]) -> bool:
        """
        Speichert die Wissensbasis in eine Datei.
        
        Args:
            filepath: Pfad zur Ausgabedatei
            data: Dictionary mit zu speichernden Daten
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            print(f"✅ Wissensbasis in '{filepath}' gespeichert.")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern: {e}")
            return False
    
    @staticmethod
    def load(filepath: str) -> Dict[str, Any]:
        """
        Lädt die Wissensbasis aus einer Datei.
        
        Args:
            filepath: Pfad zur Eingabedatei
            
        Returns:
            Dictionary mit geladenen Daten oder leeres Dict bei Fehler
        """
        if not os.path.exists(filepath):
            return {}
        
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            # Validierung der geladenen Daten
            required_keys = ['facts']
            if not all(key in data for key in required_keys):
                print("⚠️ Unvollständige KB-Datei, verwende Standardwerte")
                return {}
            
            fact_count = len(data.get('facts', []))
            cache_count = len(data.get('proof_cache', {}))
            print(f"✅ {fact_count} Kernregeln und {cache_count} gecachte Beweise geladen.")
            
            return data
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der KB: {e}")
            return {}
    
    @staticmethod
    def migrate_old_format(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migriert alte KB-Formate zum aktuellen Format.
        
        Args:
            data: Daten im alten Format
            
        Returns:
            Daten im neuen Format
        """
        # Migration von RAG-Daten wenn nötig
        if 'rag_data' in data and data['rag_data']:
            rag_chunks = data['rag_data'].get('chunks', [])
            if rag_chunks and isinstance(rag_chunks[0], tuple):
                print("   [Migration] Altes KB-Format erkannt. Konvertiere...")
                converted_chunks = []
                for chunk_tuple in rag_chunks:
                    if len(chunk_tuple) == 2:
                        converted_chunks.append({
                            'text': chunk_tuple[0],
                            'source': chunk_tuple[1]
                        })
                data['rag_data']['chunks'] = converted_chunks
        
        return data
