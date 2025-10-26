# 🔧 Fix Nginx Setup - Transfer Files and Run Setup
# This script transfers the necessary files to your Linux host and runs the setup

param(
    [Parameter(Mandatory=$false)]
    [string]$HostIP = "35.200.202.18",
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "shifthandoversajid",
    
    [Parameter(Mandatory=$false)]
    [string]$KeyPath = "~/.ssh/my-gcp-key"
)

Write-Host "🔧 Fixing Nginx Setup for handover.lab.com" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

$RemotePath = "~/shift_handover_app"

Write-Host "`n📁 Transferring nginx configuration files..." -ForegroundColor Blue

try {
    # Transfer nginx.conf
    Write-Host "Transferring nginx/nginx.conf..." -ForegroundColor Yellow
    scp -i $KeyPath "nginx\nginx.conf" "${Username}@${HostIP}:${RemotePath}/nginx/"
    
    # Transfer fix script
    Write-Host "Transferring setup script..." -ForegroundColor Yellow
    scp -i $KeyPath "fix-nginx-setup.sh" "${Username}@${HostIP}:${RemotePath}/"
    
    # Transfer .env files
    Write-Host "Transferring environment configurations..." -ForegroundColor Yellow
    scp -i $KeyPath ".env.http-only" "${Username}@${HostIP}:${RemotePath}/"
    
    Write-Host "✅ Files transferred successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ File transfer failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 Running setup on remote host..." -ForegroundColor Blue

try {
    # Connect and run the fix script
    ssh -i $KeyPath "${Username}@${HostIP}" @"
cd ${RemotePath}
chmod +x fix-nginx-setup.sh
./fix-nginx-setup.sh
"@

    Write-Host "✅ Setup completed on remote host!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Remote setup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n🔧 Manual steps:" -ForegroundColor Yellow
    Write-Host "1. SSH to your server: ssh -i $KeyPath ${Username}@${HostIP}"
    Write-Host "2. Navigate to app directory: cd ${RemotePath}"
    Write-Host "3. Run: chmod +x fix-nginx-setup.sh && ./fix-nginx-setup.sh"
}

Write-Host "`n🧪 Testing the setup..." -ForegroundColor Blue

try {
    # Test if the service is accessible
    $response = Invoke-WebRequest -Uri "http://${HostIP}/health" -TimeoutSec 10 -UseBasicParsing
    Write-Host "✅ HTTP health check passed (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⚠️  HTTP health check failed - this is normal if still starting up" -ForegroundColor Yellow
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Purple
Write-Host "1. Wait 1-2 minutes for services to fully start"
Write-Host "2. Test local access: curl http://${HostIP}/health"
Write-Host "3. Configure domain mapping: handover.lab.com → ${HostIP}"
Write-Host "4. Test domain access: curl http://handover.lab.com/health"
Write-Host "`n📊 Monitor the setup:"
Write-Host "   ssh -i $KeyPath ${Username}@${HostIP} 'cd ${RemotePath} && ./monitor.sh'"

Write-Host "`n🎉 Setup process completed!" -ForegroundColor Green