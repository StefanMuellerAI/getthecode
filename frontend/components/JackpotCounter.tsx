'use client';

import { useState, useEffect } from 'react';

interface JackpotData {
  amount: number;
  months_active: number;
  start_date: string;
  currency: string;
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
        // Fallback to calculated value
        const startDate = new Date('2025-01-01');
        const now = new Date();
        const months = Math.max(1, 
          (now.getFullYear() - startDate.getFullYear()) * 12 + 
          (now.getMonth() - startDate.getMonth()) + 1
        );
        setJackpot({
          amount: months * 100,
          months_active: months,
          start_date: '2025-01-01',
          currency: 'EUR'
        });
      }
    };

    fetchJackpot();
    // Refresh jackpot every minute
    const interval = setInterval(fetchJackpot, 60000);
    return () => clearInterval(interval);
  }, []);

  if (!jackpot) {
    return (
      <div className="terminal-window p-4 animate-pulse">
        <div className="h-16 bg-terminal-border rounded" />
      </div>
    );
  }

  return (
    <div className="terminal-window p-6 text-center gradient-border">
      <div className="flex justify-center items-center gap-2 mb-2">
        <span className="text-2xl ornament-glow">🎁</span>
        <span className="text-xs text-terminal-cyan opacity-70 uppercase tracking-widest">
          Weihnachts-Jackpot
        </span>
        <span className="text-2xl ornament-glow" style={{ animationDelay: '1.5s' }}>🎁</span>
      </div>
      
      <div className="jackpot-pulse">
        <span className="text-5xl md:text-7xl font-bold text-[#ffd700] font-['Orbitron']">
          {jackpot.amount.toLocaleString('de-DE')}€
        </span>
      </div>
      
      <div className="mt-4 flex justify-center gap-6 text-xs opacity-50">
        <div className="flex items-center gap-2">
          <span>📅</span>
          <span>Monat {jackpot.months_active}</span>
        </div>
        <div className="flex items-center gap-2">
          <span>🎄</span>
          <span>+100€ jeden Monat</span>
        </div>
      </div>

      <div className="mt-4 text-xs">
        <span className="text-terminal-green opacity-70">Amazon Gutschein • </span>
        <span className="text-[#e63946]">🔒 Noch nicht geknackt</span>
      </div>
    </div>
  );
}
