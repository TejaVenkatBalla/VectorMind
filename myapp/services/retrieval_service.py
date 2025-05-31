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
    
    def retrieve_relevant_chunks(self, question: str, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        """Retrieve most relevant chunks for a given question"""
        # Generate question embedding
        question_embedding = self.embedding_model.encode([question])
        faiss.normalize_L2(question_embedding)
        
        all_results = []
        
        # Search across all processed documents
        processed_docs = Document.objects.filter(processed=True)
        
        for document in processed_docs:
            index_path = os.path.join(settings.VECTOR_DB_PATH, f'index_{document.id}.faiss')
            metadata_path = os.path.join(settings.VECTOR_DB_PATH, f'metadata_{document.id}.pkl')
            
            if not os.path.exists(index_path) or not os.path.exists(metadata_path):
                continue
            
            # Load FAISS index and metadata
            index = faiss.read_index(index_path)
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Search
            scores, indices = index.search(question_embedding.astype('float32'), min(top_k, index.ntotal))
            
            # Get corresponding chunks
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0:  # Valid index
                    chunk_id = metadata['chunk_ids'][idx]
                    try:
                        chunk = DocumentChunk.objects.get(id=chunk_id)
                        all_results.append((chunk, float(score)))
                    except DocumentChunk.DoesNotExist:
                        continue
        
        # Sort by score and return top_k
        all_results.sort(key=lambda x: x[1], reverse=True)
        print(all_results)
        return all_results[:top_k]