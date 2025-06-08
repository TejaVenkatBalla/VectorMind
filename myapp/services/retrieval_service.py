import faiss
import pickle
import os
import numpy as np
from typing import List, Tuple
#from sentence_transformers import SentenceTransformer
from django.conf import settings
from ..models import Document, DocumentChunk
from langchain_google_genai import GoogleGenerativeAIEmbeddings
class RetrievalService:
    def __init__(self):
        
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
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
            self.metadata = {'chunk_ids': [], 'document_ids': [], 'user_ids': []}

    def retrieve_relevant_chunks(self, question: str, user_id: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Retrieve most relevant chunks for a given question and user_id"""
        if self.index is None or not self.metadata['chunk_ids']:
            return []

        # Generate question embedding
        #question_embedding = self.embedding_model.encode([question])
        question_embedding_list = self.embedding_model.embed_query(question)

        # Convert to numpy array and reshape for FAISS (needs 2D array)
        question_embedding = np.array([question_embedding_list], dtype=np.float32)

        faiss.normalize_L2(question_embedding)

        # Search
        scores, indices = self.index.search(question_embedding.astype('float32'), min(top_k, self.index.ntotal))

        all_results = []

        # Get corresponding chunks filtered by user_id
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and score >= self.similarity_threshold:
                if self.metadata['user_ids'][idx] == user_id:
                    chunk_id = self.metadata['chunk_ids'][idx]
                    try:
                        chunk = DocumentChunk.objects.get(id=chunk_id)
                        all_results.append((chunk, float(score)))
                    except DocumentChunk.DoesNotExist:
                        continue

        # Sort by score and return top_k
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:top_k]
