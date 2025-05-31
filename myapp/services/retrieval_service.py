import faiss
import pickle
import os
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from django.conf import settings
from ..models import Document, DocumentChunk

class RetrievalService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.2  # Minimum similarity score to consider relevant

        # Load single FAISS index and metadata
        index_path = os.path.join(settings.VECTOR_DB_PATH, 'index.faiss')
        metadata_path = os.path.join(settings.VECTOR_DB_PATH, 'metadata.pkl')

        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        else:
            self.index = None

        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.metadata = {'chunk_ids': [], 'document_ids': []}

    def retrieve_relevant_chunks(self, question: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Retrieve most relevant chunks for a given question"""
        if self.index is None or not self.metadata['chunk_ids']:
            return []

        # Generate question embedding
        question_embedding = self.embedding_model.encode([question])
        faiss.normalize_L2(question_embedding)

        # Search
        scores, indices = self.index.search(question_embedding.astype('float32'), min(top_k, self.index.ntotal))

        all_results = []

        # Get corresponding chunks
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and score >= self.similarity_threshold:  # Only include if above threshold
                chunk_id = self.metadata['chunk_ids'][idx]
                try:
                    chunk = DocumentChunk.objects.get(id=chunk_id)
                    all_results.append((chunk, float(score)))
                except DocumentChunk.DoesNotExist:
                    continue

        # Sort by score and return top_k
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:top_k]
