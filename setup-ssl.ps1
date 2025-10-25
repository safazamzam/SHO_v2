# SSL Certificate Setup Script for Let's Encrypt (PowerShell)
# This script helps set up SSL certificates for your domain

param(
    [string]$ConfigFile = ".env.production"
)

Write-Host "🔒 Shift Handover App - HTTPS Setup Script" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Check if .env.production exists
if (-not (Test-Path $ConfigFile)) {
    Write-Host "❌ Error: $ConfigFile file not found" -ForegroundColor Red
    Write-Host "Please copy .env.production.template to .env.production and configure your settings" -ForegroundColor Yellow
    exit 1
}

# Read environment variables from file
$envVars = @{}
Get-Content $ConfigFile | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        $envVars[$Matches[1].Trim()] = $Matches[2].Trim()
    }
}

# Validate required variables
if (-not $envVars.ContainsKey("DOMAIN_NAME") -or -not $envVars.ContainsKey("CERTBOT_EMAIL")) {
    Write-Host "❌ Error: DOMAIN_NAME and CERTBOT_EMAIL must be set in $ConfigFile" -ForegroundColor Red
    exit 1
}

$domainName = $envVars["DOMAIN_NAME"]
$certbotEmail = $envVars["CERTBOT_EMAIL"]

Write-Host "📋 Configuration:" -ForegroundColor Green
Write-Host "   Domain: $domainName"
Write-Host "   Email: $certbotEmail"
Write-Host ""

# Create necessary directories
Write-Host "📁 Creating SSL directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path ".\certbot\conf" | Out-Null
New-Item -ItemType Directory -Force -Path ".\certbot\www" | Out-Null
New-Item -ItemType Directory -Force -Path ".\nginx\ssl" | Out-Null

# Create temporary nginx config for initial certificate request
Write-Host "📝 Creating temporary nginx configuration..." -ForegroundColor Green
$tempConfig = @"
server {
    listen 80;
    server_name $domainName www.$domainName;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'Temporary server for SSL setup';
        add_header Content-Type text/plain;
    }
}
"@

$tempConfig | Out-File -FilePath ".\nginx\conf.d\temp.conf" -Encoding UTF8

# Start temporary containers for certificate generation
Write-Host "🐳 Starting temporary containers..." -ForegroundColor Green
docker-compose -f docker-compose.https.yml up -d nginx

# Wait for nginx to be ready
Write-Host "⏳ Waiting for nginx to be ready..." -ForegroundColor Green
Start-Sleep -Seconds 10

# Request SSL certificate
Write-Host "🔒 Requesting SSL certificate from Let's Encrypt..." -ForegroundColor Green
docker-compose -f docker-compose.https.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email $certbotEmail --agree-tos --no-eff-email --force-renewal -d $domainName -d "www.$domainName"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SSL certificate successfully obtained!" -ForegroundColor Green
    
    # Remove temporary config
    Remove-Item ".\nginx\conf.d\temp.conf" -ErrorAction SilentlyContinue
    
    # Replace domain placeholder in nginx config
    $httpsConfig = Get-Content ".\nginx\conf.d\https.conf" -Raw
    $httpsConfig = $httpsConfig -replace '\$\{DOMAIN_NAME\}', $domainName
    $httpsConfig | Out-File -FilePath ".\nginx\conf.d\https.conf" -Encoding UTF8
    
    Write-Host "🔄 Restarting containers with SSL configuration..." -ForegroundColor Green
    docker-compose -f docker-compose.https.yml down
    docker-compose -f docker-compose.https.yml up -d
    
    Write-Host ""
    Write-Host "🎉 SSL setup completed successfully!" -ForegroundColor Green
    Write-Host "Your application is now available at: https://$domainName" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Test your application: https://$domainName"
    Write-Host "   2. Check SSL rating: https://www.ssllabs.com/ssltest/"
    Write-Host "   3. Set up automatic certificate renewal (configure task scheduler)"
    Write-Host ""
    
    # Create renewal script
    $renewalScript = @"
# Certificate Renewal Script
docker-compose -f docker-compose.https.yml exec certbot certbot renew --quiet
if (`$LASTEXITCODE -eq 0) {
    docker-compose -f docker-compose.https.yml exec nginx nginx -s reload
}
"@
    
    $renewalScript | Out-File -FilePath ".\renew-certificates.ps1" -Encoding UTF8
    Write-Host "✅ Certificate renewal script created: renew-certificates.ps1" -ForegroundColor Green
    
} else {
    Write-Host "❌ Failed to obtain SSL certificate" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "   1. Domain DNS is pointing to your server"
    Write-Host "   2. Port 80 is accessible from the internet"
    Write-Host "   3. No firewall blocking the connection"
    exit 1
}

Write-Host "🔒 HTTPS setup complete!" -ForegroundColor Green