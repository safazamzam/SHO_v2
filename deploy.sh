#!/bin/bash

echo "🚀 Starting deployment to GCP VM..."
echo "=================================="

# Configuration
VM_IP="35.200.202.18"
VM_USER="shift_admin"
PROJECT_NAME="shift-handover-app"
REMOTE_DIR="/home/$VM_USER/$PROJECT_NAME"

echo "📦 Building Docker images locally..."

# Build the application
docker-compose build

echo "✅ Docker images built successfully"

echo "📤 Transferring files to VM..."

# Create remote directory if it doesn't exist
ssh $VM_USER@$VM_IP "mkdir -p $REMOTE_DIR"

# Transfer docker-compose.yml and related files
scp docker-compose.yml $VM_USER@$VM_IP:$REMOTE_DIR/
scp Dockerfile $VM_USER@$VM_IP:$REMOTE_DIR/
scp requirements.txt $VM_USER@$VM_IP:$REMOTE_DIR/
scp start.sh $VM_USER@$VM_IP:$REMOTE_DIR/
scp app.py $VM_USER@$VM_IP:$REMOTE_DIR/
scp config.py $VM_USER@$VM_IP:$REMOTE_DIR/

# Transfer application directories
scp -r templates/ $VM_USER@$VM_IP:$REMOTE_DIR/
scp -r static/ $VM_USER@$VM_IP:$REMOTE_DIR/
scp -r blueprints/ $VM_USER@$VM_IP:$REMOTE_DIR/
scp -r models/ $VM_USER@$VM_IP:$REMOTE_DIR/
scp -r utils/ $VM_USER@$VM_IP:$REMOTE_DIR/

echo "✅ Files transferred successfully"

echo "🔧 Deploying on remote VM..."

# Execute deployment commands on VM
ssh $VM_USER@$VM_IP << 'ENDSSH'
cd /home/shift_admin/shift-handover-app

echo "🛑 Stopping existing containers..."
docker-compose down

echo "🔄 Pulling latest images and rebuilding..."
docker-compose build --no-cache

echo "🚀 Starting updated containers..."
docker-compose up -d

echo "⏱️  Waiting for services to start..."
sleep 10

echo "🔍 Checking container status..."
docker-compose ps

echo "📊 Checking application logs..."
docker-compose logs web --tail=20

ENDSSH

echo "=================================="
echo "✅ Deployment completed!"
echo "🌐 Application should be available at: http://$VM_IP:5000"
echo "📊 To check logs: ssh $VM_USER@$VM_IP 'cd $REMOTE_DIR && docker-compose logs web'"
echo "🔧 To restart: ssh $VM_USER@$VM_IP 'cd $REMOTE_DIR && docker-compose restart'"