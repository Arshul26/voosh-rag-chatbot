const express = require('express');

require('dotenv').config();

const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const bodyParser = require('body-parser');
const { createClient } = require('redis');
const ChatService = require('./services/chatService');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.use(cors());
app.use(bodyParser.json());

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const redisClient = createClient({ url: REDIS_URL });

redisClient.connect().catch(console.error);

const chatService = new ChatService({ redisClient, io });

// Health check
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// Fetch session history
app.get('/api/session/:sid/history', async (req, res) => {
  const sid = req.params.sid;
  const history = await chatService.getSessionHistory(sid);
  res.json({ session: sid, history });
});

// Reset session
app.post('/api/session/:sid/reset', async (req, res) => {
  const sid = req.params.sid;
  await chatService.clearSession(sid);
  res.json({ session: sid, cleared: true });
});

// Optional: Alias route to support POST /api/clear-session (for convenience)
app.post('/api/clear-session', async (req, res) => {
  const { sessionId } = req.body;
  if (!sessionId) {
    return res.status(400).json({ error: 'sessionId is required' });
  }
  await chatService.clearSession(sessionId);
  res.json({ session: sessionId, cleared: true });
});

// Chat endpoint (REST)
app.post('/api/chat', async (req, res) => {
  try {
    const { sessionId, message } = req.body;
    // Use generateReplyOnly so REST returns reply but server does NOT emit it via socket
    const reply = await chatService.generateReplyOnly({ sessionId, message });
    res.json(reply); // returns the assistant message object
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

