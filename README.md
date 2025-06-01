# Project Overview

This project is a knowledge assistant system built with Django REST Framework. It allows users to upload documents, process them, and ask questions based on the uploaded knowledge base.

---

## Architecture

The architecture consists of several key components:

- **Server Distribution & Query Logging**
- **Storage Layer** (Redis Cache, SQLite Database, Vector Database with FAISS)
- **REST API** with Question Answering and User Interface layers
- **Document Processing Pipeline** supporting PDF, DOCX, Markdown, and Text files
- **Query Processing and Retrieval** with embedding-based similarity search
- **Answer Generation** using a Large Language Model (LLM)

---

## Project Setup

### Prerequisites

- Python 3.8+
- Redis server running locally or accessible remotely

### Installation

1. **Clone the repository**

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Add Django secret key (Optional)
   - Add `REDIS_URL`
   - Add `GOOGLE_API_KEY`

5. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `auth/token/` | Obtain a token for authentication |
| GET | `api/index/` | Home endpoint |
| GET, POST | `api/doc/` | List and upload documents |
| GET, POST | `api/bot/` | Query knowledge assistant and get query history |

## API Documentation

Please refer to the Postman collection attached in the repository.