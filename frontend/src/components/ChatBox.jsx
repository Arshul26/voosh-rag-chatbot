import { useEffect, useState } from 'react';
import Message from './Message';
import MessageInput from './MessageInput';
import { fetchChatReply, fetchSessionHistory, resetSession, socket } from '../services/api';

export default function ChatBox() {
  const [sessionId] = useState('sess-1'); // unique session
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Load session history
    fetchSessionHistory(sessionId).then(setMessages);

    // Listen for WebSocket messages
    socket.on('message', (msg) => {
      setMessages((prev) => [...prev, msg]);
    });

    // Join session room
    socket.emit('join', { sessionId });

    return () => socket.off('message');
  }, [sessionId]);

  const sendMessage = async (text) => {
    const userMsg = { from: 'user', text, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);

    // Send via REST API
    const reply = await fetchChatReply(sessionId, text);
    setMessages((prev) => [...prev, { from: 'assistant', text: reply.text, timestamp: Date.now() }]);

    // Optionally send via WebSocket
    socket.emit('message', { sessionId, message: text });
  };

  const handleReset = async () => {
    await resetSession(sessionId);
    setMessages([]);
  };

  return (
    <div style={{ maxWidth: '600px', margin: 'auto', padding: '24px', border: '1px solid #ccc', borderRadius: '16px' }}>
      <h2>RAG Chatbot</h2>
      <div style={{ minHeight: '300px', border: '1px solid #ddd', padding: '12px', borderRadius: '12px', overflowY: 'auto' }}>
        {messages.map((msg, i) => <Message key={i} {...msg} />)}
      </div>
      <MessageInput onSend={sendMessage} />
      <button onClick={handleReset} style={{ marginTop: '12px', padding: '8px 16px', borderRadius: '12px', background: 'red', color: 'white', border: 'none' }}>
        Reset Session
      </button>
    </div>
  );
}
