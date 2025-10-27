# 🚀 Shift Handover Application v2 - Production Ready

A comprehensive Flask-based shift handover management system with SSO authentication, nginx reverse proxy, production deployment, and modern admin interface.

## 🆕 Latest Updates (October 2025)

### ✨ Major Features Completed ✅

#### � SSO Authentication (WORKING)
- **✅ Google OAuth Integration**: Fully implemented and tested
- **✅ User Profile Display**: Shows given_name, family_name, and picture
- **✅ Claims Integration**: Complete user profile from SSO provider
- **✅ Admin Configuration**: Visual dashboard for managing SSO providers
- **✅ Secure Storage**: Encrypted configuration using Fernet encryption

#### 🌐 Production Deployment (WORKING)
- **✅ Port Mapping**: Direct IP access without port specification
- **✅ nginx Reverse Proxy**: Production-grade proxy with security headers
- **✅ Docker Compose**: Ready-to-deploy production configuration
- **✅ Health Monitoring**: Working health endpoint at `/health`
- **✅ Current Access**: `http://35.200.202.18` (Port 80 → Flask 5000)

#### 📧 Email Recipients Management
- **Admin Dashboard Integration**: New "Email Recipients" tab in Secrets Management
- **Configurable Recipients**: Separate lists for handover notifications and priority alerts
- **Email Testing**: Built-in test functionality to verify email delivery
- **Toggle Notifications**: Enable/disable email notifications globally

#### 🛡️ Enhanced Security
- **Security Headers**: HSTS, CSP, XSS protection
- **Rate Limiting**: Protection against brute force attacks
- **Secure Session Management**: Production-ready session configuration

## ✨ Key Features

### 🔐 SSO Authentication
- **Multi-Provider Support**: Google OAuth, Azure AD, SAML 2.0, Generic OAuth, LDAP
- **Admin Configuration**: Visual dashboard for managing SSO providers  
- **Secure Storage**: Encrypted configuration storage using Fernet encryption
- **Role-Based Access**: Admin-only access to SSO configuration
- **Seamless Integration**: Built-in authentication flows with user provisioning

### 📊 Core Application Features
- **Shift Handover Management**: Create, edit, and track shift handovers
- **ServiceNow Integration**: Automated CTask assignment and incident tracking
- **Team Management**: Roster management with role-based permissions
- **Dashboard Analytics**: Real-time metrics and shift status monitoring
- **Audit Logging**: Comprehensive activity tracking and reporting
- **Email Notifications**: Automated notifications with configurable recipients

## 🚀 Quick Deployment Guide

### 🎯 Option 1: Production Deployment (Current Setup)

**Current Status**: ✅ **WORKING** - Application accessible at `http://35.200.202.18`

1. **Clone the Repository**
```bash
git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git
cd shifthandover
```

2. **Quick Production Setup**
```bash
# Run the automated port mapping script
chmod +x simple-port-mapping.sh
./simple-port-mapping.sh
```

3. **Verify Deployment**
```bash
# Check health endpoint
curl http://35.200.202.18/health

# Expected response:
{
  "services": {
    "application": "up",
    "database": "up"
  },
  "status": "healthy"
}
```

### 🎯 Option 2: Domain-Based Deployment (Future)

For domain access with `handover.lab.epam.com`:

1. **Configure Domain Environment**
```bash
cp .env.epam-lab .env.production
# Configure NAT mapping: handover.lab.epam.com → 35.200.202.18

# Deploy with domain support
chmod +x setup-epam-lab.sh
./setup-epam-lab.sh
```

### 🎯 Option 3: Local Development Setup

```bash
# Clone repository
git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git
cd shifthandover

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up local environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_local_db.py

# Run development server
python run_local.py
# Access: http://localhost:5000
```

## 🔧 Production Architecture

### Current Setup
```
Internet → 35.200.202.18:80 → nginx → Flask App:5000 → MySQL Database
```

### Services Running
- **nginx**: Reverse proxy (Port 80 → 5000)
- **Flask App**: Main application (Port 5000)
- **MySQL**: Database (Port 3306)
- **Health Check**: Available at `/health`

## 🔧 SSO Configuration

### Google OAuth Setup (Working)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set authorized redirect URI: `http://35.200.202.18/auth/sso/callback/google_oauth`
6. Copy Client ID and Client Secret to SSO configuration
7. **Status**: ✅ Configured and working

### Test SSO Integration
```bash
# Access the application
curl http://35.200.202.18/login

# Or visit in browser:
# http://35.200.202.18/login
```

## 🚢 Docker Commands

### Production Deployment
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs web

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Maintenance Commands
```bash
# Clean nginx configuration conflicts
chmod +x cleanup-nginx.sh
./cleanup-nginx.sh

# Backup application
./scripts/backup_application.sh

# Deploy updates
./scripts/vm_deploy.sh
```

## 🔒 Security Features
- **✅ Encrypted Storage**: All SSO configurations encrypted using Fernet
- **✅ Environment Variables**: Sensitive data stored in environment variables
- **✅ CSRF Protection**: Built-in cross-site request forgery protection
- **✅ Session Security**: Secure session management with proper timeouts
- **✅ Role-Based Access**: Admin-only access to sensitive configurations
- **✅ Rate Limiting**: nginx-based rate limiting for API endpoints
- **✅ Security Headers**: Comprehensive security headers implementation

## 📊 Monitoring & Health Checks

### Health Endpoint
```bash
# Check application health
curl http://35.200.202.18/health

# Check specific services
curl http://35.200.202.18/health?service=database
curl http://35.200.202.18/health?service=application
```

### Application Monitoring
- **Application Logs**: Comprehensive logging with rotating file handlers
- **Audit Trail**: User activity tracking and security auditing
- **Health Checks**: Built-in health monitoring endpoints
- **Performance Metrics**: Response time and usage analytics

## 🌐 Access Information

### Current Production Access
- **Main Application**: http://35.200.202.18
- **Health Check**: http://35.200.202.18/health
- **SSO Login**: http://35.200.202.18/login
- **Admin Dashboard**: http://35.200.202.18/admin/configuration

### Future Domain Access (After NAT Setup)
- **Main Application**: http://handover.lab.epam.com
- **Health Check**: http://handover.lab.epam.com/health

## 🛠 Technical Stack
- **Backend**: Flask, SQLAlchemy, MySQL
- **Frontend**: Modern HTML5, CSS3, JavaScript with responsive design
- **Authentication**: Flask-Login with Google OAuth SSO
- **Proxy**: nginx reverse proxy with rate limiting
- **Security**: Encrypted configurations, CSRF protection, secure sessions
- **Deployment**: Docker Compose, automated scripts
- **API Integration**: ServiceNow REST API, OAuth 2.0 providers

## 📚 Documentation Files

- **[Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)**: Complete deployment instructions
- **[nginx Fix Guide](NGINX_FIX_GUIDE.md)**: Troubleshooting nginx issues
- **[Domain Setup Guide](DOMAIN_SETUP_GUIDE.md)**: Domain configuration
- **[VM Deployment Success](VM_DEPLOYMENT_SUCCESS.md)**: Deployment verification

## 🚀 Quick Commands Reference

### Deployment
```bash
# Quick production setup
./simple-port-mapping.sh

# Domain setup (future)
./setup-epam-lab.sh

# Clean nginx conflicts
./cleanup-nginx.sh
```

### Monitoring
```bash
# Check services
docker-compose -f docker-compose.prod.yml ps

# Test health
curl http://35.200.202.18/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Maintenance
```bash
# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx

# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build web
```

## 🌐 GitLab Integration
- **Repository**: https://git.garage.epam.com/shift-handover-automation/shifthandover
- **Current Branch**: main
- **Latest Commit**: Complete SSO implementation with port mapping
- **CI/CD Pipelines**: Available for automated build and deployment

---

**🎉 Status**: Production Ready ✅  
**🌐 Access**: http://35.200.202.18  
**🔐 SSO**: Google OAuth Working ✅  
**💾 Repository**: https://git.garage.epam.com/shift-handover-automation/shifthandover  
**📅 Last Updated**: October 27, 2025  
**🏷 Version**: 2.0 with Complete SSO Integration and Production Deployment
# Quick deployment command
Copy-Item .env.https.template .env.production
# Edit .env.production with your domain and credentials
docker-compose -f docker-compose.https.yml up -d
```

### 🚀 Deployment Options

#### Development
```bash
docker-compose up -d
# Access: http://localhost:5000
```

#### Production HTTPS
```bash
docker-compose -f docker-compose.https.yml up -d
# Access: https://yourdomain.com
```

### 📚 Documentation

- **[Quick HTTPS Setup](QUICK_HTTPS_SETUP.md)**: Fast deployment guide
- **[Complete Deployment Guide](HTTPS_DEPLOYMENT_GUIDE.md)**: Detailed instructions
- **[Security Configuration](SECURE_CONFIGURATION_GUIDE.md)**: Security best practices
- **Export Features**: Export incidents/key points to PDF/CSV

### 🛠 Technical Stack
- **Backend**: Flask, SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: Modern HTML5, CSS3, JavaScript with responsive design
- **Authentication**: Flask-Login with SSO integration
- **Security**: Encrypted configurations, CSRF protection, secure sessions
- **API Integration**: ServiceNow REST API, OAuth 2.0 providers

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment
- Database (SQLite for development, PostgreSQL for production)

### Local Development Setup
```bash
# Clone from GitLab
git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git
cd shifthandover

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your configuration

# Initialize database
python init_database.py

# Run the application
python app.py
```

### Access the Application
- **Main Application**: http://127.0.0.1:5000
- **SSO Configuration**: http://127.0.0.1:5000/admin/sso/ (Admin only)
- **Admin Dashboard**: http://127.0.0.1:5000/admin/configuration

## 🔧 SSO Configuration

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set authorized redirect URI: `http://your-domain/auth/sso/callback/google_oauth`
6. Copy Client ID and Client Secret to SSO configuration

### Azure AD Setup
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Azure Active Directory > App registrations
3. Create new registration
4. Configure redirect URI: `http://your-domain/auth/sso/callback/azure_ad`
5. Generate client secret
6. Copy Application (client) ID and client secret

## 🚢 Docker Deployment

### Quick Start with Docker
```bash
# Build and start the containers
docker-compose up --build

# Access the application at http://localhost:5000

# Initialize the database (in a new terminal)
docker-compose exec web flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

### Production Docker Setup
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up --build
```

## 🔒 Security Features
- **Encrypted Storage**: All SSO configurations encrypted using Fernet
- **Environment Variables**: Sensitive data stored in environment variables
- **CSRF Protection**: Built-in cross-site request forgery protection
- **Session Security**: Secure session management with proper timeouts
- **Role-Based Access**: Admin-only access to sensitive configurations

## 🌐 GitLab Integration
- **Repository**: https://git.garage.epam.com/shift-handover-automation/shifthandover
- **CI/CD Pipelines**: Available for automated build and deployment
- **Merge Requests**: Code review and collaboration features
- **Project Management**: Issue tracking and milestone management

## 📊 Monitoring & Logging
- **Application Logs**: Comprehensive logging with rotating file handlers
- **Audit Trail**: User activity tracking and security auditing
- **Health Checks**: Built-in health monitoring endpoints
- **Performance Metrics**: Response time and usage analytics

---

**Repository**: https://git.garage.epam.com/shift-handover-automation/shifthandover
**Last Updated**: October 25, 2024
**Version**: 2.0 with SSO Integration and Modern UI

## Notes
- For proof-of-concept, authentication uses static credentials.
- Replace SMTP and DB credentials in `.env` for production use.
