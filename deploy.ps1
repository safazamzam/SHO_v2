# PowerShell Deployment Script for Shift Handover App
# Deploy to GCP VM: 35.200.202.18

Write-Host "🚀 Starting deployment to GCP VM..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Yellow

# Configuration
$VM_IP = "35.200.202.18"
$VM_USER = "shift_admin"
$PROJECT_NAME = "shift-handover-app"
$REMOTE_DIR = "/home/$VM_USER/$PROJECT_NAME"

Write-Host "📦 Building Docker images locally..." -ForegroundColor Blue

# Build the application
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker images built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "📤 Transferring files to VM..." -ForegroundColor Blue

# Create remote directory if it doesn't exist
ssh $VM_USER@$VM_IP "mkdir -p $REMOTE_DIR"

# Transfer core files
scp docker-compose.yml ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp Dockerfile ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp requirements.txt ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp start.sh ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp app.py ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp config.py ${VM_USER}@${VM_IP}:${REMOTE_DIR}/

# Transfer application directories
scp -r templates/ ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp -r static/ ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp -r routes/ ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp -r models/ ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp -r services/ ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp -r instance/ ${VM_USER}@${VM_IP}:${REMOTE_DIR}/
scp -r migrations/ ${VM_USER}@${VM_IP}:${REMOTE_DIR}/

Write-Host "✅ Files transferred successfully" -ForegroundColor Green

Write-Host "🔧 Deploying on remote VM..." -ForegroundColor Blue

# Execute deployment commands on VM
$deployCommands = @"
cd $REMOTE_DIR
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
"@

ssh $VM_USER@$VM_IP $deployCommands

Write-Host "==================================" -ForegroundColor Yellow
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Application should be available at: http://$VM_IP:5000" -ForegroundColor Cyan
Write-Host "📊 To check logs: ssh $VM_USER@$VM_IP 'cd $REMOTE_DIR && docker-compose logs web'" -ForegroundColor Yellow
Write-Host "🔧 To restart: ssh $VM_USER@$VM_IP 'cd $REMOTE_DIR && docker-compose restart'" -ForegroundColor Yellow