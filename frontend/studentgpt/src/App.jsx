import React, { useState, useRef, useEffect, useCallback, memo } from 'react'

import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import { 
  Send,
  Bot,
  User,
  Sparkles
} from 'lucide-react'
import { sendMessageToServer } from './api'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'

function App() {
  // Extract query param if present
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const initialQuery = queryParams.get('query')

  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  
  // Keep chat area height within parent (parent already excludes site navbar)
  const [containerHeight, setContainerHeight] = useState('100%')

  // Set Mahaguru theme
  useEffect(() => {
    document.documentElement.style.setProperty('--bg-color', '#F6FAFF')
    document.documentElement.style.setProperty('--chat-bg', '#EEF5FF')
    document.documentElement.style.setProperty('--primary-color', '#3A82F7')
    document.documentElement.style.setProperty('--text-color', '#121826')

    // Remove footer if it exists
    const footer = document.querySelector('footer')
    if (footer) {
      footer.style.display = 'none'
    }
  }, [])

  // Initialize with query param if present (only if not using external chatbar)
  useEffect(() => {
    if (typeof window !== 'undefined' && window.useExternalChatbar) return
    if (initialQuery) {
      // Add initial query as first user message and send it
      sendMessage(decodeURIComponent(initialQuery))
      // Clear the URL parameter after using it
      window.history.replaceState({}, '', '/studentgpt')
    }
  }, [initialQuery])

  

  const sendMessage = async (messageText) => {
    try {
      const textToSend = messageText || inputValue.trim()
      if (!textToSend || isLoading) return

      setIsLoading(true)

      // Add user message immediately
      const newMessage = {
        role: 'user',
        content: textToSend,
        id: Date.now()
      }
      setMessages(prev => [...prev, newMessage])
      if (!messageText) setInputValue('')

      // Get response from server
      const aiResponse = await sendMessageToServer(textToSend)
      
      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: aiResponse,
        id: Date.now() + 1
      }])

    } catch (error) {
      console.error('Error sending message:', error)
      // Add error message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        id: Date.now() + 1,
        isError: true
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Expose sender globally for external chatbar
  useEffect(() => {
    window.studentGPTSend = (text) => {
      if (typeof text === 'string' && text.trim()) {
        sendMessage(text)
      }
    }
    return () => {
      try { delete window.studentGPTSend } catch (_) {}
    }
  }, [])

  const handleSubmit = (text) => {
    sendMessage(text)
  }

  // Scroll to bottom whenever messages change
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    if (messages.length) {
      scrollToBottom()
    }
  }, [messages.length, scrollToBottom])

  // Save messages to localStorage
  useEffect(() => {
    localStorage.setItem('studentgpt-messages', JSON.stringify(messages))
  }, [messages])

  // Load messages from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('studentgpt-messages')
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages))
      } catch (error) {
        console.error('Error loading saved messages:', error)
      }
    }
  }, [])

  // Memoized MessageComponent to prevent unnecessary rerenders during typing
  const MessageComponent = memo(({ message }) => {
    const { content, role, isError } = message
    const isUser = role === 'user'

    return (
      <div className={`flex items-start ${isUser ? 'justify-end' : 'justify-start'}`}>
        <div className={`relative flex items-start space-x-4 max-w-2xl group ${isUser ? 'flex-row-reverse space-x-reverse ml-20' : 'mr-20'}`}>
          {/* Avatar */}
          <div className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center ${isUser ? 'bg-primary' : 'bg-surface'}`}>
            {isUser ? (
              <User className="w-5 h-5 text-white" />
            ) : (
              <Bot className={`w-5 h-5 ${isError ? 'text-red-500' : 'text-primary'}`} />
            )}
          </div>

          {/* Message Content */}
          <div className={`flex-1 p-4 rounded-2xl ${isUser ? 'bg-primary text-white' : 'bg-chat-bg text-text-color'}`}>
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '')
                  return !inline && match ? (
                    <SyntaxHighlighter
                      {...props}
                      style={tomorrow}
                      language={match[1]}
                      PreTag="div"
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  )
                }
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    )
  }, [])

  return (
    <div className="flex h-full bg-sky-50">
      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="flex justify-between items-center h-16 px-4 bg-white/90 backdrop-blur-md shadow-sm">
          <div className="flex items-center">
            <span className="text-xl font-serif font-medium text-ink">Mahaguru AI</span>
          </div>
        </div>

        {/* Chat Messages */}
        <div 
          className="flex-1 overflow-y-auto px-4 py-6 space-y-6"
          style={{ height: containerHeight }}
          ref={messagesEndRef}
        >
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center h-full text-center px-4"
            >
              <Sparkles className="w-12 h-12 text-primary mb-6" />
              <h1 className="text-2xl font-serif font-bold text-ink mb-2">
                Welcome to Manthan
              </h1>
              <p className="text-muted mb-8 max-w-xl">
                Share your thoughts, questions, and dilemmas. I'm here to help you think through them.
              </p>
            </motion.div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <MessageComponent key={message.id} message={message} />
              ))}

              {/* Loading Indicator */}
              <AnimatePresence>
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="flex items-start space-x-3"
                  >
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                      <Bot className="w-4 h-4 text-primary" />
                    </div>
                    <div className="flex items-center space-x-2 py-3 px-4 rounded-2xl bg-blue-50/80 backdrop-blur-sm max-w-[280px]">
                      <span className="text-sm text-gray-600">StudentGPT is thinking</span>
                      <div className="flex space-x-1">
                        <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                        <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                        <div className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Input Area (hidden if external chatbar is used) */}
        {!(typeof window !== 'undefined' && window.useExternalChatbar) && (
          <div className="flex-shrink-0 border-t border-slate-200 bg-white/85 backdrop-blur-sm p-3 sm:p-4 fixed bottom-2 left-0 right-0">
            <div className="max-w-md mx-auto w-full px-2 sm:px-0">
              <div className="relative rounded-lg shadow-sm">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSubmit(inputValue)
                      setInputValue('')
                    }
                  }}
                  placeholder="Type your message..."
                  className="block w-full rounded-full py-2 pl-3 pr-[44px] bg-white text-[14px] text-ink placeholder:text-slate-400 resize-none border border-slate-300 focus:border-primary focus:ring-2 focus:ring-sky-300/25 focus:outline-none shadow-sm transition-shadow"
                  rows={1}
                  style={{ minHeight: '36px', maxHeight: '84px' }}
                />
                <button
                  onClick={() => {
                    handleSubmit(inputValue)
                    setInputValue('')
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-7 w-7 flex items-center justify-center rounded-full bg-primary hover:bg-primary/90 active:bg-primary-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow focus:outline-none focus:ring-2 focus:ring-sky-300/25"
                  disabled={isLoading || !inputValue.trim()}
                >
                  <Send className="w-3.5 h-3.5 -ml-px" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
