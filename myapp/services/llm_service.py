from typing import List, Tuple
from django.conf import settings
from django.core.cache import cache
import hashlib
import json
from ..models import DocumentChunk

from langchain.chat_models import init_chat_model
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableConfig
import os
from dotenv import load_dotenv
load_dotenv()


class LLMService:
    def __init__(self):
        # Initialize Gemini model via LangChain
        self.llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai",api_key=os.environ.get("GOOGLE_API_KEY"))
          
        self.max_tokens = 1000
        self.temperature = 0.1

    def generate_answer(self, question: str, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> dict:
        """Generate answer using Gemini with retrieved context"""
        
        # Check cache first
        cache_key = self._generate_cache_key(question, relevant_chunks)
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        # Prepare context from retrieved chunks
        context = self._prepare_context(relevant_chunks)

        # Define the prompt
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template = (
                "You are a precise and reliable assistant. "
                "Answer the user's question strictly based on the provided context and also explain your answer. "
                "Do not include any information that is not in the context. "
                "If the answer cannot be found, say: 'I cannot find this information in the provided context.'\n\n"
                "Avoid speculation.\n\n"
                "Context:\n{context}\n\n"
                "Question:\n{question}\n\n"
                "Answer:"
            )

        )

        chain = LLMChain(llm=self.llm, prompt=prompt_template)

        try:
            # Run the chain
            answer = chain.run({"context": context, "question": question}).strip()

            # Prepare sources
            sources = self._prepare_sources(relevant_chunks)

            result = {
                "answer": answer,
                "sources": sources,
                # "confidence": self._calculate_confidence(relevant_chunks)
            }

            # Cache the response for 1 hour
            cache.set(cache_key, result, 3600)

            return result

        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": []
                #"confidence": 0.0
            }

    
    def _prepare_context(self, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> str:
        """Prepare context string from retrieved chunks"""
        context_parts = []
        for i, (chunk, score) in enumerate(relevant_chunks, 1):
            context_parts.append(f"Context {i}:\n{chunk.content}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create the prompt for the LLM"""
        return f"""Based on the following context, please answer the question. Only use information from the provided context.

Context:
{context}

Question: {question}

Answer:"""
    
    def _prepare_sources(self, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> List[str]:
        """Prepare source citations with page numbers"""
        sources = []
        for chunk, score in relevant_chunks:
            if chunk.page_number:
                source = f"{chunk.document.title} - Page {chunk.page_number}"
            else:
                source = f"{chunk.document.title}"
            sources.append(source)
        
        return list(set(sources))  # Remove duplicates    
    
    # def _calculate_confidence(self, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> float:
    #     """Calculate confidence score based on retrieval scores"""
    #     if not relevant_chunks:
    #         return 0.0
        
    #     # Average of top chunk scores
    #     scores = [score for _, score in relevant_chunks]
    #     return sum(scores) / len(scores)
    
    def _generate_cache_key(self, question: str, relevant_chunks: List[Tuple[DocumentChunk, float]]) -> str:
        """Generate cache key for the query"""
        chunk_ids = [str(chunk.id) for chunk, _ in relevant_chunks]
        cache_data = {
            "question": question,
            "chunk_ids": sorted(chunk_ids)
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
