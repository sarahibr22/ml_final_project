
# Backend Setup

## 1. Create a Virtual Environment

Open a terminal in the `backend` directory and run:

```
python -m venv venv
```

Activate the environment:
- **Windows:**
   ```
   venv\Scripts\activate
   ```
- **macOS/Linux:**
   ```
   source venv/bin/activate
   ```

## 2. Install Requirements

```bash
pip install -r requirements.txt
```

## 3. Environment Variables

Set your secrets and config in `.env`:
```
API_KEY=your_api_key_here
DEBUG=True
COHERE_API_KEY=your_cohere_api_key
EMAIL_FROM=your_email@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
```

## 4. Run the Backend

```bash
uvicorn main:app --reload
```

## 5. Tools Overview

- **LLM (Cohere):**
   - `llm/cohere_chat.py`: Call Cohere chat API using `cohere_chat()`.
- **OCR (Tesseract):**
   - `/ocr` endpoint for image upload and OCR using pytesseract.
- **DuckDuckGo Search:**
   - `tools/duckduckgo_tool.py`: Use `duckduckgo_search()` for web search.
- **Email Sending:**
   - `tools/email_tool.py`: Use `send_email()` to send emails via SMTP.
- **Database Queries:**
   - `tools/templated_query_tool.py`: Common SQL queries for patients, prescriptions, medications.

## 6. Docker & Compose

The backend, frontend, database, and model services are all containerized. See the top-level `docker-compose.yml` for service definitions.

To build and run all services:
```bash
docker-compose up --build
```

## 7. API Endpoints

- `/agent`: Chat agent endpoint
- `/chat-stream`: Streaming chat endpoint
- `/ocr`: Image upload and OCR endpoint

## 8. Frontend

The frontend is a Next.js app with a modern chat interface and image upload, located in the `frontend` directory.

## 9. Database

Postgres database with schema for patients, prescriptions, medications, and prescription_medications. See `database/init.sql` for details.
