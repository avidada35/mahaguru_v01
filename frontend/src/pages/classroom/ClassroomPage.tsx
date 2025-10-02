import { useRef, useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { sendClassroomMessage } from '@/services/classroom';
import { HiSparkles } from 'react-icons/hi2';
import { FiSend } from 'react-icons/fi';

const ClassroomPage = () => {
  const [searchParams] = useSearchParams();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle initial query from homepage
  useEffect(() => {
    const query = searchParams.get('query');
    if (query && query.trim()) {
      // Auto-send the initial message from homepage
      const sendInitialMessage = async () => {
        setMessages([{ role: 'user', text: query }]);
        setLoading(true);
        setError(null);
        try {
          const response = await sendClassroomMessage(query);
          setMessages(prev => [...prev, { role: 'assistant', text: response }]);
        } catch (err: any) {
          setError(err?.message || 'Something went wrong.');
        } finally {
          setLoading(false);
        }
      };
      sendInitialMessage();
    }
  }, [searchParams]);

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
    <div className="h-full flex flex-col bg-white">
      {/* Messages Container - Takes full available space with top padding for navbar */}
      <div className="flex-1 overflow-y-auto pt-16">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[60vh] select-none">
              <HiSparkles className="text-sky-400 text-6xl mb-6" />
              <h2 className="text-3xl font-bold mb-4 text-gray-800">Welcome to Classroom</h2>
              <p className="text-lg text-gray-600 mb-4 text-center max-w-2xl leading-relaxed">
                Share your thoughts, questions, and dilemmas. I'm here to help you think through them and learn together.
              </p>
              <div className="text-sm text-gray-400 bg-gray-50 px-4 py-2 rounded-full">
                Start by typing your question below
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl px-6 py-4 rounded-2xl ${
                    msg.role === 'user' 
                      ? 'bg-sky-600 text-white ml-20' 
                      : 'bg-gray-50 text-gray-800 mr-20 border border-gray-100'
                  }`}>
                    <div className={`whitespace-pre-wrap ${msg.role === 'user' ? 'text-white' : 'text-gray-800'}`}>
                      {msg.text}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="max-w-3xl mr-20 px-6 py-4 bg-gray-50 text-gray-800 rounded-2xl border border-gray-100">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                      <span className="text-gray-500">Let me think...</span>
                    </div>
                  </div>
                </div>
              )}
              {error && (
                <div className="flex justify-center">
                  <div className="max-w-2xl px-4 py-3 bg-red-50 text-red-800 rounded-lg border border-red-200">
                    <div className="flex items-center space-x-2">
                      <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                      <span>{error}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="relative">
            <textarea
              ref={textareaRef}
              rows={1}
              placeholder="Ask me anything about your studies..."
              value={input}
              onChange={e => {
                setInput(e.target.value);
                // Auto-expand textarea height
                const el = e.target as HTMLTextAreaElement;
                el.style.height = 'auto';
                el.style.height = Math.min(el.scrollHeight, 120) + 'px';
              }}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              className="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 pr-12 text-base focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent text-gray-800 placeholder-gray-500 bg-white shadow-sm transition-all min-h-[48px] max-h-[120px]"
              disabled={loading}
              style={{overflowY: 'auto'}}
              autoFocus
            />
            <button
              type="button"
              className="absolute bottom-2 right-2 w-9 h-9 flex items-center justify-center rounded-lg bg-sky-600 hover:bg-sky-700 text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              onClick={send}
              disabled={!input.trim() || loading}
              tabIndex={0}
              aria-label="Send message"
            >
              {loading ? (
                <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                </svg>
              ) : (
                <FiSend className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClassroomPage;
