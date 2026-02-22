'use client';

import { useState, useEffect } from 'react';

interface ResponseDisplayProps {
  response: string | null;
  isLoading: boolean;
  onTypingComplete?: () => void;
}

export default function ResponseDisplay({ response, isLoading, onTypingComplete }: ResponseDisplayProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Typing effect
  useEffect(() => {
    if (response && !isLoading) {
      setIsTyping(true);
      setDisplayedText('');
      
      let index = 0;
      const typingSpeed = 12;
      
      const timer = setInterval(() => {
        if (index < response.length) {
          setDisplayedText(response.substring(0, index + 1));
          index++;
        } else {
          setIsTyping(false);
          clearInterval(timer);
          // Notify parent that typing is complete
          if (onTypingComplete) {
            onTypingComplete();
          }
        }
      }, typingSpeed);

      return () => clearInterval(timer);
    }
  }, [response, isLoading, onTypingComplete]);

  return (
    <div className="mt-6 pt-6 border-t-2 border-[#00d26a]/30">
      {/* Response Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-3 h-3 rounded-full ${isLoading ? 'bg-terminal-amber animate-pulse' : 'bg-terminal-green'}`} />
        <span className="text-[#7ec850] text-sm font-bold uppercase tracking-wider">
          🌿 Antwort der Garten-KI:
        </span>
      </div>

      {/* Response Content */}
      <div className="bg-[#0a140a] border border-[#00d26a]/30 rounded-lg p-4 shadow-lg shadow-[#00d26a]/5">
        {isLoading ? (
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-[#00d26a] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-[#7ec850] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-[#ffd700] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-sm opacity-70">Die KI-Wächter beraten sich...</span>
          </div>
        ) : (
          <div className="whitespace-pre-wrap leading-relaxed text-terminal-green">
            {displayedText}
            {isTyping && <span className="typing-cursor" />}
          </div>
        )}
      </div>

      {/* Security Badge */}
      {!isLoading && response && !isTyping && (
        <div className="mt-3 flex items-center justify-center gap-2 text-xs opacity-40">
          <span>🌿</span>
          <span>Geprüft durch das Sicherheitssystem</span>
          <span>🌿</span>
        </div>
      )}
    </div>
  );
}
