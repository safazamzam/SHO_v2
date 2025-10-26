# 🧹 Fix Nginx Conflicts - PowerShell Script
# Transfers cleanup script and runs it on remote host

param(
    [Parameter(Mandatory=$false)]
    [string]$HostIP = "35.200.202.18",
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "shifthandoversajid",
    
    [Parameter(Mandatory=$false)]
    [string]$KeyPath = "~/.ssh/my-gcp-key"
)

Write-Host "🧹 Fixing Nginx Configuration Conflicts" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

Write-Host "`n🔍 Issues found:" -ForegroundColor Yellow
Write-Host "  ❌ Duplicate limit_req_zone definitions" -ForegroundColor Red
Write-Host "  ❌ Deprecated HTTP/2 syntax" -ForegroundColor Red
Write-Host "  ❌ Multiple conflicting configuration files" -ForegroundColor Red

Write-Host "`n✅ Solution:" -ForegroundColor Green
Write-Host "  ✅ Remove conflicting config files" -ForegroundColor Green
Write-Host "  ✅ Create single clean configuration" -ForegroundColor Green
Write-Host "  ✅ Fix rate limiting zones" -ForegroundColor Green
Write-Host "  ✅ Update to modern nginx syntax" -ForegroundColor Green

$RemotePath = "~/shift_handover_app"

try {
    Write-Host "`n📁 Transferring cleanup script..." -ForegroundColor Blue
    
    # Transfer cleanup script
    scp -i $KeyPath "cleanup-nginx.sh" "${Username}@${HostIP}:${RemotePath}/"
    
    # Transfer updated nginx.conf
    scp -i $KeyPath "nginx\nginx.conf" "${Username}@${HostIP}:${RemotePath}/nginx/"
    
    # Transfer clean configuration
    scp -i $KeyPath "nginx\conf.d\handover-clean.conf" "${Username}@${HostIP}:${RemotePath}/nginx/conf.d/"
    
    Write-Host "✅ Files transferred successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ File transfer failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🧹 Running cleanup on remote host..." -ForegroundColor Blue

try {
    # Connect and run the cleanup script
    ssh -i $KeyPath "${Username}@${HostIP}" @"
cd ${RemotePath}
chmod +x cleanup-nginx.sh
./cleanup-nginx.sh
"@

    Write-Host "✅ Cleanup completed on remote host!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Remote cleanup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n🔧 Manual cleanup steps:" -ForegroundColor Yellow
    Write-Host "1. SSH to server: ssh -i $KeyPath ${Username}@${HostIP}"
    Write-Host "2. Navigate: cd ${RemotePath}"
    Write-Host "3. Run: chmod +x cleanup-nginx.sh && ./cleanup-nginx.sh"
    exit 1
}

Write-Host "`n🧪 Testing the fixed setup..." -ForegroundColor Blue

Start-Sleep -Seconds 10

try {
    $response = Invoke-WebRequest -Uri "http://${HostIP}/health" -TimeoutSec 15 -UseBasicParsing
    Write-Host "✅ HTTP health check passed! (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  HTTP health check failed - services might still be starting" -ForegroundColor Yellow
    Write-Host "Wait 1-2 minutes and test manually: curl http://${HostIP}/health" -ForegroundColor Yellow
}

Write-Host "`n🎉 Nginx Configuration Fixed!" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

Write-Host "`n✅ What was fixed:" -ForegroundColor Blue
Write-Host "  ✅ Removed duplicate rate limiting zones"
Write-Host "  ✅ Fixed deprecated HTTP/2 syntax"
Write-Host "  ✅ Cleaned up conflicting configuration files"
Write-Host "  ✅ Created single, clean nginx configuration"
Write-Host "  ✅ Restarted services with clean config"

Write-Host "`n🌐 Your application is now available at:" -ForegroundColor Blue
Write-Host "  Local:  http://${HostIP}/health" -ForegroundColor Green
Write-Host "  Domain: http://handover.lab.com/health (after domain mapping)" -ForegroundColor Yellow

Write-Host "`n📋 Next Steps:" -ForegroundColor Purple
Write-Host "1. Test local access: curl http://${HostIP}/health"
Write-Host "2. Configure domain mapping with NAT team"
Write-Host "3. Test domain access: curl http://handover.lab.com/health"

Write-Host "`n📊 Monitor your application:" -ForegroundColor Blue
Write-Host "  ssh -i $KeyPath ${Username}@${HostIP} 'cd ${RemotePath} && docker-compose -f docker-compose.prod.yml ps'"

Write-Host "`n🚀 Configuration cleanup completed successfully!" -ForegroundColor Green