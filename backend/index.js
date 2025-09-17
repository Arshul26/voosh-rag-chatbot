const express = require('express');
require('dotenv').config();
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const bodyParser = require('body-parser');
const { createClient } = require('redis');
const ChatService = require('./services/chatService');

console.log("✅ .env loaded successfully");

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

console.log("✅ Express + HTTP + Socket.IO initialized");

app.use(cors());
app.use(bodyParser.json());

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
console.log("🔄 Connecting to Redis at:", REDIS_URL);

const redisClient = createClient({ url: REDIS_URL });

redisClient.on("error", (err) => {
  console.error("❌ Redis Client Error", err);
});

redisClient.connect()
  .then(() => {
    console.log("✅ Redis connected successfully");

    const chatService = new ChatService({ redisClient, io });

    // ✅ Bring back all your routes
    app.get('/health', (req, res) => res.json({ status: 'ok' }));

    app.get('/api/session/:sid/history', async (req, res) => {
      const sid = req.params.sid;
      const history = await chatService.getSessionHistory(sid);
      res.json({ session: sid, history });
    });

    app.post('/api/session/:sid/reset', async (req, res) => {
      const sid = req.params.sid;
      await chatService.clearSession(sid);
      res.json({ session: sid, cleared: true });
    });

    app.post('/api/clear-session', async (req, res) => {
      const { sessionId } = req.body;
      if (!sessionId) {
        return res.status(400).json({ error: 'sessionId is required' });
      }
      await chatService.clearSession(sessionId);
      res.json({ session: sessionId, cleared: true });
    });

    app.post('/api/chat', async (req, res) => {
      try {
        const { sessionId, message } = req.body;
        const reply = await chatService.generateReplyOnly({ sessionId, message });
        res.json(reply);
      } catch (err) {
        console.error(err);
        res.status(500).json({ error: err.message });
      }
    });

    const PORT = process.env.PORT || 4000;
    server.listen(PORT, () => {
      console.log(`🚀 Server running on port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error("❌ Failed to connect to Redis:", err);
  });
