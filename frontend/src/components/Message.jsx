export default function Message({ from, text }) {
  const isUser = from === 'user';
  return (
    <div style={{
      textAlign: isUser ? 'right' : 'left',
      margin: '8px 0'
    }}>
      <span style={{
        display: 'inline-block',
        padding: '8px 12px',
        borderRadius: '16px',
        background: isUser ? '#4f46e5' : '#e5e7eb',
        color: isUser ? 'white' : 'black',
        maxWidth: '70%'
      }}>
        {text}
      </span>
    </div>
  );
}
