from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def home(request):
    if request.method == 'GET':
        
        return Response({"message": "Welcome to the home page!"})



from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import time
from .models import Document, QueryLog
from .serializers import (
    DocumentUploadSerializer, 
    DocumentSerializer, 
    QuestionSerializer, 
    AnswerSerializer,
    QueryLogSerializer
)
from .services.document_processor import DocumentProcessor
from .services.retrieval_service import RetrievalService
from .services.llm_service import LLMService

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(uploaded_by=self.request.user)
    
    def create(self, request):
        """Upload and process a new document - only requires file"""
        if 'file' not in request.FILES:
            return Response(
                {"error": "No file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Pass request context to serializer for user access
        serializer = DocumentUploadSerializer(
            data={'file': request.FILES['file']}, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            document = serializer.save()
            
            # Process document asynchronously (you can use Celery for this)
            processor = DocumentProcessor()
            success = processor.process_document(document)
            
            if success:
                response_data = DocumentSerializer(document).data
                response_data['message'] = f"Document '{document.title}' uploaded and processed successfully"
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                # Clean up if processing failed
                document.delete()
                return Response(
                    {"error": "Failed to process document"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a document"""
        document = self.get_object()
        processor = DocumentProcessor()
        success = processor.process_document(document)
        
        if success:
            return Response({"message": "Document reprocessed successfully"})
        else:
            return Response(
                {"error": "Failed to reprocess document"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class KnowledgeAssistantViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def ask_question(self, request):
        """Main endpoint for asking questions"""
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question = serializer.validated_data['question']
        start_time = time.time()
        
        try:
            # Retrieve relevant chunks
            retrieval_service = RetrievalService()
            relevant_chunks = retrieval_service.retrieve_relevant_chunks(question)
            
            if not relevant_chunks:
                response_data = {
                    "answer": "I couldn't find any relevant information in the knowledge base to answer your question.",
                    "sources": [],
                    "confidence": 0.0,
                    "response_time": time.time() - start_time
                }
            else:
                # Generate answer using LLM
                llm_service = LLMService()
                response_data = llm_service.generate_answer(question, relevant_chunks)
                response_data["response_time"] = time.time() - start_time
            
            # Log the query
            QueryLog.objects.create(
                user=request.user,
                question=question,
                answer=response_data["answer"],
                sources=response_data["sources"],
                response_time=response_data["response_time"]
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Internal server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def query_history(self, request):
        """Get user's query history"""
        queries = QueryLog.objects.filter(user=request.user)[:20]
        serializer = QueryLogSerializer(queries, many=True)
        return Response(serializer.data)
