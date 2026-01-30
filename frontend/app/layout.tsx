import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Valentine Code Challenge 💕',
  description: 'Kannst du Amors KI austricksen und den geheimen Gutscheincode erhalten? Eine romantische Prompt-Injection-Challenge zum Valentinstag!',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body className="crt-flicker">
        {/* Hearts fall effect */}
        <div className="heartfall">
          <div className="heart">💕</div>
          <div className="heart">❤️</div>
          <div className="heart">💗</div>
          <div className="heart">💖</div>
          <div className="heart">💝</div>
          <div className="heart">💘</div>
          <div className="heart">❤️</div>
          <div className="heart">💕</div>
          <div className="heart">💗</div>
          <div className="heart">💖</div>
          <div className="heart">💝</div>
          <div className="heart">💘</div>
          <div className="heart">❤️</div>
          <div className="heart">💕</div>
          <div className="heart">💗</div>
          <div className="heart">💖</div>
          <div className="heart">💝</div>
          <div className="heart">💘</div>
          <div className="heart">❤️</div>
          <div className="heart">💕</div>
        </div>
        {children}
      </body>
    </html>
  );
}
