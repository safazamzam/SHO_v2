# 🌐 Domain Setup Guide for Shift Handover App

This guide will help you set up domain name access for your Shift Handover application instead of using `http://35.200.202.18:5000`.

## 📋 Prerequisites

Before starting, ensure you have:

1. **A domain name** (e.g., `handover.yourdomain.com`)
2. **DNS access** to configure A records
3. **Server access** to your GCP instance (35.200.202.18)
4. **Ports 80 and 443** open in your firewall

## 🚀 Quick Setup (Recommended)

### Step 1: Configure DNS

1. **Log into your domain registrar** (GoDaddy, Namecheap, Cloudflare, etc.)
2. **Create an A record** pointing to your server:
   ```
   Type: A
   Name: handover (or your preferred subdomain)
   Value: 35.200.202.18
   TTL: 300 (5 minutes)
   ```
3. **Wait for DNS propagation** (usually 5-15 minutes)
4. **Test DNS**: `nslookup handover.yourdomain.com`

### Step 2: Run Domain Setup

On your server, run the setup script:

```bash
# Make script executable
chmod +x setup-domain.sh

# Run setup
./setup-domain.sh
```

Enter your domain name and email when prompted.

### Step 3: Get SSL Certificates

```bash
# Run SSL setup
./setup-ssl.sh
```

### Step 4: Deploy with Domain

```bash
# Deploy the application
./deploy-with-domain.sh
```

## 🔧 Manual Setup (Advanced)

If you prefer manual configuration:

### 1. Update Environment Configuration

Create `.env.domain` file:
```bash
DOMAIN_NAME=handover.yourdomain.com
EMAIL=admin@yourdomain.com
FLASK_ENV=production
FLASK_DEBUG=0
```

### 2. Update Nginx Configuration

Edit `nginx/conf.d/app.conf` and replace `your-domain.com` with your actual domain.

### 3. Deploy with Docker Compose

```bash
# Stop current deployment
docker-compose down

# Start with domain configuration
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Obtain SSL Certificate

```bash
# Create directories
mkdir -p certbot_conf certbot_www

# Get certificate
docker run --rm \
  -v $(pwd)/certbot_conf:/etc/letsencrypt \
  -v $(pwd)/certbot_www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@domain.com \
  --agree-tos \
  --no-eff-email \
  -d handover.yourdomain.com

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## 🌍 Domain Options

### Option 1: Subdomain (Recommended)
- `handover.yourdomain.com`
- `shift.yourdomain.com`
- `ops.yourdomain.com`

### Option 2: New Domain
- `handover-app.com`
- `shift-ops.com`

### Option 3: Free Domain Services
- Use services like:
  - Freenom (.tk, .ml, .ga domains)
  - NoIP (dynamic DNS)
  - DuckDNS (free subdomain)

## 🔒 Security Features

The setup includes:

- **SSL/TLS encryption** (Let's Encrypt)
- **HTTP to HTTPS redirect**
- **Security headers**
- **Rate limiting**
- **Access logging**

## 📊 Monitoring and Logs

### Check Application Status
```bash
# View all services
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### View Access Logs
```bash
# Nginx access logs
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log

# Application logs
docker-compose -f docker-compose.prod.yml logs -f web
```

## 🛠️ Troubleshooting

### DNS Issues
```bash
# Check DNS resolution
nslookup your-domain.com
dig your-domain.com

# Check from different locations
# Use online tools like whatsmydns.net
```

### SSL Certificate Issues
```bash
# Check certificate status
docker run --rm -v $(pwd)/certbot_conf:/etc/letsencrypt certbot/certbot certificates

# Renew certificate manually
docker run --rm -v $(pwd)/certbot_conf:/etc/letsencrypt -v $(pwd)/certbot_www:/var/www/certbot certbot/certbot renew
```

### Application Issues
```bash
# Check application health
curl -f http://localhost:5000/health

# View detailed logs
docker-compose -f docker-compose.prod.yml logs web
```

## 🔄 Certificate Renewal

SSL certificates are automatically renewed. To check renewal:

```bash
# Test renewal
docker run --rm -v $(pwd)/certbot_conf:/etc/letsencrypt certbot/certbot renew --dry-run

# Manual renewal
docker run --rm -v $(pwd)/certbot_conf:/etc/letsencrypt -v $(pwd)/certbot_www:/var/www/certbot certbot/certbot renew
```

## 📱 Access Your Application

After successful setup, access your application at:

- **HTTPS**: `https://handover.yourdomain.com`
- **HTTP**: `http://handover.yourdomain.com` (redirects to HTTPS)

## 🎯 Final Result

Instead of: `http://35.200.202.18:5000/login`
You'll have: `https://handover.yourdomain.com/login`

## 📞 Support

If you encounter issues:

1. **Check DNS propagation**: Use online DNS checker tools
2. **Verify firewall**: Ensure ports 80 and 443 are open
3. **Check logs**: `docker-compose -f docker-compose.prod.yml logs`
4. **Test certificate**: `openssl s_client -connect your-domain.com:443`

## 🔧 Useful Commands

```bash
# Quick restart
docker-compose -f docker-compose.prod.yml restart

# Full rebuild
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# Follow logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

**Note**: Replace `your-domain.com` and `handover.yourdomain.com` with your actual domain name throughout this guide.