import { useState } from 'react';
import { sendStudentGPTMessage } from '@/services/api';

const StudentGPTChat = () => {
  const [input, setInput] = useState('');
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
      const response = await sendStudentGPTMessage(text);
      setMessages((prev) => [...prev, { role: 'assistant', text: response }]);
    } catch (err: any) {
      setError(err?.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-[calc(100vh-64px)] overflow-hidden bg-gradient-to-br from-blue-50/80 via-blue-50/50 to-white/90 pb-28 flex flex-col">
      <div className="flex-1 overflow-y-auto p-4 max-w-3xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-gray-400 text-center mt-10">Start a conversation with StudentGPT!</div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`rounded-xl px-4 py-2 max-w-[80%] ${msg.role === 'user' ? 'bg-sky-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="mb-4 flex justify-start">
            <div className="rounded-xl px-4 py-2 bg-gray-100 text-gray-800 animate-pulse">StudentGPT is typing...</div>
          </div>
        )}
        {error && (
          <div className="mb-4 text-red-500 text-center">{error}</div>
        )}
      </div>
      {/* Fixed bottom chatbar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-sm">
        <div className="max-w-3xl mx-auto p-4">
          <div className="flex items-end gap-3">
            <textarea
              rows={1}
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500 text-gray-800 placeholder-gray-400"
              disabled={loading}
            />
            <button
              type="button"
              onClick={send}
              className="inline-flex items-center justify-center rounded-xl bg-sky-600 text-white px-4 py-2 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm disabled:opacity-50"
              disabled={!input.trim() || loading}
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentGPTChat;
