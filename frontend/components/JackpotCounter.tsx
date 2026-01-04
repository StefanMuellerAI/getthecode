'use client';

import { useState, useEffect } from 'react';

interface JackpotData {
  amount: number;
  months_active: number;
  start_date: string;
  currency: string;
  code_count: number;
  game_status: string;
}

export default function JackpotCounter() {
  const [jackpot, setJackpot] = useState<JackpotData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchJackpot = async () => {
      try {
        const res = await fetch('/api/jackpot');
        if (res.ok) {
          const data = await res.json();
          setJackpot(data);
        } else {
          throw new Error('Failed to fetch jackpot');
        }
      } catch (e) {
        setError(true);
        // Fallback: Show 0€ and waiting state when API fails
        setJackpot({
          amount: 0,
          months_active: 0,
          start_date: '2025-01-01',
          currency: 'EUR',
          code_count: 0,
          game_status: 'loading'
        });
      }
    };

    fetchJackpot();
    // Refresh jackpot every 30 seconds
    const interval = setInterval(fetchJackpot, 30000);
    return () => clearInterval(interval);
  }, []);

  if (!jackpot) {
    return (
      <div className="terminal-window p-6 text-center">
        <div className="flex justify-center items-center gap-2 mb-2">
          <span className="text-2xl">💎</span>
          <span className="text-xs text-terminal-cyan opacity-70 uppercase tracking-widest">
            Jackpot
          </span>
          <span className="text-2xl">💎</span>
        </div>
        <div className="text-3xl font-bold text-gray-500 animate-pulse">
          Laden...
        </div>
      </div>
    );
  }

  return (
    <div className="terminal-window p-6 text-center gradient-border">
      <div className="flex justify-center items-center gap-2 mb-2">
        <span className="text-2xl frost-glow">💎</span>
        <span className="text-xs text-terminal-cyan opacity-70 uppercase tracking-widest">
          Winter-Jackpot
        </span>
        <span className="text-2xl frost-glow" style={{ animationDelay: '1.5s' }}>💎</span>
      </div>
      
      <div className="jackpot-pulse">
        <span className="text-5xl md:text-7xl font-bold text-[#b0bec5] font-['Orbitron']">
          {jackpot.amount.toLocaleString('de-DE')}€
        </span>
      </div>
      
      <div className="mt-4 flex justify-center gap-6 text-xs opacity-50">
        <div className="flex items-center gap-2">
          <span>🎁</span>
          <span>{jackpot.code_count} Gutschein{jackpot.code_count !== 1 ? 'e' : ''} verfügbar</span>
        </div>
      </div>

      <div className="mt-4 text-xs">
        <span className="text-terminal-green opacity-70">Amazon Gutschein • </span>
        {/* Priority: code_count === 0 always shows "waiting" */}
        {jackpot.code_count === 0 ? (
          <span className="text-gray-400">⏸️ Warte auf neue Codes</span>
        ) : jackpot.game_status === 'won' ? (
          <span className="text-yellow-400">🏆 Gewonnen!</span>
        ) : jackpot.game_status === 'pending_claim' ? (
          <span className="text-blue-400">⏳ Claim wird geprüft</span>
        ) : jackpot.game_status === 'redeemed' ? (
          <span className="text-gray-400">⏸️ Eingelöst - warte auf neue Codes</span>
        ) : (
          <span className="text-[#4fc3f7]">🔒 Noch nicht geknackt</span>
        )}
      </div>
    </div>
  );
}
