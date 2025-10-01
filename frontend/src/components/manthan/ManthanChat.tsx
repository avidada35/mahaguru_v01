import { useState, useEffect, useRef } from 'react';
import { X, Send, Paperclip, Mic, Image as ImageIcon, FileText, Code, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { RefinerPanel } from '@/components/classroom/RefinerPanel';
import { useRefineQuery } from '@/hooks/useRefineQuery';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface ManthanChatProps {
  onClose?: () => void;
  onNewMessage?: () => void;
}

export function ManthanChat({ onClose, onNewMessage }: ManthanChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [refinerPanelVisible, setRefinerPanelVisible] = useState(false);
  const [refinedData, setRefinedData] = useState<any>(null);
  const [refinerError, setRefinerError] = useState<string | null>(null);
  const [queryType, setQueryType] = useState<'academic' | 'non-academic' | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const refineMutation = useRefineQuery();

  // Focus input when component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setIsLoading(true);
    setRefinerError(null);
    // Basic query classification (expandable)
    const academicKeywords = [
      'math', 'physics', 'chemistry', 'biology', 'history', 'geography', 'syllabus', 'exam', 'homework', 'assignment', 'subject', 'topic', 'explain', 'study', 'plan', 'curriculum', 'school', 'college', 'university', 'science', 'literature', 'macbeth', 'react', 'quantum', 'problem', 'solve'
    ];
    const lowerInput = input.toLowerCase();
    const isAcademic = academicKeywords.some(word => lowerInput.includes(word));
    setQueryType(isAcademic ? 'academic' : 'non-academic');
    try {
      const result = await refineMutation.mutateAsync(input);
      setRefinedData(result);
      setRefinerPanelVisible(true);
      // Collect suggestions for UI (modular)
      setSuggestions(result.suggestions || []);
      setIsLoading(false);
    } catch (err: any) {
      setRefinerError(err.message || 'Refiner error');
      setIsLoading(false);
      // Fallback: proceed with original query if refiner fails
      proceedWithQuery(input);
    }
  };

  const proceedWithQuery = (finalQuery: string) => {
    // Add user message (refined query)
    const userMessage: Message = {
      id: Date.now().toString(),
      content: finalQuery,
      isUser: true,
      timestamp: new Date()
    };
    // Maintain original query for reference (if different)
    if (refinedData && refinedData.original_query && refinedData.original_query !== finalQuery) {
      const originalMessage: Message = {
        id: (Date.now() + 0.5).toString(),
        content: `Original Query: ${refinedData.original_query}`,
        isUser: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, originalMessage, userMessage]);
    } else {
      setMessages(prev => [...prev, userMessage]);
    }
    setInput('');
    setIsLoading(true);
    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm Manthan, your AI study companion. How can I help you with your studies today? I can explain concepts, help with homework, or provide study resources.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
      if (onNewMessage) {
        onNewMessage();
      }
    }, 1000);
    setRefinerPanelVisible(false);
    setRefinedData(null);
  };

  const handleAcceptRefinement = (refinedQuery: string) => {
    proceedWithQuery(refinedQuery);
  };

  const handleSkipRefinement = () => {
    proceedWithQuery(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  // Suggested prompts
  const suggestedPrompts = [
    'Explain quantum physics in simple terms',
    'Help me solve this math problem: 2x + 5 = 15',
    'What are the main themes in Shakespeare\'s Macbeth?',
    'Create a study plan for learning React'
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      {/* Query Type & Suggestions Preview (for debugging/expansion) */}
      {refinerPanelVisible && (
        <div className="absolute top-4 left-4 bg-white/90 rounded-lg shadow p-2 text-xs z-50">
          <div><b>Query Type:</b> {queryType}</div>
          <div><b>Suggestions:</b> {suggestions.join(', ')}</div>
        </div>
      )}
      <div className="relative w-full max-w-4xl h-[80vh] bg-white rounded-lg shadow-xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-end h-12 px-4 bg-sky-50 border-b border-black/10">
          <h2 className="mr-4 font-medium">Mahaguru AI</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-9 w-9 rounded-full"
            aria-label="Close chat"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Chat messages */}
        <ScrollArea className="flex-1 p-4 overflow-y-auto bg-sky-100">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <div className="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center mb-4">
                <Zap className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">How can I help you today?</h3>
              <p className="text-muted-foreground mb-8 max-w-md">Ask me anything about your studies, and I'll do my best to assist you.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                {suggestedPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(prompt)}
                    className="p-4 text-left border rounded-lg hover:bg-accent/50 transition-colors text-sm"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.isUser
                        ? 'bg-primary text-primary-foreground rounded-br-none'
                        : 'bg-muted rounded-bl-none'
                    }`}
                  >
                    <div className="prose prose-sm max-w-none">
                      {message.content}
                    </div>
                    <div className={`text-xs mt-1 ${message.isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        {/* Input area */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="relative">
            <div className="flex items-center gap-2 mb-2">
              <Button type="button" variant="ghost" size="icon" className="h-8 w-8">
                <Paperclip className="h-4 w-4" />
              </Button>
              <Button type="button" variant="ghost" size="icon" className="h-8 w-8">
                <ImageIcon className="h-4 w-4" />
              </Button>
              <Button type="button" variant="ghost" size="icon" className="h-8 w-8">
                <FileText className="h-4 w-4" />
              </Button>
              <Button type="button" variant="ghost" size="icon" className="h-8 w-8">
                <Code className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-stretch">
              <Textarea
                ref={inputRef}
                value={input}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything about your studies..."
                className="min-h-[80px] resize-none flex-1"
              />
              <div className="flex items-center h-[80px] ml-2">
                <Button
                  type="submit"
                  className="grid place-items-center h-[68px] w-[68px] rounded-lg bg-sky-600 text-white hover:bg-sky-700 active:bg-sky-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!input.trim() || isLoading}
                  aria-label="Send message"
                >
                  <Send className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </form>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Manthan may produce inaccurate information. Verify important details.
          </p>
        </div>
        {refinerPanelVisible && refinedData && (
          <RefinerPanel
            originalQuery={input}
            refinedData={refinedData}
            onAccept={handleAcceptRefinement}
            onSkip={handleSkipRefinement}
            isLoading={isLoading}
            error={refinerError || refineMutation.error?.message}
          />
        )}
      </div>
    </div>
  );
}
