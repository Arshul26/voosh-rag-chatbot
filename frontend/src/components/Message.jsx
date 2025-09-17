export default function Message({ from, text }) {
  const isUser = from === 'user';
  return (
    <div className={`my-2 flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <span
        className={`inline-block px-5 py-3 rounded-3xl max-w-[70%] break-words
          ${isUser 
            ? 'bg-blue-500/80 text-white backdrop-blur-sm animate-fadeIn' 
            : 'bg-white/30 text-blue-700 backdrop-blur-sm border border-white/20 animate-fadeIn'}`}
      >
        {text}
      </span>
    </div>
  );
}


