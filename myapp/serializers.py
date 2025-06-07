from rest_framework import serializers
from .models import Document, QueryLog
import os
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Create a new user instance
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['file']  # Only file field required
    
    def validate_file(self, value):
        # Validate file size (max 10MB)
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 100MB")
        
        # Validate file extension
        allowed_extensions = ['.pdf', '.docx', '.md', '.txt']
        file_extension = os.path.splitext(value.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value
    
    def create(self, validated_data):
        file = validated_data['file']
        
        # Extract title from filename (remove extension)
        filename = file.name
        title = os.path.splitext(filename)[0]
        
        # Extract document type from file extension
        file_extension = os.path.splitext(filename)[1].lower()
        document_type_mapping = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.md': 'md',
            '.txt': 'txt'
        }
        document_type = document_type_mapping.get(file_extension, 'txt')
        
        # Create document with extracted information
        document = Document.objects.create(
            title=title,
            file=file,
            document_type=document_type,
            uploaded_by=self.context['request'].user
        )
        
        return document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'uploaded_at', 'processed', 'total_chunks']

class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)
    
class QueryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryLog
        fields = ['id', 'question', 'answer', 'sources', 'response_time', 'created_at']
