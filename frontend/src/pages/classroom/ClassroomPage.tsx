


import { useRef, useState } from 'react';
import { sendClassroomMessage } from '@/services/classroom';
import { HiSparkles } from 'react-icons/hi2';
import { FiSend } from 'react-icons/fi';

const ClassroomPage = () => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = async () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setInput('');
    setLoading(true);
    setError(null);
    try {
      const response = await sendClassroomMessage(text);
      setMessages((prev) => [...prev, { role: 'assistant', text: response }]);
    } catch (err: any) {
      setError(err?.message || 'Something went wrong.');
    } finally {
      setLoading(false);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  return (
    <div className="w-full h-[calc(100vh-64px)] overflow-hidden bg-gradient-to-br from-blue-50/80 via-blue-50/50 to-white/90 pb-28 flex flex-col">
      <div className="flex-1 overflow-y-auto p-4 max-w-3xl mx-auto w-full flex flex-col items-center justify-center">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center w-full h-full select-none">
            <HiSparkles className="text-sky-400 text-5xl mb-4" />
            <h2 className="text-2xl font-bold mb-2">Welcome to Classroom</h2>
            <p className="text-lg text-gray-500 mb-2 text-center max-w-xl">
              Share your thoughts, questions, and dilemmas. I'm here to help you think through them.
            </p>
          </div>
        ) : (
          <div className="w-full">
            {messages.map((msg, idx) => (
              <div key={idx} className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`rounded-xl px-4 py-2 max-w-[80%] ${msg.role === 'user' ? 'bg-sky-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="mb-4 flex justify-start">
                <div className="rounded-xl px-4 py-2 bg-gray-100 text-gray-800 animate-pulse">Manthan AI is typing...</div>
              </div>
            )}
            {error && (
              <div className="mb-4 text-red-500 text-center">{error}</div>
            )}
          </div>
        )}
      </div>
      {/* Modern AI chat bar */}
  <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-white/95 to-white/80 border-t border-gray-200 shadow-lg z-30">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              rows={1}
              placeholder="Type your message..."
              value={input}
              onChange={e => {
                setInput(e.target.value);
                // Auto-expand textarea height
                const el = e.target as HTMLTextAreaElement;
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 160) + 'px';
              }}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              className="w-full resize-none rounded-2xl border border-gray-300 px-4 py-3 pr-16 text-base focus:outline-none focus:ring-2 focus:ring-sky-500 text-gray-800 placeholder-gray-400 bg-white shadow-sm transition-all min-h-[48px] max-h-40"
              disabled={loading}
              style={{overflowY: 'auto'}}
              autoFocus
            />
              <button
                type="button"
                className="absolute bottom-2 right-2 w-10 h-10 flex items-center justify-center rounded-full bg-[#000003] hover:bg-[#fcfcfc] text-white shadow-lg focus:outline-none focus:ring-2 focus:ring-[#3578ED] disabled:opacity-50 transition-all z-50"
                onClick={send}
                disabled={!input.trim() || loading}
                tabIndex={0}
                aria-label="Send message"
              >
                {loading ? (
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                  </svg>
                ) : (
                  <FiSend className="h-5 w-5" />
                )}
              </button>
          </div>
          {/* Removed Manthan AI button as requested */}
        </div>
      </div>
    </div>
  );
};

export default ClassroomPage;
