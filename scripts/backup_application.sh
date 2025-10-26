#!/bin/bash

# ========================================
# Shift Handover Application Backup Script
# ========================================
# This script creates comprehensive backups of the application and database
# Usage: ./backup_application.sh [backup_type]
# backup_type: daily, weekly, monthly (default: daily)

set -euo pipefail

# Configuration
APP_DIR="/home/shifthandoversajid/shift_handover_app_26102025"
BACKUP_BASE_DIR="/home/shifthandoversajid/backups"
BACKUP_TYPE="${1:-daily}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_TYPE}/${TIMESTAMP}"

# Retention settings (days)
DAILY_RETENTION=7
WEEKLY_RETENTION=30
MONTHLY_RETENTION=90

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if application directory exists
check_prerequisites() {
    log "Checking prerequisites..."
    
    if [ ! -d "$APP_DIR" ]; then
        error "Application directory not found: $APP_DIR"
        exit 1
    fi
    
    # Create backup directories
    mkdir -p "$BACKUP_DIR"/{application,database,logs,config}
    
    # Check if Docker is running
    if ! docker ps &>/dev/null; then
        warning "Docker is not running or not accessible"
    fi
    
    success "Prerequisites checked"
}

# Backup application files
backup_application() {
    log "Starting application backup..."
    
    # Create application backup
    tar -czf "${BACKUP_DIR}/application/app_backup_${TIMESTAMP}.tar.gz" \
        -C "$(dirname "$APP_DIR")" \
        "$(basename "$APP_DIR")" \
        --exclude="*.pyc" \
        --exclude="__pycache__" \
        --exclude=".git" \
        --exclude="venv" \
        --exclude=".venv" \
        --exclude="node_modules" \
        --exclude="*.log" \
        --exclude="*.tmp"
    
    success "Application files backed up to ${BACKUP_DIR}/application/"
}

# Backup database
backup_database() {
    log "Starting database backup..."
    
    # Check if PostgreSQL container is running
    if docker ps --format "table {{.Names}}" | grep -q postgres; then
        POSTGRES_CONTAINER=$(docker ps --format "{{.Names}}" | grep postgres | head -1)
        
        # Get database configuration from app
        if [ -f "$APP_DIR/.env" ]; then
            source "$APP_DIR/.env"
        elif [ -f "$APP_DIR/.env.production" ]; then
            source "$APP_DIR/.env.production"
        fi
        
        DB_NAME="${DATABASE_NAME:-shift_handover}"
        DB_USER="${DATABASE_USER:-postgres}"
        
        # Create database dump
        docker exec "$POSTGRES_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" > \
            "${BACKUP_DIR}/database/db_backup_${TIMESTAMP}.sql"
        
        # Create compressed backup
        gzip "${BACKUP_DIR}/database/db_backup_${TIMESTAMP}.sql"
        
        success "Database backed up to ${BACKUP_DIR}/database/"
    else
        # Try local PostgreSQL backup
        if command -v pg_dump &>/dev/null; then
            log "Using local PostgreSQL for backup..."
            
            # Source environment variables
            if [ -f "$APP_DIR/.env" ]; then
                source "$APP_DIR/.env"
            elif [ -f "$APP_DIR/.env.production" ]; then
                source "$APP_DIR/.env.production"
            fi
            
            DB_NAME="${DATABASE_NAME:-shift_handover}"
            DB_USER="${DATABASE_USER:-postgres}"
            DB_HOST="${DATABASE_HOST:-localhost}"
            DB_PORT="${DATABASE_PORT:-5432}"
            
            PGPASSWORD="$DATABASE_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | \
                gzip > "${BACKUP_DIR}/database/db_backup_${TIMESTAMP}.sql.gz"
            
            success "Database backed up using local PostgreSQL"
        else
            warning "No PostgreSQL found for database backup"
        fi
    fi
}

# Backup configuration files
backup_config() {
    log "Backing up configuration files..."
    
    # Backup environment files (without sensitive data)
    if [ -f "$APP_DIR/.env" ]; then
        cp "$APP_DIR/.env" "${BACKUP_DIR}/config/env_backup_${TIMESTAMP}"
    fi
    
    if [ -f "$APP_DIR/.env.production" ]; then
        cp "$APP_DIR/.env.production" "${BACKUP_DIR}/config/env_production_backup_${TIMESTAMP}"
    fi
    
    # Backup Docker configurations
    if [ -f "$APP_DIR/docker-compose.yml" ]; then
        cp "$APP_DIR/docker-compose.yml" "${BACKUP_DIR}/config/"
    fi
    
    if [ -f "$APP_DIR/docker-compose.production.yml" ]; then
        cp "$APP_DIR/docker-compose.production.yml" "${BACKUP_DIR}/config/"
    fi
    
    # Backup Nginx configuration if exists
    if [ -d "$APP_DIR/nginx" ]; then
        tar -czf "${BACKUP_DIR}/config/nginx_config_${TIMESTAMP}.tar.gz" -C "$APP_DIR" nginx/
    fi
    
    success "Configuration files backed up"
}

# Backup application logs
backup_logs() {
    log "Backing up application logs..."
    
    # Find and backup log files
    find "$APP_DIR" -name "*.log" -type f -exec cp {} "${BACKUP_DIR}/logs/" \; 2>/dev/null || true
    
    # Backup Docker container logs if available
    if docker ps &>/dev/null; then
        for container in $(docker ps --format "{{.Names}}"); do
            docker logs "$container" > "${BACKUP_DIR}/logs/${container}_${TIMESTAMP}.log" 2>&1 || true
        done
    fi
    
    success "Application logs backed up"
}

# Clean old backups based on retention policy
cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    case $BACKUP_TYPE in
        daily)
            RETENTION_DAYS=$DAILY_RETENTION
            ;;
        weekly)
            RETENTION_DAYS=$WEEKLY_RETENTION
            ;;
        monthly)
            RETENTION_DAYS=$MONTHLY_RETENTION
            ;;
        *)
            RETENTION_DAYS=$DAILY_RETENTION
            ;;
    esac
    
    # Remove backups older than retention period
    find "${BACKUP_BASE_DIR}/${BACKUP_TYPE}" -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    success "Old backups cleaned up (retention: ${RETENTION_DAYS} days)"
}

# Create backup manifest
create_manifest() {
    log "Creating backup manifest..."
    
    cat > "${BACKUP_DIR}/backup_manifest.txt" << EOF
Backup Information
==================
Backup Type: $BACKUP_TYPE
Timestamp: $TIMESTAMP
Date: $(date)
Hostname: $(hostname)
User: $(whoami)

Application Directory: $APP_DIR
Backup Directory: $BACKUP_DIR

Files Backed Up:
$(find "$BACKUP_DIR" -type f -exec ls -lh {} \; | awk '{print $9, $5}')

System Information:
==================
OS: $(uname -a)
Disk Usage: $(df -h "$BACKUP_DIR" | tail -1)
Memory: $(free -h | grep "Mem:" || echo "N/A")
Docker Status: $(docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "Docker not available")

Backup Completed: $(date)
EOF
    
    success "Backup manifest created"
}

# Send notification (optional)
send_notification() {
    local status=$1
    local message=$2
    
    # You can customize this to send email, Slack, or other notifications
    log "Backup $status: $message"
    
    # Example: Send to syslog
    logger "Shift Handover Backup $status: $message"
}

# Main backup process
main() {
    log "Starting backup process - Type: $BACKUP_TYPE"
    
    # Check prerequisites
    check_prerequisites
    
    # Start backup process
    backup_application
    backup_database
    backup_config
    backup_logs
    
    # Create manifest
    create_manifest
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Calculate backup size
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    
    success "Backup completed successfully!"
    log "Backup location: $BACKUP_DIR"
    log "Backup size: $BACKUP_SIZE"
    
    # Send success notification
    send_notification "SUCCESS" "Backup completed. Size: $BACKUP_SIZE, Location: $BACKUP_DIR"
}

# Error handling
trap 'error "Backup failed at line $LINENO"; send_notification "FAILED" "Backup failed at line $LINENO"; exit 1' ERR

# Run main function
main "$@"