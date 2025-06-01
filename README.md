# Project Overview

This project is a knowledge assistant system built with Django REST Framework. It allows users to upload documents, process them, and ask questions based on the uploaded knowledge base. The system retrieves relevant information from documents and generates answers using a large language model (LLM).

---

# Architecture

The architecture consists of several key components:

- **Server Distribution & Query Logging**: Incoming queries are distributed and logged for tracking and analysis.
- **Storage Layer**:
  - **Redis Cache**: Used for caching frequently accessed data.
  - **SQLite Database**: Stores documents, query logs, and chunk metadata.
  - **Vector Database (FAISS Index)**: Stores vector embeddings of document chunks for similarity search.
- **REST API**:
  - **Question Answering API**: Handles user questions and returns answers.
  - **User Interface Layer**: Manages user interactions.
  - **Token Authentication**: Secures API endpoints.
- **Document Processing Pipeline**:
  - Supports multiple document types: PDF, DOCX, Markdown, and Text.
  - Processes documents to extract text, split into chunks, and store metadata.
- **Query Processing**:
  - Processes user queries to retrieve relevant document chunks.
  - Prepares context and generates answers using the LLM.
- **Retrieval & Ranking**:
  - Generates embeddings for queries.
  - Performs similarity search on vector database.
  - Retrieves top relevant chunks for answer generation.

---

# API Documentation

Postman collection is attached 
---

## Endpoints

### 1. GET `/index`

- **Description**: Home endpoint to verify the service is running.
- **Request**: No parameters.
- **Response**:
  ```json
  {
    "message": "Welcome to the home page!"
  }
  ```

---

### 2. Document Management: `/doc`

#### GET `/doc`

- **Description**: List all documents uploaded by the authenticated user.
- **Authentication**: Required.
- **Response**: Array of document objects.
  ```json
  [
    {
      "id": 1,
      "title": "Sample Document",
      "document_type": "pdf",
      "uploaded_at": "2024-01-01T12:00:00Z",
      "processed": true,
      "total_chunks": 10
    },
    ...
  ]
  ```

#### POST `/doc`

- **Description**: Upload and process a new document.
- **Authentication**: Required.
- **Request**: Multipart form-data with a file field.
  - Allowed file types: `.pdf`, `.docx`, `.md`, `.txt`
  - Max file size: 100MB
- **Response (Success)**:
  ```json
  {
    "id": 2,
    "title": "New Document",
    "document_type": "docx",
    "uploaded_at": "2024-01-02T15:30:00Z",
    "processed": true,
    "total_chunks": 15,
    "message": "Document 'New Document' uploaded and processed successfully"
  }
  ```
- **Response (Error)**:
  ```json
  {
    "error": "No file provided"
  }
  ```
  or
  ```json
  {
    "error": "Failed to process document"
  }
  ```

---

### 3. Knowledge Assistant: `/bot`

#### POST `/bot`

- **Description**: Ask a question to the knowledge assistant.
- **Authentication**: Required.
- **Request Body**:
  ```json
  {
    "question": "What is the capital of France?"
  }
  ```
- **Response (Success)**:
  ```json
  {
    "answer": "The capital of France is Paris.",
    "sources": ["Document1.pdf", "Document2.docx"],
    "confidence": 0.95,
    "response_time": 1.23
  }
  ```
- **Response (No relevant info)**:
  ```json
  {
    "answer": "I couldn't find any relevant information in the knowledge base to answer your question.",
    "sources": [],
    "response_time": 0.75
  }
  ```
- **Response (Error)**:
  ```json
  {
    "error": "Internal server error: <error message>"
  }
  ```

#### GET `/bot`

- **Description**: Retrieve the authenticated user's last 20 query history entries.
- **Authentication**: Required.
- **Response**:
  ```json
  [
    {
      "id": 1,
      "question": "What is AI?",
      "answer": "AI stands for Artificial Intelligence...",
      "sources": ["Doc1.pdf"],
      "response_time": 1.5,
      "created_at": "2024-01-01T12:00:00Z"
    },
    ...
  ]
  ```

---

# Technologies Used

- Django REST Framework for API development
- Redis for caching
- SQLite for relational data storage
- FAISS for vector similarity search
- Large Language Model (LLM) for answer generation
- Document processing for PDF, DOCX, Markdown, and Text files

---

# Notes


- Document processing is yet to be done asynchronously after upload.
- Query logs are stored for user history and analytics.
