#!/bin/bash

# GCP VM Deployment Script for Shift Handover App
# Usage: Run this script on your GCP VM

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"; }
warning() { echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"; }
error() { echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"; }

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CURRENT_APP_DIR="/home/shifthandoversajid/shift_handover_app_26102025"
NEW_APP_DIR="/home/shifthandoversajid/shift_handover_app_new"
BACKUP_DIR="/home/shifthandoversajid/shift_handover_app_backup_${TIMESTAMP}"

echo "======================================="
echo "Shift Handover App Deployment Script"
echo "======================================="
echo "Timestamp: $TIMESTAMP"
echo "Current App: $CURRENT_APP_DIR"
echo "New App: $NEW_APP_DIR"
echo "Backup: $BACKUP_DIR"
echo ""

# Step 1: Backup current application
backup_current_app() {
    log "Step 1: Backing up current application..."
    
    if [ -d "$CURRENT_APP_DIR" ]; then
        cp -r "$CURRENT_APP_DIR" "$BACKUP_DIR"
        success "Application backed up to: $BACKUP_DIR"
    else
        warning "Current application directory not found: $CURRENT_APP_DIR"
    fi
    
    # Backup database
    log "Creating database backup..."
    if [ -f "/home/shifthandoversajid/scripts/mysql_backup.sh" ]; then
        /home/shifthandoversajid/scripts/mysql_backup.sh backup "pre_deployment_${TIMESTAMP}"
        success "Database backup created"
    else
        warning "MySQL backup script not found"
    fi
}

# Step 2: Stop current application
stop_current_app() {
    log "Step 2: Stopping current application..."
    
    if [ -d "$CURRENT_APP_DIR" ]; then
        cd "$CURRENT_APP_DIR"
        if [ -f "docker-compose.yml" ]; then
            docker-compose down
            success "Current application stopped"
        else
            warning "docker-compose.yml not found in current app directory"
        fi
    else
        warning "Current application directory not found"
    fi
}

# Step 3: Prepare new application directory
prepare_new_app() {
    log "Step 3: Preparing new application directory..."
    
    # Create new app directory if it doesn't exist
    mkdir -p "$NEW_APP_DIR"
    success "New application directory prepared: $NEW_APP_DIR"
}

# Step 4: Configure environment for VM
configure_environment() {
    log "Step 4: Configuring environment for VM..."
    
    cd "$NEW_APP_DIR"
    
    # Create production environment file
    cat > .env.production << 'ENV'
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-change-this
DEBUG=False

# Database Configuration  
DATABASE_URI=mysql+pymysql://user:password@db/shift_handover
DATABASE_NAME=shift_handover
DATABASE_USER=user
DATABASE_PASSWORD=password
DATABASE_HOST=db
DATABASE_PORT=3306

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=mdsajid020@gmail.com
SMTP_PASSWORD=uovrivxvitovrjcu
TEAM_EMAIL=mdsajid020@gmail.com

# SSO Configuration (from existing app)
SSO_ENCRYPTION_KEY=crEMXD5xdXNui5q8dEQ25A1WHdXqxc4FKPwacV3O_Qk=

# Security Headers
FORCE_HTTPS=False
DOMAIN_NAME=35.200.202.18
ENV
    
    # Copy existing .env if it exists in current app
    if [ -f "$CURRENT_APP_DIR/.env" ]; then
        log "Copying existing .env configuration..."
        cp "$CURRENT_APP_DIR/.env" "$NEW_APP_DIR/.env.backup"
        
        # Extract SSO key from existing config
        if grep -q "SSO_ENCRYPTION_KEY" "$CURRENT_APP_DIR/.env"; then
            SSO_KEY=$(grep "SSO_ENCRYPTION_KEY" "$CURRENT_APP_DIR/.env" | cut -d'=' -f2)
            sed -i "s/SSO_ENCRYPTION_KEY=.*/SSO_ENCRYPTION_KEY=$SSO_KEY/" .env.production
        fi
    fi
    
    # Create main .env file
    cp .env.production .env
    
    success "Environment configuration completed"
}

# Step 5: Deploy new application
deploy_new_app() {
    log "Step 5: Deploying new application..."
    
    cd "$NEW_APP_DIR"
    
    # Use production docker-compose if available, otherwise create one
    if [ -f "docker-compose.production.yml" ]; then
        cp docker-compose.production.yml docker-compose.yml
        log "Using production docker-compose configuration"
    elif [ -f "$CURRENT_APP_DIR/docker-compose.yml" ]; then
        cp "$CURRENT_APP_DIR/docker-compose.yml" ./
        log "Using existing docker-compose configuration"
    else
        # Create basic docker-compose.yml
        cat > docker-compose.yml << 'COMPOSE'
version: '3.3'

services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_DATABASE: shift_handover
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql

  web:
    build: .
    command: flask run --host=0.0.0.0
    volumes:
      - .:/app
    ports:
      - "5000:5000"
    env_file:
      - .env
    environment:
      - FLASK_ENV=production
      - DATABASE_URI=mysql+pymysql://user:password@db/shift_handover
      - SMTP_SERVER=smtp.gmail.com
      - SMTP_PORT=587
      - SMTP_USERNAME=mdsajid020@gmail.com
      - SMTP_PASSWORD=uovrivxvitovrjcu
      - TEAM_EMAIL=mdsajid020@gmail.com
    depends_on:
      - db

volumes:
  db_data:
COMPOSE
        log "Created basic docker-compose configuration"
    fi
    
    # Deploy application
    log "Building and starting new application..."
    docker-compose up -d --build
    
    success "New application deployed successfully"
}

# Step 6: Verify deployment
verify_deployment() {
    log "Step 6: Verifying deployment..."
    
    # Wait a moment for containers to start
    sleep 10
    
    # Check if containers are running
    log "Checking container status..."
    docker ps
    
    # Test application health
    log "Testing application health..."
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        success "Application health check passed"
    elif curl -f http://localhost:5000 >/dev/null 2>&1; then
        success "Application is responding"
    else
        warning "Application health check failed - manual verification needed"
    fi
    
    success "Deployment verification completed"
}

# Step 7: Display access information
show_access_info() {
    log "Step 7: Deployment completed successfully!"
    
    echo ""
    echo "🎉 APPLICATION DEPLOYED SUCCESSFULLY! 🎉"
    echo "========================================"
    echo ""
    echo "Access URLs:"
    echo "  Main Application: http://35.200.202.18:5000"
    echo "  Admin Dashboard:  http://35.200.202.18:5000/admin/secrets"
    echo "  Login Page:       http://35.200.202.18:5000/login"
    echo ""
    echo "Container Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Application Logs:"
    echo "  View logs: cd $NEW_APP_DIR && docker-compose logs -f"
    echo ""
    echo "Backup Information:"
    echo "  Application backup: $BACKUP_DIR"
    echo "  Database backup: /home/shifthandoversajid/backups/database/"
    echo ""
    echo "Next Steps:"
    echo "  1. Test the application using the URLs above"
    echo "  2. Verify all functionality works as expected"
    echo "  3. If issues occur, use rollback_deployment.sh"
    echo ""
}

# Rollback function
create_rollback_script() {
    log "Creating rollback script..."
    
    cat > "/home/shifthandoversajid/rollback_deployment.sh" << ROLLBACK
#!/bin/bash

# Rollback script for deployment ${TIMESTAMP}

echo "Rolling back deployment..."

# Stop new application
cd "$NEW_APP_DIR"
docker-compose down

# Start old application
cd "$BACKUP_DIR"
docker-compose up -d

echo "Rollback completed. Application restored from backup."
echo "Access: http://35.200.202.18:5000"
ROLLBACK
    
    chmod +x "/home/shifthandoversajid/rollback_deployment.sh"
    success "Rollback script created: /home/shifthandoversajid/rollback_deployment.sh"
}

# Main execution
main() {
    backup_current_app
    stop_current_app
    prepare_new_app
    configure_environment
    create_rollback_script
    
    # At this point, we need the new application files
    echo ""
    warning "NEW APPLICATION FILES NEEDED!"
    echo "Please upload your new application files to: $NEW_APP_DIR"
    echo ""
    echo "After uploading files, run:"
    echo "  cd $NEW_APP_DIR"
    echo "  docker-compose up -d --build"
    echo ""
    echo "Or continue with automated deployment by running:"
    echo "  deploy_new_app"
    echo "  verify_deployment"
    echo "  show_access_info"
}

# Check command line arguments
case "${1:-main}" in
    backup)
        backup_current_app
        ;;
    stop)
        stop_current_app
        ;;
    configure)
        configure_environment
        ;;
    deploy)
        deploy_new_app
        ;;
    verify)
        verify_deployment
        ;;
    info)
        show_access_info
        ;;
    rollback)
        if [ -f "/home/shifthandoversajid/rollback_deployment.sh" ]; then
            /home/shifthandoversajid/rollback_deployment.sh
        else
            error "Rollback script not found"
        fi
        ;;
    *)
        main
        ;;
esac