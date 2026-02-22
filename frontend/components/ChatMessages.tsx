'use client';

import { useEffect, useRef, useState } from 'react';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onTypingComplete?: () => void;
}

function TypingMessage({ content, onComplete }: { content: string; onComplete?: () => void }) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    setDisplayedText('');
    setIsTyping(true);
    
    let index = 0;
    const typingSpeed = 12;
    
    const timer = setInterval(() => {
      if (index < content.length) {
        setDisplayedText(content.substring(0, index + 1));
        index++;
      } else {
        setIsTyping(false);
        clearInterval(timer);
        if (onComplete) {
          onComplete();
        }
      }
    }, typingSpeed);

    return () => clearInterval(timer);
  }, [content, onComplete]);

  return (
    <div className="whitespace-pre-wrap leading-relaxed">
      {displayedText}
      {isTyping && <span className="typing-cursor" />}
    </div>
  );
}

function LoadingIndicator() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-[#00d26a] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-[#7ec850] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-[#ffd700] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-sm opacity-70">Die KI-Wächter beraten sich...</span>
    </div>
  );
}

export default function ChatMessages({ messages, isLoading, onTypingComplete }: ChatMessagesProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [lastMessageIndex, setLastMessageIndex] = useState(-1);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  // Track which message is the newest to apply typing effect
  useEffect(() => {
    if (messages.length > lastMessageIndex + 1) {
      setLastMessageIndex(messages.length - 1);
    }
  }, [messages.length, lastMessageIndex]);

  if (messages.length === 0 && !isLoading) {
    return null;
  }

  return (
    <div className="flex flex-col">
      {/* Scrollable chat container with fixed height */}
      <div 
        ref={containerRef}
        className="h-[350px] overflow-y-auto space-y-4 pr-2"
      >
        {messages.map((message, index) => {
          const isUser = message.role === 'user';
          const isNewestAssistant = !isUser && index === lastMessageIndex && index === messages.length - 1;
          
          return (
            <div
              key={index}
              className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`
                  max-w-[85%] rounded-lg p-4 
                  ${isUser 
                    ? 'bg-[#0d1a0d]/40 border border-[#2d8f4e]/30 text-[#7ec850]' 
                    : 'bg-[#0a140a] border border-[#1a3a1a]/50 text-terminal-green'
                  }
                `}
              >
                {/* Message Header */}
                <div className="flex items-center gap-2 mb-2 text-xs opacity-60">
                  {isUser ? (
                    <>
                      <span>👤</span>
                      <span>Du</span>
                    </>
                  ) : (
                    <>
                      <span>🌿</span>
                      <span>Garten-KI</span>
                    </>
                  )}
                </div>
                
                {/* Message Content */}
                {isNewestAssistant ? (
                  <TypingMessage content={message.content} onComplete={onTypingComplete} />
                ) : (
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        
        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-lg p-4 bg-[#0a140a] border border-[#1a3a1a]/50">
              <div className="flex items-center gap-2 mb-2 text-xs opacity-60">
                <span>🌿</span>
                <span>Garten-KI</span>
              </div>
              <LoadingIndicator />
            </div>
          </div>
        )}
      </div>
      
      {/* Security Badge - outside scroll area */}
      {messages.length > 0 && !isLoading && (
        <div className="flex items-center justify-center gap-2 text-xs opacity-30 pt-3 mt-2 border-t border-[#00d26a]/10">
          <span>🌿</span>
          <span>Alle Antworten werden durch das Sicherheitssystem geprüft</span>
          <span>🌿</span>
        </div>
      )}
    </div>
  );
}
