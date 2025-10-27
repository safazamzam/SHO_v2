# 🚀 Deployment and Management Scripts

This directory contains production deployment and management scripts for the Shift Handover Application.

## 📁 Scripts Overview

### 🚀 Deployment Scripts

#### 1. `vm_deploy.sh`
Primary deployment script for production VM setup:
- Deploys application to GCP VM (35.200.202.18)
- Configures Docker Compose production environment
- Sets up nginx reverse proxy with port mapping
- Verifies deployment health

**Usage:**
```bash
./vm_deploy.sh
```

**Features:**
- Automatic Docker Compose setup
- nginx configuration with port 80 → 5000 mapping
- Health check verification
- Production environment configuration

#### 2. `backup_application.sh`
Complete application backup script that creates:
- Application files backup (compressed tar.gz)
- Database backup (MySQL dump)
- Configuration files backup
- nginx configuration backup
- Application logs backup
- Backup manifest with metadata

**Usage:**
```bash
./backup_application.sh [daily|weekly|monthly]
```

**Features:**
- Automatic retention management
- Docker MySQL support
- Comprehensive logging
- Error handling and notifications
- Backup to multiple locations

### 🔧 Configuration Scripts

#### Available in Root Directory:

1. **`simple-port-mapping.sh`** ✅ **WORKING**
   - Maps port 80 → 5000 for direct IP access
   - Cleans conflicting nginx configurations
   - Enables access via `http://35.200.202.18`

2. **`cleanup-nginx.sh`** ✅ **COMPREHENSIVE**
   - Comprehensive nginx cleanup and configuration
   - Fixes duplicate rate limiting zones
   - Sets up clean reverse proxy configuration

3. **`setup-epam-lab.sh`**
   - Domain setup for `handover.lab.epam.com`
   - Requires NAT configuration

4. **`setup-http-only.sh`**
   - HTTP-only deployment without SSL
   - Suitable for development/testing

### 🔐 SSO and User Management

#### Available in Root Directory:

1. **`update_sso_profile.py`** ✅ **WORKING**
   - Updates user profiles from SSO claims
   - Integrates given_name, family_name, picture

2. **`create_admin.py`**
   - Creates admin users for application
   - Sets up initial access credentials

3. **`debug_user_profile.py`**
   - Debugging tool for user profile issues
   - Validates SSO integration

### 📊 Monitoring and Maintenance

#### Health Checks
```bash
# Check application health
curl http://35.200.202.18/health

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Service Management
```bash
# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx

# Restart entire stack
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build web
```
```bash
./deploy_backup_scripts.sh
```

## 🚀 Quick Deployment

### Step 1: Deploy Scripts to VM
```bash
# From your local machine (Windows PowerShell or Git Bash)
cd scripts
./deploy_backup_scripts.sh
```

### Step 2: Verify Installation
```bash
# SSH to your VM
ssh -i ~/.ssh/my-gcp-key shifthandoversajid@35.200.202.18

# Check backup status
./scripts/backup_monitor.sh

# Test database connection
./scripts/db_backup.sh test
```

### Step 3: Create First Backup
```bash
# Create a test backup
./scripts/db_backup.sh backup "initial_backup"

# Create full application backup
./scripts/backup_application.sh daily
```

## ⏰ Automatic Schedule

The deployment script sets up these automatic backups:

| Type | Schedule | Retention |
|------|----------|-----------|
| Daily App Backup | 2:00 AM | 7 days |
| Weekly App Backup | 3:00 AM Sunday | 30 days |
| Monthly App Backup | 4:00 AM 1st day | 90 days |
| Database Backup | Every 6 hours | 30 days |
| Cleanup | 5:00 AM daily | - |

## 📊 Monitoring

### Check Backup Status
```bash
./scripts/backup_monitor.sh
```

### View Logs
```bash
tail -f logs/backup.log
tail -f logs/db_backup.log
tail -f logs/cleanup.log
```

### Check Scheduled Jobs
```bash
crontab -l
```

## 🔧 Configuration

### VM Details
- **IP**: 35.200.202.18
- **User**: shifthandoversajid
- **SSH Key**: ~/.ssh/my-gcp-key
- **App Directory**: /home/shifthandoversajid/shift_handover_app_26102025

### Backup Locations
- **Scripts**: `/home/shifthandoversajid/scripts/`
- **Backups**: `/home/shifthandoversajid/backups/`
- **Logs**: `/home/shifthandoversajid/logs/`

### Environment Support
- Docker PostgreSQL containers
- Local PostgreSQL installations
- Development and production environments

## 🚨 Important Notes

1. **Permissions**: Scripts automatically set correct permissions
2. **Database**: Auto-detects Docker or local PostgreSQL
3. **Storage**: Monitor disk space in backup directory
4. **Security**: No sensitive data stored in scripts
5. **Testing**: Test restore process regularly

## 📞 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# Test connection manually
./scripts/db_backup.sh test
```

**Backup Script Not Executable**
```bash
chmod +x scripts/*.sh
```

**Disk Space Issues**
```bash
# Check disk usage
df -h /home/shifthandoversajid/backups

# Clean old backups
./scripts/db_backup.sh cleanup 7
```

**Cron Jobs Not Running**
```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
sudo tail -f /var/log/cron
```

## 🔄 Restore Process

### Full Application Restore
1. Stop application services
2. Restore database from backup
3. Extract application files
4. Restart services

### Database-Only Restore
```bash
# List available backups
./scripts/db_backup.sh list

# Restore specific backup
./scripts/db_backup.sh restore /path/to/backup.sql.gz
```

This backup system ensures your Shift Handover Application data is protected with automated, reliable backups! 🛡️