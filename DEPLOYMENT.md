# 🚀 Deployment-Anleitung: Get The Code

Diese Anleitung beschreibt das komplette Deployment der LinkedIn Christmas Code Challenge auf einem frischen Linux-Server mit SSL-Zertifikat.

---

## 📋 Voraussetzungen

- **Server**: Ubuntu 22.04 LTS (oder Debian 12)
- **Minimum**: 2 vCPU, 4 GB RAM, 20 GB SSD
- **Empfohlen**: 4 vCPU, 8 GB RAM, 40 GB SSD
- **Domain**: Eine Domain, die auf die Server-IP zeigt (z.B. `getthecode.stefanai.de`)
- **OpenAI API Key**: Für GPT-4o Zugriff

---

## 🔧 Schritt 1: Server-Grundkonfiguration

### 1.1 Mit dem Server verbinden

```bash
ssh root@DEINE_SERVER_IP
```

### 1.2 System aktualisieren

```bash
apt update && apt upgrade -y
```

### 1.3 Erforderliche Pakete installieren

```bash
apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    ufw \
    htop \
    nano
```

---

## 🐳 Schritt 2: Docker installieren

### 2.1 Docker Repository hinzufügen

```bash
# Docker GPG Key hinzufügen
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Repository hinzufügen
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 2.2 Docker installieren

```bash
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2.3 Docker testen

```bash
docker run hello-world
```

---

## 🔐 Schritt 3: Firewall konfigurieren

```bash
# SSH erlauben (WICHTIG: Sonst sperrst du dich aus!)
ufw allow OpenSSH

# HTTP und HTTPS erlauben
ufw allow 80/tcp
ufw allow 443/tcp

# Firewall aktivieren
ufw enable

# Status prüfen
ufw status
```

---

## 📦 Schritt 4: Projekt klonen

### 4.1 Projektverzeichnis erstellen

```bash
mkdir -p /opt/getthecode
cd /opt/getthecode
```

### 4.2 Repository klonen

```bash
git clone https://github.com/StefanMuellerAI/getthecode.git .
```

---

## ⚙️ Schritt 5: Umgebungsvariablen konfigurieren

### 5.1 .env Datei erstellen

```bash
cp env.example .env
nano .env
```

### 5.2 .env Datei ausfüllen

```bash
# ==============================================
# ENVIRONMENT MODE
# ==============================================
ENVIRONMENT=production

# ==============================================
# DATABASE (Sichere Passwörter verwenden!)
# ==============================================
POSTGRES_USER=getthecode_prod
POSTGRES_PASSWORD=HIER_EIN_SICHERES_PASSWORT_GENERIEREN
POSTGRES_DB=getthecode

# ==============================================
# OPENAI API (REQUIRED)
# ==============================================
OPENAI_API_KEY=sk-DEIN-ECHTER-OPENAI-API-KEY

# ==============================================
# SECRET CODE (Der zu schützende Amazon-Code!)
# ==============================================
SECRET_CODE=AMZN-XXXX-XXXX-XXXX

# ==============================================
# CHALLENGE SETTINGS
# ==============================================
START_DATE=2025-01-01
JACKPOT_PER_MONTH=100

# ==============================================
# CORS ORIGINS (Deine Domain!)
# ==============================================
CORS_ORIGINS=https://getthecode.stefanai.de

# ==============================================
# OPTIONAL
# ==============================================
OPENAI_MODEL=gpt-4o
```

### 5.3 Sicheres Passwort generieren

```bash
# Sicheres Passwort für PostgreSQL generieren
openssl rand -base64 32
```

---

## 🔒 Schritt 6: SSL-Zertifikat mit Let's Encrypt

### 6.1 Certbot installieren

```bash
apt install -y certbot
```

### 6.2 SSL-Verzeichnis erstellen

```bash
mkdir -p /opt/getthecode/nginx/ssl
mkdir -p /opt/getthecode/nginx/certbot
```

### 6.3 Temporären Nginx für Zertifikatsanforderung starten

Erstelle eine temporäre Nginx-Konfiguration:

```bash
# Temporäre Docker Compose für Zertifikatsanforderung
cat > /tmp/docker-compose-certbot.yml << 'EOF'
services:
  nginx-temp:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - /opt/getthecode/nginx/certbot:/var/www/certbot
      - /tmp/nginx-temp.conf:/etc/nginx/conf.d/default.conf:ro
EOF

# Temporäre Nginx-Konfiguration
cat > /tmp/nginx-temp.conf << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
EOF
```

### 6.4 Temporären Nginx starten

```bash
cd /tmp
docker compose -f docker-compose-certbot.yml up -d
```

### 6.5 SSL-Zertifikat anfordern

**⚠️ WICHTIG: Ersetze `getthecode.stefanai.de` durch deine Domain!**

```bash
certbot certonly \
    --webroot \
    --webroot-path=/opt/getthecode/nginx/certbot \
    -d getthecode.stefanai.de \
    --email info@stefanai.de \
    --agree-tos \
    --non-interactive
```

### 6.6 Zertifikate kopieren

```bash
# Zertifikate in das Projektverzeichnis kopieren
cp /etc/letsencrypt/live/getthecode.stefanai.de/fullchain.pem /opt/getthecode/nginx/ssl/
cp /etc/letsencrypt/live/getthecode.stefanai.de/privkey.pem /opt/getthecode/nginx/ssl/

# Berechtigungen setzen
chmod 600 /opt/getthecode/nginx/ssl/*.pem
```

### 6.7 Temporären Nginx stoppen

```bash
cd /tmp
docker compose -f docker-compose-certbot.yml down
```

---

## 🚀 Schritt 7: Anwendung starten

### 7.1 Docker Images bauen und starten

```bash
cd /opt/getthecode

# Production Stack starten
docker compose -f docker-compose.prod.yml up -d --build
```

### 7.2 Logs prüfen

```bash
# Alle Logs anzeigen
docker compose -f docker-compose.prod.yml logs -f

# Nur Backend-Logs
docker compose -f docker-compose.prod.yml logs -f backend

# Nur Frontend-Logs
docker compose -f docker-compose.prod.yml logs -f frontend
```

### 7.3 Status prüfen

```bash
docker compose -f docker-compose.prod.yml ps
```

Erwartete Ausgabe:
```
NAME                    STATUS
getthecode-nginx        running
getthecode-postgres     running (healthy)
getthecode-temporal     running
getthecode-redis        running (healthy)
getthecode-frontend     running
getthecode-backend-1    running
getthecode-backend-2    running
getthecode-worker-1     running
getthecode-worker-2     running
getthecode-worker-3     running
```

---

## 🔄 Schritt 8: Automatische Zertifikatserneuerung

### 8.1 Erneuerungsskript erstellen

```bash
cat > /opt/getthecode/renew-certs.sh << 'EOF'
#!/bin/bash
set -e

DOMAIN="getthecode.stefanai.de"
PROJECT_DIR="/opt/getthecode"

# Zertifikat erneuern
certbot renew --quiet

# Neue Zertifikate kopieren
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $PROJECT_DIR/nginx/ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $PROJECT_DIR/nginx/ssl/

# Nginx neu laden
docker compose -f $PROJECT_DIR/docker-compose.prod.yml exec -T nginx nginx -s reload

echo "$(date): Zertifikate erneuert" >> /var/log/certbot-renewal.log
EOF

chmod +x /opt/getthecode/renew-certs.sh
```

### 8.2 Cronjob für automatische Erneuerung

```bash
# Cronjob hinzufügen (2x täglich prüfen)
(crontab -l 2>/dev/null; echo "0 3,15 * * * /opt/getthecode/renew-certs.sh") | crontab -
```

---

## 🧪 Schritt 9: Deployment testen

### 9.1 HTTPS-Verbindung testen

```bash
curl -I https://getthecode.stefanai.de
```

Erwartete Antwort:
```
HTTP/2 200
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-frame-options: DENY
x-content-type-options: nosniff
```

### 9.2 API Health Check

```bash
curl https://getthecode.stefanai.de/api/health
```

### 9.3 Jackpot-Endpoint testen

```bash
curl https://getthecode.stefanai.de/api/jackpot
```

### 9.4 Im Browser öffnen

Öffne: `https://getthecode.stefanai.de`

---

## 📊 Schritt 10: Monitoring & Wartung

### 10.1 Nützliche Befehle

```bash
# Alle Container neustarten
docker compose -f docker-compose.prod.yml restart

# Einzelnen Service neustarten
docker compose -f docker-compose.prod.yml restart backend

# Container-Ressourcen anzeigen
docker stats

# Logs der letzten Stunde
docker compose -f docker-compose.prod.yml logs --since 1h

# In einen Container einloggen
docker compose -f docker-compose.prod.yml exec backend sh
```

### 10.2 Updates einspielen

```bash
cd /opt/getthecode

# Neueste Änderungen holen
git pull origin main

# Container neu bauen und starten
docker compose -f docker-compose.prod.yml up -d --build

# Alte Images aufräumen
docker image prune -f
```

### 10.3 Datenbank-Backup

```bash
# Backup erstellen
docker compose -f docker-compose.prod.yml exec -T postgresql \
    pg_dump -U getthecode_prod getthecode > backup_$(date +%Y%m%d).sql

# Backup wiederherstellen
cat backup_20250101.sql | docker compose -f docker-compose.prod.yml exec -T postgresql \
    psql -U getthecode_prod getthecode
```

---

## 🔧 Troubleshooting

### Problem: Container startet nicht

```bash
# Detaillierte Logs anzeigen
docker compose -f docker-compose.prod.yml logs backend

# Container-Status prüfen
docker compose -f docker-compose.prod.yml ps -a
```

### Problem: SSL-Zertifikat-Fehler

```bash
# Zertifikat prüfen
openssl s_client -connect getthecode.stefanai.de:443 -servername getthecode.stefanai.de

# Zertifikatsdateien prüfen
ls -la /opt/getthecode/nginx/ssl/
```

### Problem: Datenbank-Verbindung fehlgeschlagen

```bash
# PostgreSQL-Logs prüfen
docker compose -f docker-compose.prod.yml logs postgresql

# Datenbank-Container neustarten
docker compose -f docker-compose.prod.yml restart postgresql
```

### Problem: Temporal-Fehler

```bash
# Temporal-Logs prüfen
docker compose -f docker-compose.prod.yml logs temporal

# Worker-Logs prüfen
docker compose -f docker-compose.prod.yml logs worker
```

---

## 📌 Checkliste

- [ ] Server aktualisiert
- [ ] Docker installiert
- [ ] Firewall konfiguriert (80, 443, SSH)
- [ ] Repository geklont
- [ ] .env Datei konfiguriert
- [ ] SSL-Zertifikat erstellt
- [ ] Docker Stack gestartet
- [ ] Alle Container laufen
- [ ] HTTPS funktioniert
- [ ] API erreichbar
- [ ] Frontend lädt
- [ ] Automatische Zertifikatserneuerung eingerichtet

---

## 🆘 Support

Bei Fragen oder Problemen:
- **E-Mail**: info@stefanai.de
- **Telefon**: 0221/5702984

---

*Letzte Aktualisierung: Dezember 2024*

