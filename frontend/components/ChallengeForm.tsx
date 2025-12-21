'use client';

import { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';

interface ChallengeFormProps {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
}

export interface ChallengeFormRef {
  clearInput: () => void;
}

const ChallengeForm = forwardRef<ChallengeFormRef, ChallengeFormProps>(
  ({ onSubmit, isLoading }, ref) => {
    const [prompt, setPrompt] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Expose clearInput method to parent
    useImperativeHandle(ref, () => ({
      clearInput: () => {
        setPrompt('');
      },
    }));

    // Auto-resize textarea
    useEffect(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
      }
    }, [prompt]);

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (prompt.trim() && !isLoading) {
        onSubmit(prompt.trim());
      }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
      }
    };

    return (
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-start gap-2">
          <span className="text-terminal-green mt-1 select-none">{'>'}</span>
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Schreibe deine Nachricht an den Weihnachtsmann..."
              disabled={isLoading}
              rows={1}
              className="terminal-input min-h-[24px] max-h-[200px] disabled:opacity-50"
            />
            {!prompt && !isLoading && (
              <span className="absolute right-0 top-0 text-terminal-green opacity-50 typing-cursor" />
            )}
          </div>
        </div>

        <div className="flex justify-between items-center mt-4">
          <span className="text-xs opacity-50">
            SHIFT+ENTER für neue Zeile | ENTER zum Senden
          </span>
          <button
            type="submit"
            disabled={!prompt.trim() || isLoading}
            className={`
              px-6 py-2 rounded border font-medium text-sm
              transition-all duration-200 uppercase tracking-wider
              ${
                !prompt.trim() || isLoading
                  ? 'border-terminal-border text-terminal-border cursor-not-allowed'
                  : 'border-terminal-green text-terminal-green hover:bg-terminal-green hover:text-terminal-bg'
              }
            `}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Prüfe...
              </span>
            ) : (
              '🎄 Senden'
            )}
          </button>
        </div>
      </form>
    );
  }
);

ChallengeForm.displayName = 'ChallengeForm';

export default ChallengeForm;
