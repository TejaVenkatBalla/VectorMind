from celery import shared_task
from .services.document_processor import DocumentProcessor
from .models import Document

@shared_task
def process_document_task(document_id):
    try:
        document = Document.objects.get(id=document_id)
        processor = DocumentProcessor()
        success = processor.process_document(document)
        return success
    except Document.DoesNotExist:
        return False
