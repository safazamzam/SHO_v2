# 🚀 Quick Start Domain Setup for Windows
# Shift Handover App Domain Configuration

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain,
    
    [Parameter(Mandatory=$false)]
    [string]$Email,
    
    [switch]$SkipSSL,
    
    [switch]$Help
)

# Colors for Windows PowerShell
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$Purple = [System.ConsoleColor]::Magenta
$Default = [System.ConsoleColor]::White

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Write-Header {
    param([string]$Message)
    Write-Host "[SETUP] $Message" -ForegroundColor $Purple
}

if ($Help) {
    Write-Host "🌐 Domain Setup for Shift Handover App" -ForegroundColor $Purple
    Write-Host "======================================="
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\quick-domain-setup.ps1 -Domain handover.yourdomain.com -Email admin@yourdomain.com"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Domain    Your domain name (e.g., handover.yourdomain.com)"
    Write-Host "  -Email     Your email for SSL certificate"
    Write-Host "  -SkipSSL   Skip SSL certificate setup"
    Write-Host "  -Help      Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\quick-domain-setup.ps1 -Domain shift.mycompany.com -Email it@mycompany.com"
    Write-Host "  .\quick-domain-setup.ps1 -Domain handover.example.com -Email admin@example.com -SkipSSL"
    exit 0
}

Write-Host "🌐 Quick Domain Setup for Shift Handover App" -ForegroundColor $Purple
Write-Host "============================================="

# Check if Docker is available
try {
    docker --version | Out-Null
    Write-Success "Docker is available"
} catch {
    Write-Error-Custom "Docker is not available. Please install Docker Desktop for Windows."
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
    Write-Success "Docker Compose is available"
} catch {
    Write-Error-Custom "Docker Compose is not available. Please install Docker Desktop for Windows."
    exit 1
}

# Get domain name if not provided
if (-not $Domain) {
    $Domain = Read-Host "Enter your domain name (e.g., handover.yourdomain.com)"
    if (-not $Domain) {
        Write-Error-Custom "Domain name is required!"
        exit 1
    }
}

# Get email if not provided
if (-not $Email) {
    $Email = Read-Host "Enter your email for SSL certificate"
    if (-not $Email) {
        Write-Error-Custom "Email is required!"
        exit 1
    }
}

Write-Header "Setting up domain: $Domain"
Write-Status "Contact email: $Email"

# Step 1: Create .env.domain file
Write-Status "Creating domain configuration..."
$envContent = @"
DOMAIN_NAME=$Domain
EMAIL=$Email
FLASK_ENV=production
FLASK_DEBUG=0
SSL_ENABLED=true
HTTP_PORT=80
HTTPS_PORT=443
"@

$envContent | Out-File -FilePath ".env.domain" -Encoding utf8
Write-Success "Created .env.domain configuration"

# Step 2: Update nginx configuration
Write-Status "Updating nginx configuration..."
if (Test-Path "nginx\conf.d\app.conf") {
    $nginxConfig = Get-Content "nginx\conf.d\app.conf" -Raw
    $nginxConfig = $nginxConfig -replace "your-domain\.com", $Domain
    $nginxConfig | Out-File -FilePath "nginx\conf.d\app.conf" -Encoding utf8
    Write-Success "Updated nginx configuration"
} else {
    Write-Warning "nginx configuration not found at nginx\conf.d\app.conf"
}

# Step 3: Stop existing services
Write-Status "Stopping existing services..."
try {
    docker-compose down 2>$null
    docker-compose -f docker-compose.prod.yml down 2>$null
} catch {
    # Ignore errors if services weren't running
}

# Step 4: Create necessary directories
Write-Status "Creating SSL directories..."
New-Item -ItemType Directory -Force -Path "certbot_conf" | Out-Null
New-Item -ItemType Directory -Force -Path "certbot_www" | Out-Null
New-Item -ItemType Directory -Force -Path "nginx\ssl" | Out-Null

# Step 5: Start nginx for domain validation
Write-Status "Starting nginx for domain validation..."
docker-compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to start
Start-Sleep -Seconds 5

# Step 6: DNS Check
Write-Status "Checking DNS configuration..."
try {
    $dnsResult = Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop
    $ipAddress = $dnsResult.IPAddress
    Write-Success "DNS resolved: $Domain -> $ipAddress"
    
    # Check if it points to this server (rough check)
    if ($ipAddress -match "35\.200\.202\.18") {
        Write-Success "DNS appears to point to your server!"
    } else {
        Write-Warning "DNS points to $ipAddress - make sure this is correct"
    }
} catch {
    Write-Warning "Could not resolve DNS for $Domain"
    Write-Status "Make sure you have created an A record pointing to your server IP"
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Step 7: SSL Certificate Setup (if not skipped)
if (-not $SkipSSL) {
    Write-Status "Obtaining SSL certificate..."
    
    try {
        docker run --rm `
            -v "${PWD}\certbot_conf:/etc/letsencrypt" `
            -v "${PWD}\certbot_www:/var/www/certbot" `
            certbot/certbot certonly `
            --webroot `
            --webroot-path=/var/www/certbot `
            --email $Email `
            --agree-tos `
            --no-eff-email `
            --non-interactive `
            -d $Domain
        
        if (Test-Path "certbot_conf\live\$Domain\fullchain.pem") {
            Write-Success "SSL certificate obtained successfully!"
        } else {
            Write-Warning "SSL certificate setup had issues, but continuing..."
        }
    } catch {
        Write-Warning "SSL certificate setup failed: $($_.Exception.Message)"
        Write-Status "You can set up SSL later with: docker run certbot/certbot ..."
    }
} else {
    Write-Status "Skipping SSL certificate setup as requested"
}

# Step 8: Deploy application
Write-Status "Deploying application with domain configuration..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services
Start-Sleep -Seconds 10

# Step 9: Health checks
Write-Status "Running health checks..."

# Check services
$services = docker-compose -f docker-compose.prod.yml ps --services
foreach ($service in $services) {
    $status = docker-compose -f docker-compose.prod.yml ps $service
    if ($status -match "Up") {
        Write-Success "Service $service is running"
    } else {
        Write-Warning "Service $service might have issues"
    }
}

# Test HTTP access
try {
    $response = Invoke-WebRequest -Uri "http://$Domain" -TimeoutSec 10 -UseBasicParsing
    Write-Success "HTTP access working (Status: $($response.StatusCode))"
} catch {
    Write-Warning "HTTP access test failed - this might be normal during startup"
}

# Test HTTPS access (if SSL was set up)
if (-not $SkipSSL -and (Test-Path "certbot_conf\live\$Domain\fullchain.pem")) {
    try {
        $response = Invoke-WebRequest -Uri "https://$Domain" -TimeoutSec 10 -UseBasicParsing
        Write-Success "HTTPS access working (Status: $($response.StatusCode))"
    } catch {
        Write-Warning "HTTPS access test failed - certificate might need more time to propagate"
    }
}

# Final results
Write-Host ""
Write-Success "🎉 Domain Setup Complete!"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $Green
Write-Host "🌐 Your application is now available at:" -ForegroundColor $Blue

if (-not $SkipSSL -and (Test-Path "certbot_conf\live\$Domain\fullchain.pem")) {
    Write-Host "   Primary:  https://$Domain" -ForegroundColor $Green
    Write-Host "   Login:    https://$Domain/login" -ForegroundColor $Green
    Write-Host "   Fallback: http://$Domain (redirects to HTTPS)" -ForegroundColor $Yellow
} else {
    Write-Host "   Primary: http://$Domain" -ForegroundColor $Yellow
    Write-Host "   Login:   http://$Domain/login" -ForegroundColor $Yellow
}

Write-Host ""
Write-Host "📊 Monitoring:" -ForegroundColor $Blue
Write-Host "   Check status:  docker-compose -f docker-compose.prod.yml ps"
Write-Host "   View logs:     docker-compose -f docker-compose.prod.yml logs -f"
Write-Host "   Restart:       docker-compose -f docker-compose.prod.yml restart"
Write-Host ""

if ($SkipSSL) {
    Write-Host "🔒 SSL Setup (recommended for production):" -ForegroundColor $Yellow
    Write-Host "   Run this script again without -SkipSSL to enable HTTPS"
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $Green
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor $Purple
Write-Host "1. Test your application by visiting the URLs above"
Write-Host "2. Update any bookmarks from http://35.200.202.18:5000"
Write-Host "3. Monitor the application logs for any issues"
Write-Host "4. Set up regular backups and monitoring"

Write-Success "Setup completed successfully! 🚀"