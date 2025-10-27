# 🚀 Complete Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Shift Handover Application v2 with SSO integration and production-ready configuration.

## 🎯 Current Production Status

✅ **DEPLOYED AND WORKING**
- **URL**: http://35.200.202.18
- **Health Check**: http://35.200.202.18/health
- **SSO**: Google OAuth integrated and working
- **Database**: MySQL running in Docker
- **Proxy**: nginx reverse proxy (Port 80 → 5000)

## 🚀 Quick Deployment (Recommended)

### Option 1: Clone and Deploy
```bash
# 1. Clone the repository
git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git
cd shifthandover

# 2. Quick production setup
chmod +x simple-port-mapping.sh
./simple-port-mapping.sh

# 3. Verify deployment
curl http://localhost/health
```

### Option 2: Manual Deployment

#### Step 1: Prepare Environment
```bash
# Create project directory
mkdir -p /home/sajid/shift_handover_app
cd /home/sajid/shift_handover_app

# Clone repository
git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git .
```

#### Step 2: Configure Environment
```bash
# Copy production environment template
cp .env.domain .env.production

# Edit environment variables
nano .env.production
```

**Required Environment Variables:**
```env
# Database Configuration
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_PASSWORD=your_secure_password

# SSO Configuration
SSO_ENCRYPTION_KEY=your_32_character_encryption_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your_flask_secret_key
```

#### Step 3: Deploy with Docker Compose
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
sleep 15

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

#### Step 4: Verify Deployment
```bash
# Test health endpoint
curl http://localhost/health

# Expected response:
{
  "services": {
    "application": "up",
    "database": "up"
  },
  "status": "healthy",
  "timestamp": 1761506683.3520174
}
```

## 🔧 Service Architecture

### Current Setup
```
Internet (Port 80) → nginx → Flask App (Port 5000) → MySQL Database
```

### Docker Services
- **nginx**: Reverse proxy and load balancer
- **web**: Flask application container
- **db**: MySQL database container
- **certbot**: SSL certificate management (for future HTTPS)

## 🔐 SSO Configuration

### Google OAuth Setup (Working Configuration)

1. **Google Cloud Console Configuration**
   - Project: Your Google Cloud Project
   - API: Google+ API enabled
   - OAuth 2.0 Client ID created
   - Authorized redirect URI: `http://35.200.202.18/auth/sso/callback/google_oauth`

2. **Application Configuration**
   - SSO provider configured in admin dashboard
   - Client ID and secret encrypted and stored
   - User claims mapping enabled

3. **Test SSO Integration**
   ```bash
   # Test login flow
   curl -I http://35.200.202.18/login
   
   # Should redirect to Google OAuth
   ```

## 🌐 Domain Configuration (Future)

### Setup for handover.lab.epam.com

1. **NAT Configuration**
   ```bash
   # Coordinate with network team
   # Map handover.lab.epam.com → 35.200.202.18
   ```

2. **Deploy Domain Configuration**
   ```bash
   # Use domain setup script
   chmod +x setup-epam-lab.sh
   ./setup-epam-lab.sh
   ```

3. **Update nginx Configuration**
   ```bash
   # Domain-specific nginx config will be applied
   # Access via: http://handover.lab.epam.com
   ```

## 📊 Monitoring and Maintenance

### Health Monitoring
```bash
# Application health
curl http://35.200.202.18/health

# Service status
docker-compose -f docker-compose.prod.yml ps

# Resource usage
docker stats
```

### Log Monitoring
```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs web

# nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Database logs
docker-compose -f docker-compose.prod.yml logs db

# Follow all logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Maintenance Commands
```bash
# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build web

# Clean nginx configuration
./cleanup-nginx.sh

# Backup application
./scripts/backup_application.sh
```

## 🔒 Security Considerations

### Current Security Features
- ✅ nginx reverse proxy with security headers
- ✅ Rate limiting on API endpoints
- ✅ Encrypted SSO configuration storage
- ✅ Secure session management
- ✅ CSRF protection
- ✅ SQL injection prevention

### Production Security Checklist
- [ ] Enable HTTPS with Let's Encrypt certificates
- [ ] Configure firewall rules
- [ ] Set up log monitoring and alerting
- [ ] Regular security updates
- [ ] Database backup encryption
- [ ] Network segmentation

## 🚨 Troubleshooting

### Common Issues

#### nginx Configuration Errors
```bash
# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Fix conflicts
./cleanup-nginx.sh
```

#### Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.prod.yml exec db mysql -u root -p

# Reset database
docker-compose -f docker-compose.prod.yml restart db
```

#### SSO Authentication Issues
```bash
# Check SSO configuration
docker-compose -f docker-compose.prod.yml logs web | grep -i sso

# Debug user profile
python debug_user_profile.py
```

### Emergency Recovery
```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Remove containers and volumes (CAUTION: Data loss)
docker-compose -f docker-compose.prod.yml down -v

# Redeploy from scratch
./simple-port-mapping.sh
```

## 📞 Support and Documentation

### Repository Information
- **GitLab**: https://git.garage.epam.com/shift-handover-automation/shifthandover
- **Branch**: main
- **Documentation**: Available in repository root

### Additional Resources
- `PRODUCTION_DEPLOYMENT_GUIDE.md`: Detailed production setup
- `NGINX_FIX_GUIDE.md`: nginx troubleshooting
- `VM_DEPLOYMENT_SUCCESS.md`: Deployment verification
- `scripts/README.md`: Script documentation

### Contact Information
- **Repository Owner**: EPAM Shift Handover Automation Team
- **Environment**: Production VM at 35.200.202.18
- **Last Updated**: October 27, 2025

---

## ✅ Deployment Verification Checklist

- [ ] Application accessible at http://35.200.202.18
- [ ] Health endpoint returns successful response
- [ ] SSO login redirects to Google OAuth
- [ ] User profile displays correctly after login
- [ ] Dashboard loads with proper data
- [ ] Database connections working
- [ ] nginx reverse proxy functioning
- [ ] Docker services running stable
- [ ] Logs capturing properly
- [ ] Performance acceptable

**Status**: ✅ Production Ready and Deployed