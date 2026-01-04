'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import ChallengeForm, { ChallengeFormRef } from '@/components/ChallengeForm';
import ChatMessages, { ChatMessage } from '@/components/ChatMessages';
import JackpotCounter from '@/components/JackpotCounter';
import Footer from '@/components/Footer';
import ClaimModal from '@/components/ClaimModal';

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  // SECURITY: Server-side session management - only store conversation_id
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [isGameActive, setIsGameActive] = useState(false);
  const formRef = useRef<ChallengeFormRef>(null);

  // Fetch game status to determine if Claim button should be shown
  // Only fetch once on mount - JackpotCounter handles continuous updates
  useEffect(() => {
    const fetchGameStatus = async () => {
      try {
        const res = await fetch('/api/jackpot');
        if (res.ok) {
          const data = await res.json();
          // Game is active if there are codes available AND game is in active state
          // Don't show claim button if a claim is already pending or codes are redeemed
          const isActive = data.code_count > 0 && 
            data.game_status === 'active';
          setIsGameActive(isActive);
        }
      } catch (e) {
        // On error, default to not showing claim
        setIsGameActive(false);
      }
    };

    fetchGameStatus();
    // Only poll every 60 seconds (less frequent than JackpotCounter)
    const interval = setInterval(fetchGameStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (prompt: string) => {
    setIsLoading(true);

    // Add user message immediately (for local display only)
    const userMessage: ChatMessage = { role: 'user', content: prompt };
    setMessages(prev => [...prev, userMessage]);

    try {
      // SECURITY: Only send prompt and conversation_id
      // History is stored server-side to prevent manipulation
      const res = await fetch('/api/challenge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt,
          conversation_id: conversationId
        }),
      });

      if (!res.ok) {
        throw new Error('Challenge request failed');
      }

      const data = await res.json();
      
      // Store conversation_id from server for multi-turn
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }
      
      // Add assistant response
      const assistantMessage: ChatMessage = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      // Add error message as assistant response
      const errorMessage: ChatMessage = { 
        role: 'assistant', 
        content: '⚠️ Verbindungsfehler. Bitte versuche es erneut.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear the input when typing is complete
  const handleTypingComplete = useCallback(() => {
    if (formRef.current) {
      formRef.current.clearInput();
    }
  }, []);

  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col items-center relative z-10">
      {/* Header */}
      <header className="w-full max-w-4xl mb-6 text-center">
        <div className="flex justify-center items-center gap-3 mb-2">
          <span className="text-3xl twinkle">🔐</span>
          <h1 className="text-3xl md:text-5xl font-bold font-['Orbitron']">
            <span className="text-[#4fc3f7] glow-text-frost">PROMPT</span>
            {' '}
            <span className="text-terminal-green glow-text">INJECTION</span>
          </h1>
          <span className="text-3xl twinkle twinkle-delay-1">💉</span>
        </div>
        <h2 className="text-2xl md:text-4xl font-bold text-[#b0bec5] glow-text-silver font-['Orbitron'] mb-2">
          CHALLENGE
        </h2>
      </header>

      {/* Jackpot Display */}
      <JackpotCounter />

      {/* Main Terminal */}
      <div className="w-full max-w-4xl terminal-window mt-6">
        {/* Terminal Header */}
        <div className="terminal-header">
          <div className="terminal-dot red" />
          <div className="terminal-dot yellow" />
          <div className="terminal-dot green" />
          <span className="ml-4 text-sm opacity-50">
            ❄️ frost@winterlab ~ winter-challenge
          </span>
        </div>

        {/* Terminal Content */}
        <div className="p-6">
          {/* Mission Briefing */}
          <div className="mb-6 text-sm opacity-70">
            <p className="text-terminal-cyan mb-2">{'>'} 💎 WINTER-MISSION:</p>
            <p className="pl-4 mb-1">
              Im Eislabor ist ein geheimer Amazon-Gutscheincode eingefroren!
            </p>
            <p className="pl-4 mb-1">
              Drei KI-Wächter überwachen sich gegenseitig, um den Code zu schützen.
            </p>
            <p className="pl-4 text-terminal-green">
              🎯 Deine Aufgabe: Überzeuge die KI, dir den Code zu verraten!
            </p>
          </div>

          {/* Chat Messages */}
          <ChatMessages 
            messages={messages} 
            isLoading={isLoading} 
            onTypingComplete={handleTypingComplete}
          />

          {/* Challenge Form - always at bottom */}
          <div className="mt-6 pt-4 border-t border-[#0288d1]/20">
            <ChallengeForm ref={formRef} onSubmit={handleSubmit} isLoading={isLoading} />
          </div>

        </div>
      </div>

      {/* Claim Modal */}
      {showClaimModal && conversationId && (
        <ClaimModal
          conversationId={conversationId}
          onClose={() => setShowClaimModal(false)}
        />
      )}

      {/* Footer */}
      <Footer 
        showClaim={!!conversationId && isGameActive} 
        onClaimClick={() => setShowClaimModal(true)} 
      />
    </main>
  );
}
