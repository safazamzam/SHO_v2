# 🔒 HTTPS Deployment - Quick Start

## ✅ Ready to Deploy!

Your Shift Handover Application is now configured for production HTTPS deployment with Nginx reverse proxy and Let's Encrypt SSL certificates.

### 📋 What's Included

**Core Configuration Files:**
- `docker-compose.https.yml` - Production Docker setup with SSL
- `nginx/conf.d/https.conf` - Nginx HTTPS configuration
- `.env.production.template` - Environment variables template

**Setup Scripts:**
- `setup-ssl.sh` (Linux) - Automated SSL certificate setup  
- `setup-ssl.ps1` (Windows) - PowerShell SSL setup script
- `deploy-https.sh` (Linux) - Complete deployment automation

**Documentation:**
- `HTTPS_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide

### 🚀 Quick Deployment (3 Steps)

#### 1. **Server Preparation**
```bash
# Ensure Docker is installed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone your repository
git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git
cd shifthandover
```

#### 2. **Configuration**
```bash
# Copy and edit environment file
cp .env.production.template .env.production
nano .env.production

# At minimum, set these required variables:
# DOMAIN_NAME=your-domain.com
# CERTBOT_EMAIL=admin@your-domain.com
# SECRET_KEY=generate-32-char-secret
# POSTGRES_PASSWORD=secure-db-password
# SECRETS_MASTER_KEY=generate-fernet-key
```

#### 3. **Deploy with HTTPS**
```bash
# Make script executable and run
chmod +x setup-ssl.sh
./setup-ssl.sh
```

**That's it!** 🎉 Your app will be available at `https://your-domain.com`

### 🔧 Key Features

✅ **Automatic HTTPS** - Let's Encrypt SSL certificates  
✅ **Auto-renewal** - Certificates renew automatically  
✅ **Security Headers** - HSTS, CSP, XSS protection  
✅ **Rate Limiting** - Protection against abuse  
✅ **Gzip Compression** - Optimized performance  
✅ **Health Monitoring** - Built-in health checks  
✅ **Database Backup** - PostgreSQL with persistent storage  

### 🛡️ Security Features

- **TLS 1.2/1.3** only
- **HSTS** with preload
- **Content Security Policy**
- **Rate limiting** on auth/API endpoints
- **Secure session** management
- **X-Frame-Options** protection

### 📊 Production Ready

- **Load balancer** compatible
- **Horizontal scaling** ready
- **Log aggregation** configured
- **Health check** endpoints
- **Graceful shutdowns**
- **Container restart** policies

### 🔍 Management Commands

```bash
# View application logs
docker-compose -f docker-compose.https.yml logs -f web

# View all service logs
docker-compose -f docker-compose.https.yml logs -f

# Restart services
docker-compose -f docker-compose.https.yml restart

# Update application
git pull
docker-compose -f docker-compose.https.yml up -d --build

# Check SSL certificate
docker-compose -f docker-compose.https.yml exec certbot certbot certificates

# Manual certificate renewal
docker-compose -f docker-compose.https.yml exec certbot certbot renew

# Database backup
docker-compose -f docker-compose.https.yml exec db pg_dump -U shifthandover_user shifthandover > backup.sql
```

### 🆘 Troubleshooting

**SSL Certificate Issues:**
```bash
# Check DNS propagation
nslookup your-domain.com

# Test certificate request
docker-compose -f docker-compose.https.yml run --rm certbot certonly --dry-run --webroot --webroot-path=/var/www/certbot --email admin@domain.com -d your-domain.com
```

**Application Issues:**
```bash
# Check container status
docker-compose -f docker-compose.https.yml ps

# Test database connection
docker-compose -f docker-compose.https.yml exec web python -c "from app import db; print('DB Connected' if db.engine else 'DB Failed')"
```

**Nginx Issues:**
```bash
# Test nginx configuration
docker-compose -f docker-compose.https.yml exec nginx nginx -t

# Reload nginx
docker-compose -f docker-compose.https.yml exec nginx nginx -s reload
```

### 📈 Performance Testing

**SSL Rating:**
- https://www.ssllabs.com/ssltest/

**Security Headers:**
- https://securityheaders.com/

**Performance:**
- https://pagespeed.web.dev/

### 📞 Support

- **Documentation**: `HTTPS_DEPLOYMENT_GUIDE.md`
- **Repository**: https://git.garage.epam.com/shift-handover-automation/shifthandover
- **Issues**: Create GitLab issue for support

---

**🎯 Result**: Production-ready HTTPS application with enterprise-grade security and performance!