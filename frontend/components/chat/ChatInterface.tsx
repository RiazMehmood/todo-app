'use client';

/**
 * Chat Interface Component (Phase III - US1)
 *
 * Provides a chat interface for AI-powered task management.
 * Users can create, query, update, and delete tasks via natural language.
 */

import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import { Message } from '@/lib/types';
import Link from 'next/link';

interface ChatInterfaceProps {
  userId: string;
  onTaskCreated?: () => void; // Callback to refresh task list
}

export function ChatInterface({ userId, onTaskCreated }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'network' | 'server' | 'validation' | null>(null);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);
  const [aiEnabled, setAiEnabled] = useState<boolean | null>(null); // null = loading
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load AI preferences and chat history on mount
  useEffect(() => {
    loadAIPreferences();
    loadChatHistory();
  }, [userId]);

  const loadAIPreferences = async () => {
    try {
      const preferences = await api.getAIPreferences(userId);
      setAiEnabled(preferences.ai_enabled || false);
    } catch (err: any) {
      console.error('Error loading AI preferences:', err);
      setAiEnabled(false); // Default to disabled if error
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const history = await api.getChatHistory(userId);
      setMessages(history.messages);
    } catch (err: any) {
      console.error('Error loading chat history:', err);
      // Don't show error for empty history
      if (!err.message.includes('404')) {
        setError('Failed to load chat history');
      }
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) {
      return;
    }

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);
    setIsLoading(true);

    // Add user message optimistically
    const tempUserMessage: Message = {
      id: Date.now(),
      user_id: userId,
      conversation_id: 0,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, tempUserMessage]);

    try {
      // Send message to API
      const response = await api.sendChatMessage(userId, userMessage);

      // Add assistant response
      const assistantMessage: Message = {
        id: response.assistant_message_id,
        user_id: userId,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.response,
        created_at: new Date().toISOString(),
        language: response.language,
        related_task_id: response.related_task_id,
      };

      setMessages(prev => [
        ...prev.filter(m => m.id !== tempUserMessage.id),
        {
          ...tempUserMessage,
          id: response.user_message_id,
          conversation_id: response.conversation_id,
        },
        assistantMessage,
      ]);

      // Clear any previous errors
      setError(null);
      setErrorType(null);
      setLastFailedMessage(null);

      // Trigger callback if any task operation occurred (create, update, delete, complete)
      const responseText = response.response.toLowerCase();
      const taskOperationKeywords = [
        'created', 'added', 'complete', 'completed', 'marked',
        'deleted', 'removed', 'updated', 'changed', 'renamed'
      ];

      if (onTaskCreated && taskOperationKeywords.some(keyword => responseText.includes(keyword))) {
        onTaskCreated();
      }
    } catch (err: any) {
      console.error('Error sending message:', err);

      // Categorize error type
      let errorMessage = '';
      let type: 'network' | 'server' | 'validation' = 'server';

      if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        errorMessage = 'Unable to connect to the server. Please check your internet connection.';
        type = 'network';
      } else if (err.message.includes('AI chatbot is disabled')) {
        errorMessage = 'AI chatbot is disabled. Please enable it in settings.';
        type = 'validation';
      } else if (err.message.includes('rate limit') || err.message.includes('quota')) {
        errorMessage = 'AI service is temporarily unavailable due to rate limits. Please try again in a few moments.';
        type = 'server';
      } else if (err.message.includes('500') || err.message.includes('Internal')) {
        errorMessage = 'The AI service encountered an error. Please try again.';
        type = 'server';
      } else {
        errorMessage = err.message || 'Failed to send message. Please try again.';
      }

      setError(errorMessage);
      setErrorType(type);
      setLastFailedMessage(userMessage); // Store for retry

      // Remove optimistic message
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastFailedMessage) {
      setInputMessage(lastFailedMessage);
      setError(null);
      setErrorType(null);
      setLastFailedMessage(null);
      // Auto-send after a brief delay
      setTimeout(() => {
        const form = document.querySelector('form');
        if (form) {
          form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        }
      }, 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e as any);
    }
  };

  // If AI preferences are still loading
  if (aiEnabled === null) {
    return (
      <div className="bg-white rounded-lg shadow flex flex-col h-[400px] sm:h-[500px] md:h-[600px]">
        <div className="flex items-center justify-center h-full">
          <div className="animate-pulse text-gray-400">
            <svg className="h-10 w-10 sm:h-12 sm:w-12 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <p className="text-xs sm:text-sm">Loading chat...</p>
          </div>
        </div>
      </div>
    );
  }

  // If AI is disabled, show disabled/blurred UI
  if (!aiEnabled) {
    return (
      <div className="bg-white rounded-lg shadow flex flex-col h-[400px] sm:h-[500px] md:h-[600px] relative">
        {/* Blurred background chat */}
        <div className="absolute inset-0 blur-sm pointer-events-none opacity-50">
          <div className="px-4 py-3 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">AI Task Assistant</h2>
            <p className="text-xs text-gray-600">Chat in English or Urdu to manage your tasks</p>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <div className="flex justify-end">
              <div className="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-[75%]">
                <p className="text-sm">Create a task to buy groceries</p>
              </div>
            </div>
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-2 max-w-[75%]">
                <p className="text-sm">I can help you with that!</p>
              </div>
            </div>
          </div>
          <div className="px-4 py-3 border-t border-gray-200">
            <div className="flex gap-2">
              <input type="text" className="flex-1 px-4 py-2 border border-gray-300 rounded-lg" placeholder="Type your message..." />
              <button className="px-6 py-2 bg-blue-600 text-white rounded-lg">Send</button>
            </div>
          </div>
        </div>

        {/* Overlay with enable message */}
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm p-4">
          <div className="text-center px-4 sm:px-6 py-6 sm:py-8 max-w-md">
            <div className="mb-4 sm:mb-6">
              <svg className="h-14 w-14 sm:h-20 sm:w-20 mx-auto text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-lg sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-3">AI Chatbot is Disabled</h3>
            <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">
              Enable the AI chatbot in your settings to start chatting and managing tasks with natural language.
            </p>
            <Link
              href="/settings"
              className="inline-flex items-center px-4 sm:px-6 py-2 sm:py-3 bg-blue-600 text-white text-sm sm:text-base font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
            >
              <svg className="h-4 w-4 sm:h-5 sm:w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Go to Settings
            </Link>
            <p className="text-xs text-gray-500 mt-3 sm:mt-4">
              You can enable or disable AI features at any time
            </p>
          </div>
        </div>
      </div>
    );
  }

  // AI is enabled, show normal chat interface
  return (
    <div className="bg-white rounded-lg shadow flex flex-col h-[400px] sm:h-[500px] md:h-[600px]">
      {/* Header */}
      <div className="px-3 sm:px-4 py-2 sm:py-3 border-b border-gray-200">
        <h2 className="text-base sm:text-lg font-semibold text-gray-900">AI Task Assistant</h2>
        <p className="text-xs text-gray-600 hidden sm:block">
          Chat in English or Urdu to manage your tasks
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8 sm:py-12 px-4">
            <div className="text-gray-400 mb-3 sm:mb-4">
              <svg
                className="mx-auto h-10 w-10 sm:h-12 sm:w-12"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </div>
            <p className="text-sm sm:text-base text-gray-600 font-medium">Start a conversation</p>
            <p className="text-xs sm:text-sm text-gray-500 mt-2">
              Try: "Add a task to buy groceries"
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[75%] rounded-lg px-3 sm:px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-xs sm:text-sm whitespace-pre-wrap break-words">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.role === 'user'
                        ? 'text-blue-100'
                        : 'text-gray-500'
                    }`}
                  >
                    {new Date(message.created_at).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '0ms' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '150ms' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: '300ms' }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className={`px-4 py-3 border-t ${
          errorType === 'network' ? 'bg-orange-50 border-orange-200' :
          errorType === 'validation' ? 'bg-yellow-50 border-yellow-200' :
          'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-2 flex-1">
              {/* Error Icon */}
              <svg
                className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
                  errorType === 'network' ? 'text-orange-500' :
                  errorType === 'validation' ? 'text-yellow-600' :
                  'text-red-500'
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {errorType === 'network' ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                )}
              </svg>
              <p className={`text-sm flex-1 ${
                errorType === 'network' ? 'text-orange-800' :
                errorType === 'validation' ? 'text-yellow-800' :
                'text-red-800'
              }`}>
                {error}
              </p>
            </div>
            {/* Retry Button (only for network and server errors) */}
            {lastFailedMessage && errorType !== 'validation' && (
              <button
                onClick={handleRetry}
                className={`flex-shrink-0 px-3 py-1 text-xs font-medium rounded transition-colors ${
                  errorType === 'network'
                    ? 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                    : 'bg-red-100 text-red-700 hover:bg-red-200'
                }`}
              >
                <svg className="inline h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Retry
              </button>
            )}
            {/* Dismiss Button */}
            <button
              onClick={() => {
                setError(null);
                setErrorType(null);
                setLastFailedMessage(null);
              }}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600"
              aria-label="Dismiss error"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="px-3 sm:px-4 py-2 sm:py-3 border-t border-gray-200">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 text-sm sm:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            maxLength={2000}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 sm:px-6 py-2 sm:py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            aria-label={isLoading ? 'Sending...' : 'Send message'}
          >
            {isLoading ? (
              <svg
                className="animate-spin h-4 w-4 sm:h-5 sm:w-5"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
              <svg
                className="h-4 w-4 sm:h-5 sm:w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-1.5 sm:mt-2 hidden sm:block">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
