import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Spring Code Challenge 🌱',
  description: 'Kannst du die KI austricksen und den geheimen Gutscheincode erhalten? Eine Prompt-Injection-Challenge zum Frühlingsbeginn!',
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
        {/* Petal fall effect */}
        <div className="petalfall">
          <div className="petal">🌸</div>
          <div className="petal">🍃</div>
          <div className="petal">🌿</div>
          <div className="petal">🌻</div>
          <div className="petal">🌱</div>
          <div className="petal">☀️</div>
          <div className="petal">🍃</div>
          <div className="petal">🌸</div>
          <div className="petal">🌿</div>
          <div className="petal">🌻</div>
          <div className="petal">🌱</div>
          <div className="petal">🌷</div>
          <div className="petal">🍃</div>
          <div className="petal">🌸</div>
          <div className="petal">🌿</div>
          <div className="petal">🌻</div>
          <div className="petal">🌱</div>
          <div className="petal">🌷</div>
          <div className="petal">🍃</div>
          <div className="petal">🌸</div>
        </div>
        {children}
      </body>
    </html>
  );
}
