import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Impressum | LinkedIn Christmas Code Challenge',
  description: 'Impressum und rechtliche Informationen',
};

export default function Impressum() {
  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col items-center relative z-10">
      {/* Back Navigation */}
      <div className="w-full max-w-4xl mb-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-terminal-green/70 hover:text-terminal-green transition-colors duration-200 text-sm"
        >
          <span>←</span>
          <span>Zurück zur Challenge</span>
        </Link>
      </div>

      {/* Terminal Window */}
      <div className="w-full max-w-4xl terminal-window">
        {/* Terminal Header */}
        <div className="terminal-header">
          <div className="terminal-dot red" />
          <div className="terminal-dot yellow" />
          <div className="terminal-dot green" />
          <span className="ml-4 text-sm opacity-50">
            📜 cat /legal/impressum.txt
          </span>
        </div>

        {/* Content */}
        <div className="p-6 md:p-8 space-y-8 text-sm md:text-base">
          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-2xl md:text-3xl font-bold text-[#ffd700] glow-text-gold font-['Orbitron'] mb-2">
              IMPRESSUM
            </h1>
            <div className="h-px w-32 mx-auto bg-gradient-to-r from-transparent via-terminal-green to-transparent" />
          </div>

          {/* Main Info */}
          <section>
            <p className="text-terminal-green font-semibold mb-2">Stefan Müller</p>
            <p className="text-terminal-green/80">StefanAI – Research & Development</p>
            <p className="text-terminal-green/80">Graeffstr. 22</p>
            <p className="text-terminal-green/80">50823 Köln</p>
          </section>

          {/* Contact */}
          <section>
            <h2 className="text-terminal-cyan font-semibold mb-2">{'>'} Kontakt</h2>
            <p className="text-terminal-green/80">Telefon: 0221/5702984</p>
            <p className="text-terminal-green/80">
              E-Mail:{' '}
              <a
                href="mailto:info@stefanai.de"
                className="text-terminal-green hover:glow-text transition-all duration-200"
              >
                info@stefanai.de
              </a>
            </p>
          </section>

          {/* VAT */}
          <section>
            <h2 className="text-terminal-cyan font-semibold mb-2">{'>'} Umsatzsteuer-ID</h2>
            <p className="text-terminal-green/80">
              Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:
            </p>
            <p className="text-terminal-green font-mono">DE347707954</p>
          </section>

          {/* Editorial */}
          <section>
            <h2 className="text-terminal-cyan font-semibold mb-2">{'>'} Redaktionell verantwortlich</h2>
            <p className="text-terminal-green/80">Stefan Müller</p>
            <p className="text-terminal-green/80">Graeffstr. 22</p>
            <p className="text-terminal-green/80">50823 Köln</p>
          </section>

          {/* EU Dispute Resolution */}
          <section>
            <h2 className="text-terminal-cyan font-semibold mb-2">{'>'} EU-Streitschlichtung</h2>
            <p className="text-terminal-green/80 mb-2">
              Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:{' '}
              <a
                href="https://ec.europa.eu/consumers/odr/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-terminal-amber hover:glow-text-gold transition-all duration-200 break-all"
              >
                https://ec.europa.eu/consumers/odr/
              </a>
            </p>
            <p className="text-terminal-green/80">
              Unsere E-Mail-Adresse finden Sie oben im Impressum.
            </p>
          </section>

          {/* Consumer Dispute */}
          <section>
            <h2 className="text-terminal-cyan font-semibold mb-2">{'>'} Verbraucherstreitbeilegung/Universalschlichtungsstelle</h2>
            <p className="text-terminal-green/80">
              Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
              Verbraucherschlichtungsstelle teilzunehmen.
            </p>
          </section>

          {/* Footer */}
          <div className="pt-6 border-t border-terminal-green/20 text-center">
            <Link
              href="/datenschutz"
              className="inline-flex items-center gap-2 text-terminal-green/70 hover:text-terminal-green transition-colors duration-200 text-sm"
            >
              <span>Zur Datenschutzerklärung →</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Back to Home */}
      <div className="mt-8 text-center">
        <Link
          href="/"
          className="text-xs text-terminal-green/40 hover:text-terminal-green transition-colors duration-200"
        >
          🎄 Zurück zur Christmas Code Challenge 🎄
        </Link>
      </div>
    </main>
  );
}

