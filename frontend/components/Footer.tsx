'use client';

import Link from 'next/link';

interface FooterProps {
  onClaimClick?: () => void;
  showClaim?: boolean;
}

export default function Footer({ onClaimClick, showClaim = false }: FooterProps) {
  return (
    <footer className="mt-12 w-full max-w-4xl">
      {/* Divider */}
      <div className="flex items-center justify-center gap-4 mb-6">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-terminal-green/30 to-transparent" />
        <span className="text-terminal-green/40 text-xs">❄️ ❄️ ❄️</span>
        <div className="h-px flex-1 bg-gradient-to-l from-transparent via-terminal-green/30 to-transparent" />
      </div>

      {/* Links */}
      <div className="flex flex-col items-center gap-4">
        <div className="flex gap-6 text-xs">
          <Link
            href="/impressum"
            className="text-terminal-green/50 hover:text-terminal-green transition-colors duration-200 hover:glow-text"
          >
            [ Impressum ]
          </Link>
          <Link
            href="/datenschutz"
            className="text-terminal-green/50 hover:text-terminal-green transition-colors duration-200 hover:glow-text"
          >
            [ Datenschutz ]
          </Link>
          {showClaim && onClaimClick && (
            <button
              onClick={onClaimClick}
              className="text-amber-400 hover:text-yellow-300 transition-colors duration-200 animate-pulse"
              style={{ 
                textShadow: '0 0 10px rgba(251, 191, 36, 0.5), 0 0 20px rgba(251, 191, 36, 0.3)' 
              }}
            >
              [ 🏆 Claim ]
            </button>
          )}
        </div>

        {/* Copyright */}
        <div className="text-center text-xs opacity-30">
          <p>❄️ Drei KI-Wächter. Ein Geheimnis. Kannst du es lüften? 💎</p>
          <p className="mt-1">© 2026 Prompt Injection Challenge | StefanAI – Research & Development</p>
        </div>
      </div>
    </footer>
  );
}
