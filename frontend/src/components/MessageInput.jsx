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
    <div style={{ display: 'flex', marginTop: '12px' }}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message..."
        style={{ flex: 1, padding: '8px 12px', borderRadius: '12px', border: '1px solid #ccc' }}
      />
      <button onClick={handleSend} style={{ marginLeft: '8px', padding: '8px 16px', borderRadius: '12px', background: '#4f46e5', color: 'white', border: 'none' }}>
        Send
      </button>
    </div>
  );
}
