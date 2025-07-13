# -*- coding: utf-8 -*-
"""
Wissensbasis Manager - RAG (Retrieval-Augmented Generation) Funktionalität
"""

import os
from typing import List, Dict, Optional, Any

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    from pypdf import PdfReader
    RAG_ENABLED = True
except ImportError:
    RAG_ENABLED = False
    SentenceTransformer = None
    np = None
    faiss = None
    PdfReader = None


class WissensbasisManager:
    """
    Verwaltet die Wissensbasis mit RAG-Funktionalität.
    Unterstützt Dokumenten-Indizierung und semantische Suche.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialisiert den Wissensbasis-Manager.
        
        Args:
            model_name: Name des Sentence-Transformer Modells
        """
        if not RAG_ENABLED:
            self.model = None
            self.index = None
            self.chunks: List[Dict[str, str]] = []
            self.doc_paths: Dict[str, str] = {}
            print("   ℹ️  RAG-Funktionen deaktiviert.")
            return
        
        # Initialisiere Sentence Transformer
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialisiere FAISS Index
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Speicher für Chunks und Dokument-Pfade
        self.chunks: List[Dict[str, str]] = []
        self.doc_paths: Dict[str, str] = {}
    
    def add_document(self, file_path: str) -> bool:
        """
        Fügt ein Dokument zur Wissensbasis hinzu.
        
        Args:
            file_path: Pfad zum Dokument
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not RAG_ENABLED:
            return False
        
        doc_id = os.path.basename(file_path)
        
        # Prüfe ob bereits indiziert
        if doc_id in self.doc_paths:
            print(f"   ℹ️ '{file_path}' bereits indiziert.")
            return False
        
        try:
            # Lese Dokument
            if file_path.endswith(".pdf"):
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
        except Exception as e:
            print(f"   ❌ Fehler beim Lesen von '{file_path}': {e}")
            return False
        
        # Teile Text in Chunks
        text_chunks = [
            chunk.strip()
            for chunk in text.split('\n\n')
            if len(chunk.strip()) > 30
        ]
        
        if not text_chunks:
            print(f"   ℹ️ Keine Chunks in '{file_path}' gefunden.")
            return False
        
        # Erstelle Embeddings
        embeddings = self.model.encode(
            text_chunks,
            convert_to_tensor=False,
            show_progress_bar=True
        )
        
        # Füge zu Index hinzu
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Speichere Chunks mit Metadaten
        for chunk in text_chunks:
            self.chunks.append({
                'text': chunk,
                'source': doc_id
            })
        
        # Speichere Dokument-Pfad
        self.doc_paths[doc_id] = file_path
        
        print(f"   ✅ {len(text_chunks)} Chunks aus '{doc_id}' indiziert.")
        return True
    
    def retrieve_relevant_chunks(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        """
        Findet relevante Chunks für eine Anfrage.
        
        Args:
            query: Die Suchanfrage
            k: Anzahl der zu returnierenden Chunks
            
        Returns:
            Liste der relevantesten Chunks mit Metadaten
        """
        if not RAG_ENABLED or self.index.ntotal == 0:
            return []
        
        # Erstelle Query-Embedding
        query_embedding = self.model.encode([query])
        
        # Suche ähnliche Chunks
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            k
        )
        
        # Sammle Ergebnisse
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.chunks):
                results.append(self.chunks[i])
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über die Wissensbasis zurück.
        
        Returns:
            Dictionary mit Statistiken
        """
        if not RAG_ENABLED:
            return {
                'enabled': False,
                'doc_count': 0,
                'chunk_count': 0
            }
        
        return {
            'enabled': True,
            'doc_count': len(self.doc_paths),
            'chunk_count': self.index.ntotal if self.index else 0,
            'embedding_dimension': self.dimension if self.model else 0
        }
    
    def get_indexed_documents(self) -> Dict[str, str]:
        """
        Gibt alle indizierten Dokumente zurück.
        
        Returns:
            Dictionary mit Dokument-IDs und Pfaden
        """
        return self.doc_paths.copy()
    
    def clear(self):
        """Leert die gesamte Wissensbasis."""
        if RAG_ENABLED and self.index:
            # Neuer Index
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.chunks.clear()
        self.doc_paths.clear()
        print("   [RAG] Wissensbasis geleert.")
    
    def rebuild_index_from_chunks(self, chunks: List[Dict[str, str]]):
        """
        Baut den Index aus geladenen Chunks neu auf.
        
        Args:
            chunks: Liste von Chunk-Dictionaries
        """
        if not RAG_ENABLED or not chunks:
            return
        
        self.chunks = chunks
        
        # Extrahiere nur die Texte
        texts = [chunk['text'] for chunk in chunks]
        
        # Erstelle Embeddings
        embeddings = self.model.encode(
            texts,
            convert_to_tensor=False,
            show_progress_bar=False
        )
        
        # Füge zum Index hinzu
        self.index.add(np.array(embeddings).astype('float32'))
        
        print(f"   [RAG] Index mit {len(chunks)} Chunks neu aufgebaut.")
