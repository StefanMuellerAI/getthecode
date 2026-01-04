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
        <div className="w-2 h-2 bg-[#4fc3f7] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-[#b0bec5] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-terminal-green rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
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
                    ? 'bg-[#0288d1]/20 border border-[#4fc3f7]/30 text-[#4fc3f7]' 
                    : 'bg-[#0d1f0d] border border-[#2d6a4f]/50 text-terminal-green'
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
                      <span>🧊</span>
                      <span>Winter-KI</span>
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
            <div className="max-w-[85%] rounded-lg p-4 bg-[#0d1f0d] border border-[#2d6a4f]/50">
              <div className="flex items-center gap-2 mb-2 text-xs opacity-60">
                <span>🧊</span>
                <span>Winter-KI</span>
              </div>
              <LoadingIndicator />
            </div>
          </div>
        )}
      </div>
      
      {/* Security Badge - outside scroll area */}
      {messages.length > 0 && !isLoading && (
        <div className="flex items-center justify-center gap-2 text-xs opacity-30 pt-3 mt-2 border-t border-[#0288d1]/10">
          <span>🛡️</span>
          <span>Alle Antworten werden durch das Winter-Sicherheitssystem geprüft</span>
          <span>🛡️</span>
        </div>
      )}
    </div>
  );
}
