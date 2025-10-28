# 🔒 Enable HTTPS for Shift Handover Application
# Complete Guide to Switch from HTTP to HTTPS

## 📋 Current Situation Analysis

You currently have:
- ✅ Application running on HTTP via nginx (port 80)
- ✅ Complete HTTPS nginx configuration files ready
- ✅ SSL setup scripts available
- ✅ Docker infrastructure configured for SSL

## 🎯 Two Approaches to Enable HTTPS

### **Option A: Use Your Domain with Let's Encrypt SSL (Recommended)**
This gives you a proper SSL certificate from Let's Encrypt for free.

### **Option B: Self-Signed Certificate (Quick Testing)**
This gives you HTTPS immediately but with browser warnings.

---

## 🚀 **Option A: Domain + Let's Encrypt SSL (Production Ready)**

### **Step 1: Set Up Your Domain**

1. **Configure Domain DNS**:
   - Point your domain to your server IP: `35.200.202.18`
   - Create an A record: `your-domain.com` → `35.200.202.18`

2. **Update Domain Configuration**:
   ```bash
   # Edit .env.domain file
   cat > .env.domain << EOF
   DOMAIN_NAME=your-actual-domain.com
   EMAIL=your-email@domain.com
   FLASK_ENV=production
   FLASK_DEBUG=0
   SSL_ENABLED=true
   HTTP_PORT=80
   HTTPS_PORT=443
   EOF
   ```

### **Step 2: Update Nginx Configuration**

Replace `your-domain.com` with your actual domain in nginx config:
```bash
sed -i 's/your-domain\.com/your-actual-domain.com/g' nginx/conf.d/app.conf
sed -i 's/your-domain\.com/your-actual-domain.com/g' nginx/conf.d/https.conf
```

### **Step 3: Run SSL Setup**

You have ready-made scripts for this:
```bash
# Make scripts executable
chmod +x setup-ssl.sh
chmod +x setup-domain.sh

# Run domain setup (if not done)
./setup-domain.sh

# Get SSL certificate
./setup-ssl.sh
```

### **Step 4: Deploy with HTTPS**

```bash
# Switch to production configuration
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 **Option B: Self-Signed Certificate (Quick Setup)**

For immediate HTTPS without domain setup:

### **Step 1: Generate Self-Signed Certificate**

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/selfsigned.key \
  -out nginx/ssl/selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=35.200.202.18"
```

### **Step 2: Create HTTPS Nginx Configuration**

Create a new nginx config for self-signed SSL:
```bash
cat > nginx/conf.d/https-self-signed.conf << 'EOF'
# Upstream to Flask app
upstream flask_app {
    server web:5000;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name _;
    return 301 https://$server_name$request_uri;
}

# HTTPS server with self-signed certificate
server {
    listen 443 ssl http2;
    server_name _;

    # Self-signed SSL certificate
    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Main proxy configuration
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Port 443;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # SSO callback with HTTPS
    location /auth/sso/callback/ {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Port 443;
    }
}
EOF
```

### **Step 3: Update Docker Compose for Self-Signed SSL**

```bash
# Remove existing configs and use self-signed
rm -f nginx/conf.d/http-only.conf
rm -f nginx/conf.d/app.conf

# Update docker-compose to mount SSL certificates
cat >> docker-compose.yml << 'EOF'

  # Nginx with SSL
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - web
    networks:
      - app_network

volumes:
  nginx_logs:

networks:
  app_network:
    driver: bridge
EOF
```

### **Step 4: Restart with HTTPS**

```bash
docker-compose down
docker-compose up -d
```

---

## 🔄 **Quick PowerShell Deployment Script**

I'll create a PowerShell script to automate this for you: