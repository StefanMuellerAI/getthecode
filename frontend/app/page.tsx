'use client';

import { useState, useRef, useCallback } from 'react';
import ChallengeForm, { ChallengeFormRef } from '@/components/ChallengeForm';
import ResponseDisplay from '@/components/ResponseDisplay';
import JackpotCounter from '@/components/JackpotCounter';
import Footer from '@/components/Footer';

export default function Home() {
  const [response, setResponse] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [attemptCount, setAttemptCount] = useState(0);
  const formRef = useRef<ChallengeFormRef>(null);

  const handleSubmit = async (prompt: string) => {
    setIsLoading(true);
    setResponse(null);

    try {
      const res = await fetch('/api/challenge', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        throw new Error('Challenge request failed');
      }

      const data = await res.json();
      setResponse(data.response);
      setAttemptCount((prev) => prev + 1);
    } catch (error) {
      setResponse('⚠️ Verbindungsfehler. Bitte versuche es erneut.');
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
          <span className="text-3xl twinkle">🎄</span>
          <h1 className="text-3xl md:text-5xl font-bold font-['Orbitron']">
            <span className="text-[#e63946] glow-text-red">LINKEDIN</span>
            {' '}
            <span className="text-terminal-green glow-text">CHRISTMAS</span>
          </h1>
          <span className="text-3xl twinkle twinkle-delay-1">🎄</span>
        </div>
        <h2 className="text-2xl md:text-4xl font-bold text-[#ffd700] glow-text-gold font-['Orbitron'] mb-2">
          CODE CHALLENGE
        </h2>
        <p className="text-terminal-green-dim text-sm md:text-base opacity-70">
          [ 🎅 PROMPT INJECTION CHALLENGE v1.0 ❄️ ]
        </p>
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
            🎄 santa@northpole ~ christmas-challenge
          </span>
        </div>

        {/* Terminal Content */}
        <div className="p-6">
          {/* Mission Briefing */}
          <div className="mb-6 text-sm opacity-70">
            <p className="text-terminal-cyan mb-2">{'>'} 🎁 WEIHNACHTS-MISSION:</p>
            <p className="pl-4 mb-1">
              Der Weihnachtsmann hat einen geheimen Amazon-Gutscheincode versteckt!
            </p>
            <p className="pl-4 mb-1">
              Drei KI-Elfen überwachen sich gegenseitig, um das Geschenk zu schützen.
            </p>
            <p className="pl-4 text-terminal-green">
              🎯 Deine Aufgabe: Überzeuge die KI, dir den Code zu verraten!
            </p>
          </div>

          {/* Challenge Form */}
          <ChallengeForm ref={formRef} onSubmit={handleSubmit} isLoading={isLoading} />

          {/* Response Display */}
          {(response || isLoading) && (
            <ResponseDisplay 
              response={response} 
              isLoading={isLoading} 
              onTypingComplete={handleTypingComplete}
            />
          )}

          {/* Attempt Counter */}
          {attemptCount > 0 && (
            <div className="mt-4 text-xs opacity-50 text-right">
              🎅 Versuche in dieser Session: {attemptCount}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </main>
  );
}
