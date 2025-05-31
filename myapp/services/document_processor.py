import PyPDF2
import docx
import markdown
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from django.conf import settings
from ..models import Document, DocumentChunk

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = 1000
        self.chunk_overlap = 200
        
    def process_document(self, document: Document) -> bool:
        """Process a document and store its chunks with embeddings"""
        try:
            # Extract text with page numbers based on document type
            if document.document_type == 'pdf':
                pages_text = self._extract_pdf_text(document.file.path)
            elif document.document_type == 'docx':
                pages_text = self._extract_docx_text(document.file.path)
            elif document.document_type == 'md':
                pages_text = self._extract_markdown_text(document.file.path)
            elif document.document_type == 'txt':
                pages_text = self._extract_text_file(document.file.path)
            else:
                raise ValueError(f"Unsupported document type: {document.document_type}")
            
            # Create chunks with page tracking
            chunks_with_pages = self._create_chunks_with_pages(pages_text)
            
            # Store chunks in database
            self._store_chunks_with_pages(document, chunks_with_pages)
            
            # Create and store embeddings
            self._create_embeddings(document)
            
            # Mark document as processed
            document.processed = True
            document.total_chunks = len(chunks_with_pages)
            document.save()
            
            return True
            
        except Exception as e:
            print(f"Error processing document {document.id}: {str(e)}")
            return False
    
    def _extract_pdf_text(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text from PDF file with page numbers"""
        pages_text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    pages_text.append((text, page_num))
        return pages_text
    
    def _extract_docx_text(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text from DOCX file with estimated page numbers"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        # For DOCX, we'll estimate pages (roughly 500 words per page)
        words = text.split()
        words_per_page = 500
        estimated_pages = max(1, len(words) // words_per_page)
        
        return [(text, 1)]  # Return as single page for simplicity, can be enhanced
    
    def _extract_markdown_text(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text from Markdown file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
            html = markdown.markdown(md_content)
            # Simple HTML tag removal
            import re
            text = re.sub('<[^<]+?>', '', html)
            return [(text, 1)]  # Single page for markdown files
    
    def _extract_text_file(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text from plain text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            return [(text, 1)]  # Single page for text files
    
    def _create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, start + self.chunk_size // 2, -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            
        return chunks
    
    def _create_chunks_with_pages(self, pages_text: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """Split text into overlapping chunks while preserving page numbers"""
        chunks_with_pages = []
        
        for page_text, page_num in pages_text:
            # Split current page into chunks
            page_chunks = self._create_chunks(page_text)
            
            # Add page number to each chunk from this page
            for chunk in page_chunks:
                chunks_with_pages.append((chunk, page_num))
        
        return chunks_with_pages
    
    def _store_chunks_with_pages(self, document: Document, chunks_with_pages: List[Tuple[str, int]]):
        """Store chunks with page numbers in database"""
        chunk_objects = []
        for i, (chunk_content, page_num) in enumerate(chunks_with_pages):
            chunk_objects.append(
                DocumentChunk(
                    document=document,
                    content=chunk_content,
                    chunk_index=i,
                    page_number=page_num
                )
            )
        
        DocumentChunk.objects.bulk_create(chunk_objects)
    
    def _create_embeddings(self, document: Document):
        """Create embeddings for document chunks and store in FAISS"""
        chunks = DocumentChunk.objects.filter(document=document)
        texts = [chunk.content for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Create or load FAISS index
        index_path = os.path.join(settings.VECTOR_DB_PATH, f'index_{document.id}.faiss')
        metadata_path = os.path.join(settings.VECTOR_DB_PATH, f'metadata_{document.id}.pkl')
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        # Save index
        faiss.write_index(index, index_path)
        
        # Save metadata (chunk IDs)
        metadata = {
            'chunk_ids': [str(chunk.id) for chunk in chunks],
            'document_id': str(document.id)
        }
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        # Mark chunks as having embeddings stored
        chunks.update(embedding_stored=True)