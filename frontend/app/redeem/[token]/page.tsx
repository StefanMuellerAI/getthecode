'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface GiftCode {
  id: number;
  code: string;
  value: number;
}

interface RedemptionResult {
  success: boolean;
  codes: GiftCode[];
  total_value: number;
  message: string;
  error?: string;
}

export default function RedeemPage() {
  const params = useParams();
  const token = params.token as string;
  const [result, setResult] = useState<RedemptionResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [copied, setCopied] = useState<number | null>(null);

  useEffect(() => {
    const redeemCodes = async () => {
      try {
        const response = await fetch(`/api/redeem/${token}`);
        const data = await response.json();

        if (response.ok) {
          setResult({
            success: true,
            codes: data.codes,
            total_value: data.total_value,
            message: data.message,
          });
        } else {
          setResult({
            success: false,
            codes: [],
            total_value: 0,
            message: data.detail || 'Ein Fehler ist aufgetreten.',
          });
        }
      } catch (error) {
        setResult({
          success: false,
          codes: [],
          total_value: 0,
          message: 'Verbindungsfehler. Bitte versuche es später erneut.',
        });
      } finally {
        setIsLoading(false);
      }
    };

    if (token) {
      redeemCodes();
    }
  }, [token]);

  const copyCode = async (code: string, id: number) => {
    await navigator.clipboard.writeText(code);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-6xl mb-6 animate-bounce">🎁</div>
          <h1 className="text-2xl font-bold text-terminal-green mb-4">
            Einlösung wird verarbeitet...
          </h1>
          <div className="flex justify-center gap-2">
            <div className="w-3 h-3 bg-terminal-green rounded-full animate-pulse" />
            <div className="w-3 h-3 bg-terminal-green rounded-full animate-pulse delay-100" />
            <div className="w-3 h-3 bg-terminal-green rounded-full animate-pulse delay-200" />
          </div>
        </div>
      </main>
    );
  }

  if (!result?.success) {
    return (
      <main className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-lg w-full bg-[#0d1117] border border-red-500/50 rounded-xl p-8 text-center">
          <div className="text-6xl mb-6">❌</div>
          <h1 className="text-2xl font-bold text-red-400 mb-4">
            Einlösung fehlgeschlagen
          </h1>
          <p className="text-gray-400 mb-6">{result?.message}</p>
          <Link 
            href="/"
            className="inline-block px-6 py-3 bg-[#21262d] text-white rounded-lg hover:bg-[#30363d] transition-colors"
          >
            Zurück zur Challenge
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Confetti Animation Background */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-confetti"
            style={{
              left: `${Math.random() * 100}%`,
              top: `-10%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${3 + Math.random() * 2}s`,
            }}
          >
            {['🎉', '🎊', '✨', '🌟', '💰', '🏆'][Math.floor(Math.random() * 6)]}
          </div>
        ))}
      </div>

      <div className="max-w-2xl w-full bg-gradient-to-b from-[#0d1117] to-[#161b22] border-2 border-yellow-500/50 rounded-2xl p-8 shadow-2xl shadow-yellow-500/20 relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-7xl mb-4 animate-bounce">🏆</div>
          <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-amber-500 mb-2">
            HERZLICHEN GLÜCKWUNSCH!
          </h1>
          <p className="text-xl text-terminal-green font-bold">
            Du hast die KI überlistet!
          </p>
        </div>

        {/* Total Value */}
        <div className="bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border border-yellow-500/50 rounded-xl p-6 mb-6 text-center">
          <p className="text-gray-400 text-sm mb-1">Dein Gewinn</p>
          <p className="text-5xl font-bold text-yellow-400">
            {result.total_value}€
          </p>
          <p className="text-gray-400 mt-2">
            in Amazon-Gutscheinen
          </p>
        </div>

        {/* Gift Codes */}
        <div className="space-y-4 mb-8">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span>🎁</span>
            Deine Gutscheincodes:
          </h2>
          
          {result.codes.map((code) => (
            <div
              key={code.id}
              className="bg-[#0d1117] border border-[#30363d] rounded-lg p-4 flex items-center justify-between"
            >
              <div>
                <code className="text-xl font-mono text-terminal-green font-bold tracking-wider">
                  {code.code}
                </code>
                <p className="text-sm text-gray-400 mt-1">
                  Wert: {code.value}€
                </p>
              </div>
              <button
                onClick={() => copyCode(code.code, code.id)}
                className={`px-4 py-2 rounded-lg font-bold transition-all ${
                  copied === code.id
                    ? 'bg-green-500 text-white'
                    : 'bg-[#21262d] text-gray-300 hover:bg-[#30363d]'
                }`}
              >
                {copied === code.id ? '✓ Kopiert!' : '📋 Kopieren'}
              </button>
            </div>
          ))}
        </div>

        {/* Warning */}
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6">
          <p className="text-red-400 text-sm flex items-start gap-2">
            <span className="text-lg">⚠️</span>
            <span>
              <strong>WICHTIG:</strong> Diese Seite kann nur EINMAL aufgerufen werden! 
              Mach einen Screenshot oder kopiere die Codes JETZT!
            </span>
          </p>
        </div>

        {/* Instructions */}
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-6">
          <p className="text-blue-300 text-sm">
            <strong>So löst du die Codes ein:</strong><br />
            1. Gehe zu amazon.de/gc/redeem<br />
            2. Melde dich in deinem Amazon-Konto an<br />
            3. Gib den Gutscheincode ein<br />
            4. Der Betrag wird deinem Konto gutgeschrieben
          </p>
        </div>

        {/* Back Link */}
        <div className="text-center">
          <Link 
            href="/"
            className="text-terminal-cyan hover:underline"
          >
            ← Zurück zur Challenge
          </Link>
        </div>
      </div>

      <style jsx global>{`
        @keyframes confetti {
          0% {
            transform: translateY(-10vh) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(110vh) rotate(720deg);
            opacity: 0;
          }
        }
        .animate-confetti {
          animation: confetti linear infinite;
        }
      `}</style>
    </main>
  );
}

