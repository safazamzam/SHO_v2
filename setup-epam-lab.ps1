# 🏢 EPAM Lab Domain Setup Script
# Configures handover.lab.epam.com for Shift Handover App

param(
    [Parameter(Mandatory=$false)]
    [string]$Email = "admin@epam.com",
    
    [switch]$SkipSSL,
    [switch]$TestMode,
    [switch]$Help
)

# Colors for output
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$Purple = [System.ConsoleColor]::Magenta

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
    Write-Host "[EPAM-SETUP] $Message" -ForegroundColor $Purple
}

if ($Help) {
    Write-Host "🏢 EPAM Lab Domain Setup for Shift Handover App" -ForegroundColor $Purple
    Write-Host "==============================================="
    Write-Host ""
    Write-Host "This script configures handover.lab.epam.com domain access"
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\setup-epam-lab.ps1 -Email admin@epam.com"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Email     Your EPAM email for SSL certificate (default: admin@epam.com)"
    Write-Host "  -SkipSSL   Skip SSL certificate setup (HTTP only)"
    Write-Host "  -TestMode  Test configuration without applying changes"
    Write-Host "  -Help      Show this help message"
    Write-Host ""
    Write-Host "Prerequisites:"
    Write-Host "  1. NAT configured to forward traffic to 35.200.202.18"
    Write-Host "  2. DNS handover.lab.epam.com pointing to NAT gateway"
    Write-Host "  3. Ports 80 and 443 open in firewall"
    exit 0
}

Write-Host "🏢 EPAM Lab Domain Setup" -ForegroundColor $Purple
Write-Host "========================"
Write-Host "Domain: handover.lab.epam.com" -ForegroundColor $Green
Write-Host "Email:  $Email" -ForegroundColor $Blue

# Configuration
$Domain = "handover.lab.epam.com"

# Check prerequisites
Write-Status "Checking prerequisites..."

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Success "Docker is available: $dockerVersion"
} catch {
    Write-Error-Custom "Docker is not available. Please install Docker Desktop."
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose is available: $composeVersion"
} catch {
    Write-Error-Custom "Docker Compose is not available."
    exit 1
}

if ($TestMode) {
    Write-Status "Running in test mode - no changes will be applied"
}

# Step 1: Create EPAM Lab environment configuration
Write-Header "Creating EPAM Lab configuration..."

if (-not $TestMode) {
    Copy-Item ".env.epam-lab" ".env.domain" -Force
    
    # Update email in configuration
    $envContent = Get-Content ".env.domain" -Raw
    $envContent = $envContent -replace "your-email@epam.com", $Email
    $envContent | Out-File -FilePath ".env.domain" -Encoding utf8
    
    Write-Success "Created .env.domain with EPAM Lab settings"
}

# Step 2: Configure nginx for EPAM domain
Write-Header "Configuring nginx for handover.lab.epam.com..."

if (-not $TestMode) {
    # Backup existing configuration
    if (Test-Path "nginx\conf.d\app.conf") {
        Copy-Item "nginx\conf.d\app.conf" "nginx\conf.d\app.conf.backup" -Force
        Write-Status "Backed up existing nginx configuration"
    }
    
    # Use EPAM specific configuration
    Copy-Item "nginx\conf.d\epam-lab.conf" "nginx\conf.d\app.conf" -Force
    Write-Success "Applied EPAM Lab nginx configuration"
}

# Step 3: Create necessary directories
Write-Status "Creating required directories..."
if (-not $TestMode) {
    $directories = @("certbot_conf", "certbot_www", "nginx\ssl", "logs")
    foreach ($dir in $directories) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Write-Success "Created directory structure"
}

# Step 4: DNS and NAT verification
Write-Header "Verifying DNS and NAT configuration..."

try {
    $dnsResult = Resolve-DnsName -Name $Domain -Type A -ErrorAction Stop
    $resolvedIP = $dnsResult.IPAddress
    Write-Success "DNS resolved: $Domain -> $resolvedIP"
    
    # Note about NAT
    Write-Status "Make sure your NAT gateway forwards traffic from $resolvedIP to 35.200.202.18"
} catch {
    Write-Warning "Could not resolve DNS for $Domain"
    Write-Status "Please ensure:"
    Write-Host "  1. DNS record exists for handover.lab.epam.com" -ForegroundColor $Yellow
    Write-Host "  2. NAT is configured to forward to 35.200.202.18" -ForegroundColor $Yellow
    
    if (-not $TestMode) {
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y") {
            exit 1
        }
    }
}

# Step 5: Stop existing services
Write-Status "Stopping existing services..."
if (-not $TestMode) {
    try {
        docker-compose down 2>$null
        docker-compose -f docker-compose.prod.yml down 2>$null
        Write-Success "Stopped existing services"
    } catch {
        Write-Status "No existing services to stop"
    }
}

# Step 6: Start services for domain validation
Write-Header "Starting services for EPAM Lab domain..."
if (-not $TestMode) {
    # Start with HTTP first for certificate validation
    docker-compose -f docker-compose.prod.yml up -d
    
    Start-Sleep -Seconds 10
    
    # Check if services are running
    $services = docker-compose -f docker-compose.prod.yml ps --services
    $allRunning = $true
    
    foreach ($service in $services) {
        $status = docker-compose -f docker-compose.prod.yml ps $service
        if ($status -match "Up") {
            Write-Success "Service $service is running"
        } else {
            Write-Warning "Service $service has issues"
            $allRunning = $false
        }
    }
    
    if (-not $allRunning) {
        Write-Warning "Some services have issues. Check logs:"
        Write-Host "docker-compose -f docker-compose.prod.yml logs" -ForegroundColor $Yellow
    }
}

# Step 7: SSL Certificate setup (if not skipped)
if (-not $SkipSSL) {
    Write-Header "Setting up SSL certificate for handover.lab.epam.com..."
    
    if (-not $TestMode) {
        try {
            # Test HTTP access first
            Write-Status "Testing HTTP access to validate domain..."
            Start-Sleep -Seconds 5
            
            # Get SSL certificate
            Write-Status "Obtaining SSL certificate from Let's Encrypt..."
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
                
                # Restart services with SSL
                docker-compose -f docker-compose.prod.yml restart
                Start-Sleep -Seconds 10
            } else {
                Write-Warning "SSL certificate setup had issues"
            }
        } catch {
            Write-Warning "SSL setup failed: $($_.Exception.Message)"
            Write-Status "Continuing with HTTP-only setup"
        }
    }
} else {
    Write-Status "Skipping SSL setup as requested"
}

# Step 8: Health checks and testing
Write-Header "Running health checks..."

if (-not $TestMode) {
    # Test HTTP access
    try {
        Write-Status "Testing HTTP access..."
        $httpResponse = Invoke-WebRequest -Uri "http://$Domain/health" -TimeoutSec 15 -UseBasicParsing
        Write-Success "HTTP health check passed (Status: $($httpResponse.StatusCode))"
    } catch {
        Write-Warning "HTTP health check failed - this might be normal if NAT isn't configured yet"
    }
    
    # Test HTTPS access (if SSL was set up)
    if (-not $SkipSSL -and (Test-Path "certbot_conf\live\$Domain\fullchain.pem")) {
        try {
            Write-Status "Testing HTTPS access..."
            $httpsResponse = Invoke-WebRequest -Uri "https://$Domain/health" -TimeoutSec 15 -UseBasicParsing
            Write-Success "HTTPS health check passed (Status: $($httpsResponse.StatusCode))"
        } catch {
            Write-Warning "HTTPS health check failed - certificate might need time to propagate"
        }
    }
}

# Step 9: Create monitoring and maintenance scripts
Write-Header "Creating monitoring scripts..."

if (-not $TestMode) {
    # Create log monitoring script
    $logScript = @'
# EPAM Lab - Log Monitoring Script
Write-Host "🏢 EPAM Lab Handover App - Log Monitor" -ForegroundColor Green
Write-Host "======================================"

Write-Host "`n📊 Service Status:" -ForegroundColor Blue
docker-compose -f docker-compose.prod.yml ps

Write-Host "`n📋 Recent Application Logs:" -ForegroundColor Blue
docker-compose -f docker-compose.prod.yml logs --tail=50 web

Write-Host "`n🌐 Recent Nginx Logs:" -ForegroundColor Blue
docker-compose -f docker-compose.prod.yml logs --tail=20 nginx

Write-Host "`n🔍 Quick Health Check:" -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "https://handover.lab.epam.com/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Application is healthy (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Application health check failed" -ForegroundColor Red
}
'@
    
    $logScript | Out-File -FilePath "monitor-epam-lab.ps1" -Encoding utf8
    Write-Success "Created monitoring script: monitor-epam-lab.ps1"
}

# Final results
Write-Host ""
Write-Success "🎉 EPAM Lab Domain Setup Complete!"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $Green

Write-Host "🌐 EPAM Lab Application URLs:" -ForegroundColor $Blue
if (-not $SkipSSL -and (Test-Path "certbot_conf\live\$Domain\fullchain.pem")) {
    Write-Host "   Primary:  https://handover.lab.epam.com" -ForegroundColor $Green
    Write-Host "   Login:    https://handover.lab.epam.com/login" -ForegroundColor $Green
    Write-Host "   Health:   https://handover.lab.epam.com/health" -ForegroundColor $Green
} else {
    Write-Host "   Primary: http://handover.lab.epam.com" -ForegroundColor $Yellow
    Write-Host "   Login:   http://handover.lab.epam.com/login" -ForegroundColor $Yellow
    Write-Host "   Health:  http://handover.lab.epam.com/health" -ForegroundColor $Yellow
}

Write-Host ""
Write-Host "🔧 Management Commands:" -ForegroundColor $Blue
Write-Host "   Monitor:       .\monitor-epam-lab.ps1"
Write-Host "   Check status:  docker-compose -f docker-compose.prod.yml ps"
Write-Host "   View logs:     docker-compose -f docker-compose.prod.yml logs -f"
Write-Host "   Restart:       docker-compose -f docker-compose.prod.yml restart"

Write-Host ""
Write-Host "🏢 EPAM Lab Configuration:" -ForegroundColor $Purple
Write-Host "   Domain:        handover.lab.epam.com"
Write-Host "   Environment:   Production (EPAM Lab)"
Write-Host "   SSL:           $(if (-not $SkipSSL -and (Test-Path "certbot_conf\live\$Domain\fullchain.pem")) { "Enabled" } else { "Disabled" })"
Write-Host "   Rate Limiting: Enabled"
Write-Host "   Access Logs:   Enabled"

Write-Host ""
Write-Host "📋 NAT Configuration Requirements:" -ForegroundColor $Yellow
Write-Host "   External Domain: handover.lab.epam.com"
Write-Host "   Target Server:   35.200.202.18"
Write-Host "   Required Ports:  80 (HTTP), 443 (HTTPS)"
Write-Host "   Health Check:    /health endpoint"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor $Green

if ($TestMode) {
    Write-Host ""
    Write-Warning "This was a test run. To apply changes, run without -TestMode"
} else {
    Write-Host ""
    Write-Success "Setup completed successfully! 🚀"
    Write-Host "Your Shift Handover App is now available at handover.lab.epam.com"
}