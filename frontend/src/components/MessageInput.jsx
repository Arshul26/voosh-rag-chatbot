import { useState } from 'react';

export default function MessageInput({ onSend }) {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSend(text.trim());
      setText('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="flex mt-4 gap-3">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message..."
        className="flex-1 px-5 py-3 rounded-3xl border border-white/20 bg-white/30 text-blue-700 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-blue-300 placeholder-blue-400 animate-fadeIn"
      />
      <button
        onClick={handleSend}
        className="px-6 py-3 rounded-3xl bg-blue-500/80 text-white hover:bg-blue-600/90 transition-all shadow-md animate-fadeIn"
      >
        Send
      </button>
    </div>
  );
}

