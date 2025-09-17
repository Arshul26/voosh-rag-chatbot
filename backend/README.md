# RAG-Powered News Chatbot - Backend

This is the backend service for a Retrieval-Augmented Generation (RAG) chatbot for news websites.  
It handles chat sessions, embeddings, document retrieval, and communication with a language model (LLM) adapter.

---

## Tech Stack

- **Node.js + Express** – REST API server
- **Redis** – In-memory session storage for chat history
- **Qdrant** – Vector database for storing news embeddings
- **Socket.io** – Real-time chat support
- **Axios** – HTTP client for embedding and LLM adapters
- **Python Flask** – LLM adapter (`worker/llm_adapter.py`)
- **dotenv** – Environment variable management

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Arshul26/voosh-rag-chatbot.git
cd backend
```
---
### 2. Install dependencies
```bash
npm install

```
### 3. Configure environment variables
```bash

# Create a .env file in the backend/ folder (rename .env.example to .env) and add:

PORT=4000
REDIS_URL=redis://localhost:6379
QDRANT_URL=<your-qdrant-cloud-url>
QDRANT_API_KEY=<your-qdrant-api-key>
EMBEDDING_ADAPTER_URL=http://localhost:5001/embed
LLM_ADAPTER_URL=http://localhost:5002/llm
SESSION_TTL_SECONDS=86400
GEMINI_API_KEY=<your-gemini-api-key>

