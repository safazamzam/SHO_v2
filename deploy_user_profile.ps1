# Deploy User Profile Updates to Production VM
Write-Host "🚀 Deploying User Profile System to Production..." -ForegroundColor Green

# Define files to upload
$filesToUpload = @(
    "routes\user_profile.py",
    "templates\user_profile.html",
    "templates\notifications.html", 
    "templates\alerts.html",
    "templates\help_support.html",
    "templates\about.html",
    "templates\account_settings.html",
    "app.py"
)

# VM connection details
$vmUser = "pysajid"
$vmHost = "35.200.202.18"
$vmPath = "~/shift_handover_app/"

Write-Host "📁 Files to deploy:" -ForegroundColor Yellow
$filesToUpload | ForEach-Object {
    Write-Host "  - $_" -ForegroundColor Cyan
}

Write-Host "`n🔗 Connecting to production VM..." -ForegroundColor Blue

Write-Host "📋 Manual deployment instructions:" -ForegroundColor Green
Write-Host "1. Use WinSCP, FileZilla, or similar to connect to $vmHost" -ForegroundColor White
Write-Host "2. Upload the following files to $vmPath" -ForegroundColor White
$filesToUpload | ForEach-Object {
    Write-Host "   - $_" -ForegroundColor Cyan
}

Write-Host "`n✅ Deployment preparation complete!" -ForegroundColor Green
Write-Host "Next: Restart the application on the VM" -ForegroundColor Yellow