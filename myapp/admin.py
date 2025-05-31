from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Document, DocumentChunk, QueryLog

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'uploaded_by', 'uploaded_at', 'processed', 'total_chunks']
    list_filter = ['document_type', 'processed', 'uploaded_at']
    search_fields = ['title', 'uploaded_by__username']
    readonly_fields = ['id', 'uploaded_at', 'processed', 'total_chunks']

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'page_number', 'embedding_stored']
    list_filter = ['embedding_stored', 'document']
    search_fields = ['content', 'document__title']

@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'question_preview', 'response_time', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['question', 'answer']
    readonly_fields = ['id', 'created_at']
    
    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = "Question"