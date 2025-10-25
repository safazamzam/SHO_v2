# 🔒 HTTPS Production Deployment Guide

This guide will help you deploy your Shift Handover Application with HTTPS using Nginx reverse proxy and Let's Encrypt SSL certificates.

## 📋 Prerequisites

### Server Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- Domain name pointing to your server's public IP
- Ports 80 and 443 open in firewall
- At least 2GB RAM and 10GB disk space

### Domain Setup
1. **Purchase a domain** (e.g., from GoDaddy, Namecheap, etc.)
2. **Configure DNS A Record**:
   ```
   Type: A
   Name: @ (or your subdomain)
   Value: YOUR_SERVER_PUBLIC_IP
   TTL: 300 (or default)
   ```
3. **Optional: Add www subdomain**:
   ```
   Type: A
   Name: www
   Value: YOUR_SERVER_PUBLIC_IP
   TTL: 300
   ```
- **Linux VM**: Ubuntu 20.04+ or CentOS 8+ recommended
- **Windows Server**: Windows Server 2019+ with Docker Desktop
- **Resources**: Minimum 2GB RAM, 20GB storage
- **Ports**: 80 (HTTP), 443 (HTTPS) open in firewall

## 🚀 Deployment Options

### Option 1: Nginx Reverse Proxy + Let's Encrypt (Recommended)

This is the most robust production setup with automatic SSL certificate management.

#### Files Created:
- `docker-compose.https.yml` - Main orchestration file
- `nginx/nginx.conf` - Main Nginx configuration
- `nginx/conf.d/app.conf` - Application-specific Nginx config
- `deploy-https.sh` - Linux deployment script
- `deploy-https.ps1` - Windows deployment script

#### Features:
✅ **Automatic SSL certificates** from Let's Encrypt  
✅ **Auto-renewal** of certificates  
✅ **Security headers** and best practices  
✅ **Load balancing** ready  
✅ **Static file optimization**  
✅ **HTTP to HTTPS redirect**  

#### Quick Start (Linux):
```bash
# 1. Copy your application files to the server
scp -r . user@your-server:/opt/shift-handover/

# 2. SSH into your server
ssh user@your-server

# 3. Run the deployment script
sudo chmod +x /opt/shift-handover/deploy-https.sh
sudo /opt/shift-handover/deploy-https.sh

# 4. Follow the prompts to enter your domain and email
```

#### Quick Start (Windows Server):
```powershell
# 1. Copy application files to C:\shift-handover
# 2. Open PowerShell as Administrator
# 3. Run deployment script
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy-https.ps1 -DomainName "yourdomain.com" -Email "admin@yourdomain.com"
```

### Option 2: Direct Flask HTTPS (Simple Setup)

For smaller deployments or when you can't use Nginx.

#### Files Created:
- `app_https.py` - Flask app with built-in HTTPS support
- `Dockerfile.https` - Enhanced Dockerfile with SSL support
- `start-https.sh` - Startup script with certificate management

#### Features:
✅ **Self-signed certificates** for testing  
✅ **Let's Encrypt integration** possible  
✅ **Gunicorn production server**  
✅ **Health checks**  
⚠️ **Less scalable** than Option 1  

## 🔧 Configuration Files

### Environment Variables (.env.https)

Copy `.env.https.example` to `.env.https` and configure:

```bash
# Domain Configuration
DOMAIN_NAME=yourdomain.com
CERTBOT_EMAIL=admin@yourdomain.com

# SSL Settings
USE_LETSENCRYPT=true
USE_GUNICORN=true

# Application Settings
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DATABASE_URI=sqlite:///instance/shift_handover.db

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### SSL Certificate Options

#### 1. Let's Encrypt (Free, Recommended)
- **Automatic**: Certificates requested and renewed automatically
- **Trusted**: Recognized by all browsers
- **Valid**: 90-day certificates with auto-renewal

#### 2. Self-Signed (Development/Testing)
- **Quick**: Generated automatically if no other certificates
- **Warning**: Browser security warnings
- **Use Case**: Development and internal testing

#### 3. Custom Certificates (Enterprise)
- **Purchased**: From certificate authorities like DigiCert, Comodo
- **Wildcard**: Support for subdomains
- **Extended Validation**: Green bar in browsers

## 🔒 Security Features

### HTTPS Implementation
- **TLS 1.2/1.3**: Modern encryption protocols
- **Strong Ciphers**: Secure cipher suites
- **HSTS**: HTTP Strict Transport Security headers
- **Security Headers**: X-Frame-Options, CSP, etc.

### Additional Security
```nginx
# Security headers in Nginx config
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
```

## 📊 Monitoring & Maintenance

### Health Checks
- **Endpoint**: `https://yourdomain.com/health`
- **Docker**: Built-in health checks in containers
- **Nginx**: Upstream health monitoring

### Log Monitoring
```bash
# View application logs
docker-compose -f docker-compose.https.yml logs -f web

# View Nginx logs
docker-compose -f docker-compose.https.yml logs -f nginx

# SSL certificate status
docker-compose -f docker-compose.https.yml run --rm certbot certificates
```

### Certificate Renewal
```bash
# Manual renewal (automatic renewal is configured)
docker-compose -f docker-compose.https.yml run --rm certbot renew

# Test renewal process
docker-compose -f docker-compose.https.yml run --rm certbot renew --dry-run
```

## 🛠 Troubleshooting

### Common Issues

#### 1. Certificate Request Failed
```bash
# Check DNS propagation
nslookup yourdomain.com

# Verify domain points to your server
curl -I http://yourdomain.com/.well-known/acme-challenge/test

# Check firewall
sudo ufw status
```

#### 2. SSL Certificate Errors
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Verify certificate chain
openssl verify -CAfile chain.pem cert.pem
```

#### 3. Application Not Accessible
```bash
# Check container status
docker-compose -f docker-compose.https.yml ps

# Check port bindings
netstat -tlnp | grep ':443'

# Test local connectivity
curl -k https://localhost/health
```

### Performance Optimization

#### Nginx Tuning
```nginx
# In nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 20M;
```

#### Flask/Gunicorn Tuning
```bash
# Environment variables
WORKERS=4                    # Number of worker processes
WORKER_CONNECTIONS=1000      # Connections per worker
TIMEOUT=60                   # Request timeout
MAX_REQUESTS=1000           # Requests before worker restart
```

## 🔄 Deployment Workflow

### Initial Deployment
1. **Prepare**: Copy files, configure environment
2. **DNS**: Point domain to server IP
3. **Deploy**: Run deployment script
4. **Verify**: Test HTTPS access
5. **Configure**: Update application settings

### Updates
```bash
# Standard update process
git pull origin main
docker-compose -f docker-compose.https.yml build web
docker-compose -f docker-compose.https.yml up -d
```

### Rollback
```bash
# Quick rollback to previous version
git checkout previous-commit
docker-compose -f docker-compose.https.yml up -d --force-recreate
```

## 📞 Support

### Testing Your Setup
1. **SSL Test**: https://www.ssllabs.com/ssltest/
2. **Security Headers**: https://securityheaders.com/
3. **Performance**: https://gtmetrix.com/

### Getting Help
- Check Docker logs for specific error messages
- Verify DNS propagation with online tools
- Test certificate validity with SSL checkers
- Monitor server resources (CPU, memory, disk)

## 🎯 Production Checklist

Before going live:
- [ ] Domain DNS properly configured
- [ ] Firewall rules configured (ports 80, 443)
- [ ] SSL certificates obtained and valid
- [ ] Environment variables configured
- [ ] Database properly initialized
- [ ] SMTP settings tested
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Security headers verified
- [ ] Performance tested under load

---

**🌟 Your Flask application is now ready for production HTTPS deployment!**

Choose Option 1 (Nginx + Let's Encrypt) for most production scenarios, or Option 2 (Direct Flask HTTPS) for simpler setups.