import { useEffect, useState, useRef } from 'react';
import Message from './Message';
import MessageInput from './MessageInput';
import { fetchChatReply, fetchSessionHistory, resetSession, socket } from '../services/api';

export default function ChatBox() {
  const [sessionId] = useState('sess-1');
  const [messages, setMessages] = useState([]);
  const [assistantTyping, setAssistantTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom whenever messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, assistantTyping]);

  // Load history + socket listeners
  useEffect(() => {
    fetchSessionHistory(sessionId).then(setMessages);

    socket.on('message', (msg) => {
      // Skip assistant messages from socket to avoid duplicate replies
      if (msg.from === 'assistant') return;

      setMessages((prev) => {
        const recent = prev.slice(-5);
        const isDuplicate = recent.some(
          (m) => m.from === msg.from && m.text === msg.text
        );
        return isDuplicate ? prev : [...prev, msg];
      });
    });

    socket.emit('join', { sessionId });

    return () => socket.off('message');
  }, [sessionId]);

  // Send message
  const sendMessage = async (text) => {
    const userMsg = { from: 'user', text, timestamp: Date.now() };

    // ✅ Prevent duplicate user message
    setMessages((prev) => {
      const recent = prev.slice(-5);
      const isDuplicate = recent.some(
        (m) => m.from === 'user' && m.text === text
      );
      return isDuplicate ? prev : [...prev, userMsg];
    });

    setAssistantTyping(true);

    // Fetch reply directly from backend
    const reply = await fetchChatReply(sessionId, text);

    // ✅ Add only ONE assistant message
    setMessages((prev) => [
      ...prev,
      { from: 'assistant', text: reply.text, timestamp: Date.now() },
    ]);

    setAssistantTyping(false);

    // Emit user message only (not assistant response)
    socket.emit('message', { sessionId, message: text });
  };

  // Reset session
  const handleReset = async () => {
    await resetSession(sessionId);
    setMessages([]);
  };

  return (
    <div className="w-full max-w-3xl h-[80vh] p-6 bg-white/20 backdrop-blur-xl rounded-3xl shadow-2xl flex flex-col border border-white/20 animate-fadeIn">
      {/* Header */}
      <h2 className="text-3xl font-bold text-blue-600 mb-4 text-center drop-shadow-md">
        Voosh RAG Chatbot
      </h2>

      {/* Messages Window */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-white/20 rounded-xl border border-white/10 scrollbar-thin scrollbar-thumb-blue-300/50 scrollbar-track-transparent">
        {messages.map((msg, i) => (
          <Message key={i} {...msg} />
        ))}

        {assistantTyping && (
          <div className="my-2 flex justify-start">
            <span className="inline-block px-4 py-2 rounded-2xl max-w-[40%] bg-white/30 text-blue-700 animate-pulse">
              Assistant is typing...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <MessageInput onSend={sendMessage} />

      {/* Reset Session */}
      <button
        onClick={handleReset}
        className="mt-4 py-2 px-6 bg-blue-500/70 text-white rounded-2xl hover:bg-blue-600/80 transition-all duration-200 shadow-md self-center"
      >
        Reset Session
      </button>
    </div>
  );
}


