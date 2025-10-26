# Backup and Restore Scripts for GCP VM

This directory contains comprehensive backup and restore scripts for your Shift Handover Application running on GCP VM.

## 📁 Scripts Overview

### 1. `backup_application.sh`
Complete application backup script that creates:
- Application files backup (compressed tar.gz)
- Database backup (PostgreSQL dump)
- Configuration files backup
- Application logs backup
- Backup manifest with metadata

**Usage:**
```bash
./backup_application.sh [daily|weekly|monthly]
```

**Features:**
- Automatic retention management
- Docker and local PostgreSQL support
- Comprehensive logging
- Error handling and notifications

### 2. `db_backup.sh`
Dedicated database backup and restore utility:
- Create database backups
- Restore from backups
- List available backups
- Cleanup old backups
- Schedule automatic backups

**Usage:**
```bash
./db_backup.sh backup [name]          # Create backup
./db_backup.sh restore <file>         # Restore from backup
./db_backup.sh list                   # List backups
./db_backup.sh cleanup [days]         # Remove old backups
./db_backup.sh test                   # Test connection
```

### 3. `deploy_backup_scripts.sh`
Deployment script to set up the backup system on your GCP VM:
- Uploads scripts to VM
- Configures automatic schedules
- Sets up monitoring
- Creates directory structure

**Usage:**
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