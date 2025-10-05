import { useRef, useState, useEffect } from 'react';
import type { Message, RefinementData, ClassroomApiResponse } from '@/types/classroom';
import { useSearchParams } from 'react-router-dom';
import { sendClassroomMessage } from '@/services/classroom';
import { HiSparkles } from 'react-icons/hi2';
import { FiSend } from 'react-icons/fi';
import RefinementPanel from '@/components/classroom/RefinementPanel';

const ClassroomPage = () => {
  const [searchParams] = useSearchParams();
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  // Refinement state
  const [showRefinement, setShowRefinement] = useState<boolean>(false);
  const [refinementData, setRefinementData] = useState<RefinementData | null>(null);
  const [selectedSuggestions, setSelectedSuggestions] = useState<number[]>([]);
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
        // Clear refinement state
        setShowRefinement(false);
        setRefinementData(null);
        setSelectedSuggestions([]);
        try {
          const response = await sendClassroomMessage(query);
          handleApiResponse(response, query);
        } catch (err: any) {
          setError(err?.message || 'Something went wrong.');
        } finally {
          setLoading(false);
        }
      };
      sendInitialMessage();
    }
    // eslint-disable-next-line
  }, [searchParams]);

  const send = async () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: 'user', text }]);
    setInput('');
    setLoading(true);
    setError(null);
    // Clear refinement state
    setShowRefinement(false);
    setRefinementData(null);
    setSelectedSuggestions([]);
    try {
      const response = await sendClassroomMessage(text);
      handleApiResponse(response, text);
    } catch (err: any) {
      setError(err?.message || 'Something went wrong.');
    } finally {
      setLoading(false);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  // Handle API response for both direct and refinement flows
  const handleApiResponse = (response: ClassroomApiResponse | string, originalQuery: string) => {
    console.log('🔍 DEBUG - Raw response:', JSON.stringify(response, null, 2));
    console.log('[FRONTEND] Received response:', response);
    console.log('[FRONTEND] Response type:', typeof response);
    
    // Handle string responses (errors or backward compatibility)
    if (typeof response === 'string') {
      console.log('[FRONTEND] String response detected');
      setMessages((prev) => [...prev, { role: 'assistant', text: response }]);
      return;
    }
    
    // Handle object responses with explicit property checks
    if (response && typeof response === 'object') {
      // Backend uses 'response_type', frontend types expect 'type' - handle both
      const responseType = (response as any).type || (response as any).response_type;
      console.log('[FRONTEND] Response.type/response_type:', responseType);
      
      // Direct response handler
      if (responseType === 'direct_response' && 'bot_message' in response) {
        console.log('[FRONTEND] ✅ Direct response - displaying message');
        setMessages((prev) => [...prev, { role: 'assistant', text: (response as any).bot_message }]);
        return;
      }
      
      // Refinement needed handler
      if (responseType === 'refinement_needed' && 'refinement_data' in response) {
        console.log('[FRONTEND] ✅ Refinement needed - showing panel');
        const refinementData = (response as any).refinement_data;
        setRefinementData(refinementData);
        const suggestionCount = refinementData?.suggestions?.length || 0;
        setSelectedSuggestions(Array.from({ length: suggestionCount }, (_, idx) => idx));
        setShowRefinement(true);
        return;
      }
    }
    
    // Fallback error
    console.error('[FRONTEND] ❌ Unrecognized format:', response);
    setMessages((prev) => [...prev, { 
      role: 'assistant', 
      text: '🤖 Unrecognized response from backend. Please try again.' 
    }]);
  };

  // Handler for confirming refinement
  const handleRefinementConfirm = () => {
    if (!refinementData) return;
    const selected = (refinementData.suggestions || []).filter((_: any, idx: number) => selectedSuggestions.includes(idx));
    const refinedQuery = `${refinementData.original_query} ${selected.map((s: any) => s.text).join(' ')}`;
  setMessages((prev) => [...prev, { role: 'assistant', text: `🚧 Main agent is under development. Your refined query: ${refinedQuery}` }]);
    setShowRefinement(false);
    setRefinementData(null);
    setSelectedSuggestions([]);
    console.log('handleRefinementConfirm called. Refined query:', refinedQuery);
  };

  // Handler for skipping refinement
  const handleSkipRefinement = () => {
    if (!refinementData) return;
  setMessages((prev) => [...prev, { role: 'assistant', text: `🚧 Main agent is under development. Using your original query: ${refinementData.original_query}` }]);
    setShowRefinement(false);
    setRefinementData(null);
    setSelectedSuggestions([]);
    console.log('handleSkipRefinement called. Original query:', refinementData.original_query);
  };

  // Track selectedSuggestions changes
  useEffect(() => {
    console.log('selectedSuggestions changed:', selectedSuggestions);
  }, [selectedSuggestions]);
  return (
    <div className="h-full flex flex-col bg-white">
      {/* Welcome Note - Modern AI style, positioned below top bar */}
      <div className="w-full mt-16 bg-gradient-to-br from-white via-white to-white border-b border-white py-8 px-6 flex flex-col items-center relative">
        <div className="relative z-10 flex flex-col items-center">
          <h1 className="text-3xl sm:text-4xl font-bold text-slate-700 mb-3 text-center tracking-tight">@Welcome to Classroom</h1>
          <p className="text-sm sm:text-base text-slate-500 text-center max-w-lg mb-4 leading-relaxed">A focused fool can accomplish more than a distracted genius.</p>
        </div>
      </div>
      {/* Messages Container - below welcome note */}
      <div className="flex-1 overflow-y-auto pt-4">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[40vh] select-none"></div>
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
              {/* Refinement Panel */}
              {showRefinement && (
                <RefinementPanel
                  originalQuery={refinementData?.original_query || ''}
                  suggestions={refinementData?.suggestions || []}
                  reasoning={refinementData?.reasoning || ''}
                  selectedSuggestions={selectedSuggestions}
                  onToggleSuggestion={(index) => {
                    setSelectedSuggestions(prev =>
                      prev.includes(index)
                        ? prev.filter(i => i !== index)
                        : [...prev, index]
                    );
                  }}
                  onConfirm={handleRefinementConfirm}
                  onSkip={handleSkipRefinement}
                />
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="max-w-3xl mr-20 px-6 py-4 bg-gray-50 text-gray-800 rounded-2xl border border-gray-100">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                      <span className="text-gray-500">Do the hard thing first</span>
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
