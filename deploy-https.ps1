# PowerShell HTTPS Deployment Script for Windows Server

param(
    [Parameter(Mandatory=$true)]
    [string]$DomainName,
    
    [Parameter(Mandatory=$true)]
    [string]$Email,
    
    [string]$AppPath = "C:\shift-handover"
)

Write-Host "🚀 HTTPS Deployment Setup for Shift Handover Application" -ForegroundColor Green
Write-Host "=========================================================="

# Check if Docker Desktop is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Desktop is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "Download from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if Docker is running
try {
    docker version | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Setting up for domain: $DomainName" -ForegroundColor Cyan

# Create application directory
if (-not (Test-Path $AppPath)) {
    New-Item -ItemType Directory -Path $AppPath -Force
    Write-Host "📁 Created application directory: $AppPath" -ForegroundColor Green
}

Set-Location $AppPath

# Create environment file
Write-Host "⚙️ Creating environment configuration..." -ForegroundColor Yellow

$secretKey = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
$masterKey = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

$envContent = @"
FLASK_ENV=production
SECRET_KEY=$secretKey
DOMAIN_NAME=$DomainName
CERTBOT_EMAIL=$Email
USE_LETSENCRYPT=true
USE_GUNICORN=true
DATABASE_URI=sqlite:///instance/shift_handover.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SERVICENOW_ENABLED=false
SECRETS_MASTER_KEY=$masterKey
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
"@

$envContent | Out-File -FilePath ".env.https" -Encoding UTF8

# Create nginx configuration with domain
Write-Host "🌐 Creating Nginx configuration..." -ForegroundColor Yellow

if (-not (Test-Path "nginx\conf.d")) {
    New-Item -ItemType Directory -Path "nginx\conf.d" -Force
}

# Copy and update nginx config
$nginxConfig = Get-Content "nginx\conf.d\app.conf" -Raw
$nginxConfig = $nginxConfig -replace '\$\{DOMAIN_NAME\}', $DomainName
$nginxConfig | Out-File -FilePath "nginx\conf.d\app.conf" -Encoding UTF8

# Create directories for Let's Encrypt
if (-not (Test-Path "certbot\conf")) {
    New-Item -ItemType Directory -Path "certbot\conf" -Force
}
if (-not (Test-Path "certbot\www")) {
    New-Item -ItemType Directory -Path "certbot\www" -Force
}

Write-Host "🔐 Starting HTTPS setup..." -ForegroundColor Cyan

# Build and start services
Write-Host "🏗️ Building and starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.https.yml up -d nginx

# Wait for nginx to start
Start-Sleep -Seconds 10

# Get initial certificate
Write-Host "📜 Requesting SSL certificate from Let's Encrypt..." -ForegroundColor Yellow
docker-compose -f docker-compose.https.yml run --rm certbot `
    certonly --webroot --webroot-path=/var/www/certbot `
    --email $Email --agree-tos --no-eff-email `
    -d $DomainName

# Restart services with SSL
Write-Host "🔄 Restarting services with SSL..." -ForegroundColor Yellow
docker-compose -f docker-compose.https.yml down
docker-compose -f docker-compose.https.yml up -d

# Create certificate renewal task
Write-Host "⚡ Setting up automatic certificate renewal..." -ForegroundColor Yellow

$taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command `"Set-Location '$AppPath'; docker-compose -f docker-compose.https.yml run --rm certbot renew --quiet; docker-compose -f docker-compose.https.yml exec nginx nginx -s reload`""
$taskTrigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "SSL Certificate Renewal" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Force

Write-Host ""
Write-Host "✅ HTTPS Deployment Complete!" -ForegroundColor Green
Write-Host "==============================="
Write-Host "🌐 Your application is now available at: https://$DomainName" -ForegroundColor Cyan
Write-Host "🔒 SSL certificate auto-renewal is configured" -ForegroundColor Green
Write-Host "📊 Check logs with: docker-compose -f docker-compose.https.yml logs" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Important Notes:" -ForegroundColor Yellow
Write-Host "1. Make sure your domain DNS points to this server's IP"
Write-Host "2. Update your .env.https file with proper SMTP/database credentials"
Write-Host "3. Restart services after config changes: docker-compose -f docker-compose.https.yml restart"
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "- View logs: docker-compose logs -f"
Write-Host "- Restart: docker-compose restart"
Write-Host "- Update app: git pull && docker-compose up --build -d"