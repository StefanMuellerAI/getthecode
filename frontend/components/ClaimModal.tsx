'use client';

import { useState } from 'react';

interface ClaimModalProps {
  conversationId: string;
  onClose: () => void;
}

export default function ClaimModal({ conversationId, onClose }: ClaimModalProps) {
  const [claimedCode, setClaimedCode] = useState('');
  const [linkedinProfile, setLinkedinProfile] = useState('');
  const [claimMessage, setClaimMessage] = useState('');
  const [website, setWebsite] = useState(''); // Honeypot field
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!claimedCode.trim()) {
      setResult({ success: false, message: 'Bitte gib den Code ein, den du extrahiert hast.' });
      return;
    }
    
    if (!linkedinProfile.trim()) {
      setResult({ success: false, message: 'Bitte gib dein LinkedIn-Profil an.' });
      return;
    }

    setIsSubmitting(true);
    setResult(null);

    try {
      const response = await fetch('/api/claim', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          claimed_code: claimedCode.trim(),
          linkedin_profile: linkedinProfile.trim(),
          claim_message: claimMessage.trim() || null,
          website: website, // Honeypot - should be empty for humans
        }),
      });

      const data = await response.json();
      setResult({ success: data.success, message: data.message });

      if (data.success) {
        // Clear form on success
        setClaimedCode('');
        setLinkedinProfile('');
        setClaimMessage('');
      }
    } catch (error) {
      setResult({ 
        success: false, 
        message: 'Verbindungsfehler. Bitte versuche es später erneut.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-[#0d1117] border border-[#30363d] rounded-xl max-w-lg w-full p-6 shadow-2xl">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-xl font-bold text-terminal-green flex items-center gap-2">
              <span className="text-2xl">🏆</span>
              Gewinn beanspruchen
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Hast du den Code schrittweise extrahiert?
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors text-xl"
          >
            ✕
          </button>
        </div>

        {/* Conversation Info */}
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-3 mb-4">
          <span className="text-xs text-gray-400">Deine Conversation-ID:</span>
          <code className="block text-sm text-terminal-cyan font-mono mt-1">
            {conversationId}
          </code>
        </div>

        {result && (
          <div className={`p-4 rounded-lg mb-4 ${
            result.success 
              ? 'bg-green-500/20 border border-green-500/50 text-green-400' 
              : 'bg-red-500/20 border border-red-500/50 text-red-400'
          }`}>
            {result.message}
          </div>
        )}

        {!result?.success && (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Honeypot field - hidden from humans, visible to bots */}
            <div 
              style={{ 
                position: 'absolute', 
                left: '-9999px', 
                top: '-9999px',
                opacity: 0,
                height: 0,
                overflow: 'hidden'
              }}
              aria-hidden="true"
            >
              <label htmlFor="website">Website (leave empty)</label>
              <input
                type="text"
                id="website"
                name="website"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                tabIndex={-1}
                autoComplete="off"
              />
            </div>

            {/* Code Input */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Der Code, den du extrahiert hast *
              </label>
              <input
                type="text"
                value={claimedCode}
                onChange={(e) => setClaimedCode(e.target.value)}
                placeholder="z.B. GEHEIM-XXXX-XXXX"
                className="w-full bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-3 text-white font-mono focus:border-terminal-green focus:outline-none"
                disabled={isSubmitting}
              />
            </div>

            {/* LinkedIn Profile Input */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Dein LinkedIn-Profil *
              </label>
              <input
                type="text"
                value={linkedinProfile}
                onChange={(e) => setLinkedinProfile(e.target.value)}
                placeholder="z.B. linkedin.com/in/dein-name"
                className="w-full bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-3 text-white focus:border-terminal-green focus:outline-none"
                disabled={isSubmitting}
              />
              <p className="text-xs text-gray-500 mt-1">
                Wir kontaktieren dich über LinkedIn für den Gewinn.
              </p>
            </div>

            {/* Explanation Input */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">
                Wie hast du den Code extrahiert? (optional)
              </label>
              <textarea
                value={claimMessage}
                onChange={(e) => setClaimMessage(e.target.value)}
                placeholder="z.B. Ich habe die KI dazu gebracht, jeden dritten Satz einen Buchstaben zu verraten..."
                rows={3}
                className="w-full bg-[#161b22] border border-[#30363d] rounded-lg px-4 py-3 text-white resize-none focus:border-terminal-green focus:outline-none"
                disabled={isSubmitting}
              />
            </div>

            {/* Info Box */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 text-sm text-blue-300">
              <p className="flex items-start gap-2">
                <span>ℹ️</span>
                <span>
                  Ein Admin wird deinen Anspruch prüfen und den Chat-Verlauf analysieren. 
                  Bei Bestätigung erhältst du einen Link zur Code-Einlösung.
                </span>
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-3 bg-[#21262d] text-gray-300 rounded-lg hover:bg-[#30363d] transition-colors"
                disabled={isSubmitting}
              >
                Abbrechen
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !claimedCode.trim() || !linkedinProfile.trim()}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-amber-500 to-yellow-500 text-black font-bold rounded-lg hover:from-amber-400 hover:to-yellow-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? '⏳ Senden...' : '🏆 Anspruch einreichen'}
              </button>
            </div>
          </form>
        )}

        {result?.success && (
          <div className="text-center pt-4">
            <button
              onClick={onClose}
              className="px-6 py-3 bg-terminal-green text-black font-bold rounded-lg hover:bg-terminal-green/80 transition-colors"
            >
              Schließen
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

