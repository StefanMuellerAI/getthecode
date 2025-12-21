'use client';

import Link from 'next/link';

export default function Footer() {
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
        </div>

        {/* Copyright */}
        <div className="text-center text-xs opacity-30">
          <p>🎄 Drei KI-Elfen. Ein Geschenk. Kannst du es auspacken? 🎁</p>
          <p className="mt-1">© 2024 LinkedIn Christmas Code Challenge | StefanAI – Research & Development</p>
        </div>
      </div>
    </footer>
  );
}

