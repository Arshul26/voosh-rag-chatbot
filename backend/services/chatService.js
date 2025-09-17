// backend/services/chatService.js
const { QdrantClient } = require('@qdrant/js-client-rest');
require('dotenv').config();
const axios = require('axios');

class ChatService {
  constructor({ redisClient, io }) {
    this.redis = redisClient;
    this.io = io;
    this.qdrant = new QdrantClient({
      url: process.env.QDRANT_URL || 'http://localhost:6333',
      apiKey: process.env.QDRANT_API_KEY,
      checkCompatibility: false
    });
    this.collectionName = process.env.QDRANT_COLLECTION || 'news_articles';
    this.embeddingAdapterUrl = process.env.EMBEDDING_ADAPTER_URL || 'http://localhost:5001/embed';
    this.llmAdapterUrl = process.env.LLM_ADAPTER_URL || 'http://localhost:5002/llm';
  }

  async appendToHistory(sessionId, messageObj) {
    const key = `session:${sessionId}:history`;
    await this.redis.rPush(key, JSON.stringify(messageObj));
    const ttl = parseInt(process.env.SESSION_TTL_SECONDS || '86400', 10);
    await this.redis.expire(key, ttl);
  }

  async getSessionHistory(sessionId) {
    const key = `session:${sessionId}:history`;
    const items = await this.redis.lRange(key, 0, -1);
    return items.map(i => JSON.parse(i));
  }

  async clearSession(sessionId) {
    const key = `session:${sessionId}:history`;
    await this.redis.del(key);
  }

  async retrieveRelevantDocs(queryEmbedding, topK = 4) {
    const res = await this.qdrant.search(this.collectionName, {
      vector: queryEmbedding,
      limit: topK,
      with_payload: true
    });
    return res?.map(hit => hit.payload?.text || '') || [];
  }

  // Generates reply and stores user+assistant messages, but DOES NOT emit via socket
  async generateReplyOnly({ sessionId, message }) {
    const userMsg = { role: 'user', text: message, ts: Date.now() };
    await this.appendToHistory(sessionId, userMsg);

    // Embedding
    const embResp = await axios.post(this.embeddingAdapterUrl, { text: message });
    const embedding = embResp.data.embedding || (embResp.data.embeddings && embResp.data.embeddings[0]);

    // Retrieve docs
    const docs = await this.retrieveRelevantDocs(embedding, 4);
    const prompt = this.composePrompt(message, docs);

    // Call LLM adapter
    const llmResp = await axios.post(this.llmAdapterUrl, { prompt, stream: false });
    const botText = llmResp.data.text;

    const botMsg = { role: 'assistant', text: botText, ts: Date.now(), retrieved: docs };
    await this.appendToHistory(sessionId, botMsg);

    // Return the full assistant message object (no emit)
    return botMsg;
  }

  // Generates reply and emits via socket (used for WebSocket flow)
  async handleMessage({ sessionId, message, socket = null }) {
    // reuse generateReplyOnly to do the heavy lifting (history + LLM)
    const botMsg = await this.generateReplyOnly({ sessionId, message });

    // Build payload for socket
    const payload = {
      from: 'assistant',
      text: botMsg.text,
      timestamp: Date.now(),
      retrieved: botMsg.retrieved || []
    };

    // Emit only once: either directly to the calling socket or broadcast to the room
    if (socket) {
      socket.emit('message', payload); // to the connected socket only
    } else {
      this.io.to(sessionId).emit('message', payload); // broadcast to the session room
    }

    // return the assistant message object for callers
    return botMsg;
  }

  composePrompt(query, docs) {
    const system = `You are a helpful assistant that answers user queries using the provided news passages. If nothing in the passages answers the question, say "I don't know".`;
    const passages = docs.map((d, i) => `Passage ${i + 1}:\n${d}`).join('\n\n');
    return `${system}\n\nUser question: ${query}\n\nNews passages:\n${passages}\n\nAnswer:`;
  }
}

module.exports = ChatService;



