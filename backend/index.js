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

// Chat endpoint (REST)
app.post('/api/chat', async (req, res) => {
  try {
    const { sessionId, message } = req.body;
    const reply = await chatService.handleMessage({ sessionId, message });
    res.json(reply);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

// WebSocket events
io.on('connection', socket => {
  console.log('socket connected', socket.id);

  socket.on('join', ({ sessionId }) => {
    socket.join(sessionId);
  });

  socket.on('message', async ({ sessionId, message }) => {
    try {
      io.to(sessionId).emit('message', { from: 'user', text: message, timestamp: Date.now() });
      await chatService.handleMessage({ sessionId, message, socket });
    } catch (e) {
      console.error(e);
      socket.emit('error', { error: e.message });
    }
  });

  socket.on('disconnect', () => console.log('socket disconnected', socket.id));
});

const PORT = process.env.PORT || 4000;
server.listen(PORT, () => console.log(`Backend listening on ${PORT}`));
