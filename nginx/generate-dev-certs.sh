#!/bin/bash
# ==============================================
# Generate Self-Signed SSL Certificates for Development
# ==============================================
# WARNING: Only use these certificates for local development!
# For production, use Let's Encrypt or a trusted CA.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$SCRIPT_DIR/ssl"

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/privkey.pem" \
    -out "$SSL_DIR/fullchain.pem" \
    -subj "/C=DE/ST=Berlin/L=Berlin/O=GetTheCode/OU=Development/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

echo "✓ Development SSL certificates generated in $SSL_DIR"
echo ""
echo "Files created:"
echo "  - $SSL_DIR/fullchain.pem (certificate)"
echo "  - $SSL_DIR/privkey.pem (private key)"
echo ""
echo "WARNING: These are self-signed certificates for development only!"
echo "Your browser will show a security warning - this is expected."

