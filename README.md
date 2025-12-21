# 🎮 Get The Code

Eine Prompt-Injection-Challenge, bei der du versuchst, eine KI auszutricksen, um einen geheimen Amazon-Gutscheincode zu erhalten.

## 🏗️ Architektur

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js       │────▶│   FastAPI       │────▶│   Temporal      │
│   Frontend      │     │   Backend       │     │   Workflow      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  3x OpenAI      │
                                               │  GPT-4o Calls   │
                                               └─────────────────┘
```

### Drei-Stufen-Sicherheitssystem

1. **Stage 1 - Generator**: Generiert eine Antwort auf den User-Prompt (kennt den Code)
2. **Stage 2 - Validator 1**: Prüft ob der Code in der Antwort enthalten ist
3. **Stage 3 - Validator 2**: Finale Sicherheitsprüfung

## 🚀 Quick Start

### Voraussetzungen

- Docker & Docker Compose
- OpenAI API Key

### Setup

1. **Umgebungsvariablen konfigurieren:**

```bash
# .env Datei erstellen
cp .env.example .env

# OpenAI API Key eintragen
nano .env
```

2. **Docker Stack starten:**

```bash
docker-compose up -d
```

3. **Öffne die App:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Temporal UI: http://localhost:8080

## 📁 Projektstruktur

```
getyourcode/
├── docker-compose.yml      # Docker Stack Definition
├── frontend/               # Next.js Frontend
│   ├── app/               # App Router
│   │   ├── page.tsx       # Hauptseite
│   │   └── api/           # API Routes (Proxy)
│   └── components/        # React Components
├── backend/               # FastAPI Backend
│   ├── app/              # Hauptanwendung
│   │   ├── main.py       # FastAPI App
│   │   ├── config.py     # Konfiguration
│   │   └── routers/      # API Endpoints
│   └── workflows/        # Temporal Workflows
│       ├── worker.py     # Worker Process
│       └── activities.py # OpenAI Activities
└── scripts/              # Hilfsskripte
    └── init-db.sql       # Datenbank-Initialisierung
```

## 🎯 Spielregeln

- Die KI kennt einen Amazon-Gutscheincode im Wert von 100€
- Jeden Monat, in dem niemand den Code erhält, steigt der Jackpot um 100€
- Nach einem Jahr: 12 × 100€ = 1.200€ Jackpot
- Drei KI-Instanzen überwachen sich gegenseitig

## 🔧 Entwicklung

### Backend lokal starten

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Worker lokal starten

```bash
cd backend
python -m workflows.worker
```

### Frontend lokal starten

```bash
cd frontend
npm install
npm run dev
```

## 🛠️ API Endpoints

| Endpoint | Method | Beschreibung |
|----------|--------|--------------|
| `/challenge` | POST | Sendet einen Prompt an die KI |
| `/jackpot` | GET | Aktueller Jackpot-Betrag |
| `/health` | GET | Health Check |

## 🔐 Sicherheit

Der geheime Code wird durch drei Ebenen geschützt:

1. **System-Prompt Injection Prevention**: Die KI ist angewiesen, den Code niemals herauszugeben
2. **Validierung Stage 2**: Prüft auf direkte und kodierte Formen des Codes
3. **Validierung Stage 3**: Finale Prüfung mit strengeren Kriterien

## 📝 Umgebungsvariablen

| Variable | Beschreibung | Default |
|----------|--------------|---------|
| `OPENAI_API_KEY` | OpenAI API Key | (required) |
| `SECRET_CODE` | Der geheime Gutscheincode | `FAKE-AMZN-2024-XXXX` |
| `START_DATE` | Startdatum für Jackpot-Berechnung | `2025-01-01` |
| `POSTGRES_USER` | PostgreSQL Benutzer | `getthecode` |
| `POSTGRES_PASSWORD` | PostgreSQL Passwort | `getthecode123` |

## 📄 Lizenz

MIT

