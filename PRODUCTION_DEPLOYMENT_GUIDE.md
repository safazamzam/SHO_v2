# 🚀 Production Deployment Guide

## 📋 Overview
This guide covers deploying the Shift Handover Application using the unified `docker-compose.yml` with Docker secrets for secure credential management.

## 🔐 Security Architecture

### **Tier 1: Infrastructure Secrets (Docker Secrets)**
- Database credentials (MySQL user/root passwords)
- Flask session key
- SSO encryption key  
- Master encryption key for database secrets

### **Tier 2: Application Secrets (Encrypted Database)**
- SMTP credentials
- ServiceNow configuration
- Email recipients lists
- Feature toggles

## 📁 Required Files Structure

```
shift_handover_app/
├── docker-compose.yml          # Main deployment file
├── Dockerfile                  # Application container
├── app.py                     # Main application
├── requirements.txt           # Python dependencies
├── start.sh                   # Application startup script
├── init_local.sql            # Database initialization
├── secrets/                   # Docker secrets directory
│   ├── flask_secret_key       # Flask session encryption
│   ├── database_url           # Full database connection string
│   ├── sso_encryption_key     # SSO encryption key
│   ├── secrets_master_key     # Master key for database encryption
│   ├── mysql_password         # Database user password
│   ├── mysql_root_password    # Database root password
│   ├── mysql_user_password    # Alternative database password
│   ├── smtp_username          # SMTP username (fallback)
│   └── smtp_password          # SMTP password (fallback)
├── models/                    # Application models
├── routes/                    # Application routes
├── services/                  # Application services
├── templates/                 # HTML templates
└── static/                    # Static files
```

## 🛠️ Deployment Steps

### Step 1: Prepare Secrets Directory
```bash
# Ensure secrets directory exists with proper permissions
chmod 700 ./secrets/
chmod 600 ./secrets/*
```

### Step 2: Local Development Deployment
```bash
# Stop any existing containers
docker-compose down -v

# Start services
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f web
```

### Step 3: Initialize Database
```bash
# Create database tables
docker-compose exec web python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database initialized')
"
```

### Step 4: Production VM Deployment
```bash
# Upload files to VM
scp -r . user@vm-ip:/path/to/app/

# Connect to VM and deploy
ssh user@vm-ip
cd /path/to/app/
docker-compose up -d --build
```

## 🔧 Configuration Management

### Database Configuration
All managed via admin dashboard at `/admin/secrets`:
- SMTP settings
- Email recipients
- ServiceNow configuration
- Feature toggles
- Application settings

### Environment Modes
- **Development**: `FLASK_ENV=development`, `FLASK_DEBUG=1`
- **Production**: `FLASK_ENV=production`, `FLASK_DEBUG=0`

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Main App** | `http://localhost:5000` | Application interface |
| **Admin Dashboard** | `http://localhost:5000/admin/secrets` | Configuration management |
| **Health Check** | `http://localhost:5000/health` | Service monitoring |
| **Database** | `localhost:3306` | Direct database access |

## 🔍 Monitoring & Logs

### Check Application Status
```bash
# Container status
docker-compose ps

# Application logs
docker-compose logs web

# Database logs  
docker-compose logs db

# Follow live logs
docker-compose logs -f
```

### Health Checks
```bash
# Application health
curl http://localhost:5000/health

# Database health
docker-compose exec db mysqladmin ping
```

## 🛡️ Security Checklist

- [ ] All secret files have proper permissions (600)
- [ ] Secrets directory has proper permissions (700)
- [ ] FLASK_DEBUG=0 in production
- [ ] Database passwords are unique and strong
- [ ] Application secrets are configured via admin dashboard
- [ ] Regular backups are configured
- [ ] Firewall rules are properly configured

## 🚨 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check database container
docker-compose logs db

# Verify secrets
docker-compose exec web cat /run/secrets/database_url
```

**Application Won't Start**
```bash
# Check application logs
docker-compose logs web

# Verify all secrets are mounted
docker-compose exec web ls -la /run/secrets/
```

**Secrets Not Loading**
```bash
# Check secret file permissions
ls -la secrets/

# Verify secret content
cat secrets/database_url
```

### Reset Deployment
```bash
# Complete reset
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

## 📝 Maintenance

### Backup Commands
```bash
# Database backup
docker-compose exec db mysqldump -u user -p$(cat secrets/mysql_password) shift_handover > backup.sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz . --exclude=.git
```

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Verify deployment
docker-compose ps
curl http://localhost:5000/health
```

## 🎯 Production Readiness

✅ **Docker secrets for secure credential management**  
✅ **Encrypted database storage for application settings**  
✅ **Health checks and monitoring**  
✅ **Proper security configurations**  
✅ **Volume persistence for data**  
✅ **Easy backup and restore procedures**  

Your application is now production-ready! 🚀