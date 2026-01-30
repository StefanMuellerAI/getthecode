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
          bg: '#0a0808',
          surface: '#120a0a',
          border: '#2a1515',
          green: '#ff69b4',
          'green-dim': '#ff1493',
          amber: '#ffb000',
          red: '#ff3333',
          cyan: '#ff6b9d',
        },
        valentine: {
          pink: '#ff69b4',
          hot: '#ff1493',
          rose: '#ffb6c1',
          deep: '#c41e3a',
          crimson: '#dc143c',
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
        'heartbeat': 'heartbeat 1.2s ease-in-out infinite',
      },
      keyframes: {
        blink: {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #ff69b4, 0 0 10px #ff69b4, 0 0 15px #ff69b4' },
          '100%': { boxShadow: '0 0 10px #ff69b4, 0 0 20px #ff69b4, 0 0 30px #ff69b4' },
        },
        heartbeat: {
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

