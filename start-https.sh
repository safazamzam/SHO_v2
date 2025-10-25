#!/bin/bash

# Production startup script with HTTPS support
echo "🚀 Starting Shift Handover Application with HTTPS..."

# Wait for certificates if using Let's Encrypt
if [ "$USE_LETSENCRYPT" = "true" ]; then
    echo "⏳ Waiting for SSL certificates..."
    until [ -f /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem ]; do
        echo "Waiting for certificates to be generated..."
        sleep 10
    done
    echo "✅ SSL certificates found!"
fi

# Create self-signed certificates for development/testing if none exist
if [ ! -f "/app/certs/cert.pem" ] && [ "$USE_LETSENCRYPT" != "true" ]; then
    echo "🔐 Generating self-signed SSL certificates..."
    openssl req -x509 -newkey rsa:4096 -nodes \
        -out /app/certs/cert.pem \
        -keyout /app/certs/key.pem \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN_NAME:-localhost}"
    echo "✅ Self-signed certificates generated!"
fi

# Initialize database if needed
echo "🗄️ Initializing database..."
python -c "
from app import app, db
with app.app_context():
    try:
        db.create_all()
        print('✅ Database initialized successfully')
    except Exception as e:
        print(f'⚠️ Database initialization warning: {e}')
"

# Set certificate paths based on configuration
if [ "$USE_LETSENCRYPT" = "true" ]; then
    export SSL_CERT_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
    export SSL_KEY_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"
else
    export SSL_CERT_PATH="/app/certs/cert.pem"
    export SSL_KEY_PATH="/app/certs/key.pem"
fi

# Production server options
if [ "$USE_GUNICORN" = "true" ]; then
    echo "🌟 Starting with Gunicorn (Production)..."
    exec gunicorn --bind 0.0.0.0:5000 \
        --workers 4 \
        --worker-class gevent \
        --worker-connections 1000 \
        --timeout 60 \
        --keepalive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --certfile="$SSL_CERT_PATH" \
        --keyfile="$SSL_KEY_PATH" \
        "app:app"
else
    echo "🐍 Starting with Flask development server..."
    exec python app.py
fi