/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#060d06',
          surface: '#0a140a',
          border: '#1a2e1a',
          green: '#00d26a',
          'green-dim': '#7ec850',
          amber: '#ffb000',
          red: '#ff3333',
          cyan: '#2d8f4e',
        },
        spring: {
          green: '#00d26a',
          lime: '#7ec850',
          blossom: '#ffb7c5',
          meadow: '#2d8f4e',
          sun: '#ffd700',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', 'monospace'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'typing': 'typing 0.5s steps(1) infinite',
        'blink': 'blink 1s step-end infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'bloom': 'bloom 1.2s ease-in-out infinite',
      },
      keyframes: {
        blink: {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #00d26a, 0 0 10px #00d26a, 0 0 15px #00d26a' },
          '100%': { boxShadow: '0 0 10px #00d26a, 0 0 20px #00d26a, 0 0 30px #00d26a' },
        },
        bloom: {
          '0%, 100%': { transform: 'scale(1)' },
          '25%': { transform: 'scale(1.1)' },
          '50%': { transform: 'scale(1)' },
          '75%': { transform: 'scale(1.05)' },
        },
      },
    },
  },
  plugins: [],
};
