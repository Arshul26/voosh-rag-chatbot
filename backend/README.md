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
git clone <your-backend-repo-url>
cd backend


2. Install dependencies
npm install


3. Configure environment variables

Create a .env file in the backend/ folder (rename .env.example to .env) and add:

PORT=4000
REDIS_URL=redis://localhost:6379
QDRANT_URL=<your-qdrant-cloud-url>
QDRANT_API_KEY=<your-qdrant-api-key>
EMBEDDING_ADAPTER_URL=http://localhost:5001/embed
LLM_ADAPTER_URL=http://localhost:5002/llm
SESSION_TTL_SECONDS=86400
GEMINI_API_KEY=<your-gemini-api-key>


Replace placeholders with your actual keys and URLs.

4. Start supporting services

Embedding Adapter (Python Flask)

cd worker
python adapter.py


LLM Adapter (Python Flask)

python llm_adapter.py


Backend

npm run dev

API Endpoints
Health Check
GET /health


Returns { status: "ok" }.

Chat
POST /api/chat
Body: { "sessionId": "<id>", "message": "<text>" }


Returns assistant response along with retrieved documents.

Fetch Session History
GET /api/session/:sid/history


Returns chat history for a session.

Reset Session
POST /api/session/:sid/reset


Or (alias)

POST /api/clear-session
Body: { "sessionId": "<id>" }


Clears chat history for a session.

Testing:

You can test the endpoints using curl:

curl -X POST http://localhost:4000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"test-sess-1\",\"message\":\"What is the top news today?\"}"

curl -X POST http://localhost:4000/api/session/test-sess-1/reset \
  -H "Content-Type: application/json"

Notes:

Session management: Chat history is stored in Redis with a TTL of 24 hours by default.

RAG Pipeline: Queries are converted into embeddings, relevant news articles are retrieved from Qdrant, and the prompt is sent to the LLM adapter for generation.

LLM Adapter: Currently uses a placeholder. Can be integrated with Google Gemini API using the provided API key.