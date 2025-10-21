# PowerShell script to deploy Shift Handover App updates to GCP VM
# This script will copy updated files and restart the Docker container

param(
    [string]$VMUser = "your-username",
    [string]$VMHost = "35.200.202.18",
    [string]$AppPath = "/opt/shift-handover-app"
)

Write-Host "🚀 Deploying Shift Handover App updates to GCP VM..." -ForegroundColor Green

# Configuration
$LocalPath = Get-Location
$TemplateFile = "templates\user_management.html"
$RoutesFile = "routes\user_management.py"

Write-Host "📂 Local path: $LocalPath" -ForegroundColor Yellow
Write-Host "🖥️ Target VM: $VMUser@$VMHost" -ForegroundColor Yellow

# Step 1: Copy updated files to GCP VM
Write-Host "📤 Copying updated files to GCP VM..." -ForegroundColor Cyan

try {
    # Copy user management template
    Write-Host "  - Copying $TemplateFile..."
    & scp "$TemplateFile" "${VMUser}@${VMHost}:${AppPath}/templates/"
    
    # Copy user management routes
    Write-Host "  - Copying $RoutesFile..."
    & scp "$RoutesFile" "${VMUser}@${VMHost}:${AppPath}/routes/"
    
    Write-Host "✅ Files copied successfully!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error copying files: $_" -ForegroundColor Red
    exit 1
}

# Step 2: SSH to GCP VM and restart Docker container
Write-Host "🔄 Restarting Docker container on GCP VM..." -ForegroundColor Cyan

$RestartCommands = @"
cd $AppPath && \
echo '🛑 Stopping current container...' && \
sudo docker-compose down && \
echo '🏗️ Rebuilding and starting container...' && \
sudo docker-compose up --build -d && \
echo '✅ Container restarted successfully!' && \
echo '🌐 App should be available at: http://$VMHost' && \
sudo docker-compose logs --tail=10 web
"@

try {
    Write-Host "  - Executing restart commands on VM..."
    & ssh "${VMUser}@${VMHost}" "$RestartCommands"
    
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Your app should be available at: http://$VMHost" -ForegroundColor Yellow
}
catch {
    Write-Host "❌ Error restarting container: $_" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Deployment finished! Test your user editing functionality." -ForegroundColor Green