#!/usr/bin/env powershell
# Local Docker Testing Script for Secure Configuration
# This script tests the Docker setup locally before production deployment

Write-Host "🧪 Starting Local Docker Testing for Secure Configuration..." -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Yellow

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        docker version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to cleanup existing containers and volumes
function Cleanup-Existing {
    Write-Host "🧹 Cleaning up existing containers and volumes..." -ForegroundColor Yellow
    
    # Stop and remove containers
    docker-compose -f docker-compose.secure.yml down --volumes --remove-orphans 2>$null
    
    # Remove any dangling containers from previous runs
    $containers = docker ps -a --filter "name=shift_handover" --format "{{.ID}}" 2>$null
    if ($containers) {
        docker rm -f $containers 2>$null
    }
    
    # Remove volumes
    docker volume rm shift_handover_app_flash_bkp_db_data 2>$null
    
    Write-Host "✅ Cleanup completed!" -ForegroundColor Green
}

# Function to verify secret files
function Test-SecretFiles {
    Write-Host "🔐 Verifying secret files..." -ForegroundColor Yellow
    
    $secretFiles = @(
        "secrets/mysql_root_password.txt",
        "secrets/mysql_user_password.txt", 
        "secrets/secret_key.txt",
        "secrets/secrets_master_key.txt"
    )
    
    $allExists = $true
    foreach ($file in $secretFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            if ($content.Trim().Length -gt 0) {
                Write-Host "  ✅ $file - OK" -ForegroundColor Green
            } else {
                Write-Host "  ❌ $file - EMPTY" -ForegroundColor Red
                $allExists = $false
            }
        } else {
            Write-Host "  ❌ $file - MISSING" -ForegroundColor Red
            $allExists = $false
        }
    }
    
    return $allExists
}

# Function to test database connection
function Test-DatabaseConnection {
    Write-Host "🗄️ Testing database connection..." -ForegroundColor Yellow
    
    # Wait for database to be ready
    $maxAttempts = 30
    $attempt = 0
    
    do {
        $attempt++
        Write-Host "  Attempt $attempt/$maxAttempts - Waiting for database..." -ForegroundColor Gray
        
        $password = Get-Content "secrets/mysql_user_password.txt" -Raw
        $password = $password.Trim()
        
        try {
            # Test connection using docker exec
            $result = docker exec shift_handover_app_flash_bkp_db_1 mysql -u user -p"$password" -e "SELECT 1;" shift_handover 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ Database connection successful!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            # Continue trying
        }
        
        Start-Sleep -Seconds 2
        
    } while ($attempt -lt $maxAttempts)
    
    Write-Host "  ❌ Database connection failed after $maxAttempts attempts" -ForegroundColor Red
    return $false
}

# Function to test Flask application
function Test-FlaskApplication {
    Write-Host "🌐 Testing Flask application..." -ForegroundColor Yellow
    
    # Wait for Flask to be ready
    $maxAttempts = 30
    $attempt = 0
    
    do {
        $attempt++
        Write-Host "  Attempt $attempt/$maxAttempts - Waiting for Flask app..." -ForegroundColor Gray
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✅ Flask application is responding!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            # Continue trying
        }
        
        Start-Sleep -Seconds 2
        
    } while ($attempt -lt $maxAttempts)
    
    Write-Host "  ❌ Flask application failed to respond after $maxAttempts attempts" -ForegroundColor Red
    return $false
}

# Function to test secrets management
function Test-SecretsManagement {
    Write-Host "🔑 Testing secrets management..." -ForegroundColor Yellow
    
    try {
        # Test secrets verification script in Docker
        $result = docker exec shift_handover_app_flash_bkp_web_1 python verify_secrets.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Secrets management working!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ Secrets verification failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "  ❌ Error testing secrets management: $_" -ForegroundColor Red
        return $false
    }
}

# Function to show container logs
function Show-ContainerLogs {
    Write-Host "📋 Container Logs:" -ForegroundColor Yellow
    Write-Host "=================" -ForegroundColor Yellow
    
    Write-Host "🗄️ Database Logs:" -ForegroundColor Cyan
    docker logs shift_handover_app_flash_bkp_db_1 --tail 20
    
    Write-Host "`n🌐 Web Application Logs:" -ForegroundColor Cyan
    docker logs shift_handover_app_flash_bkp_web_1 --tail 20
}

# Main testing flow
Write-Host "📋 Pre-flight Checks:" -ForegroundColor Yellow
Write-Host "=====================" -ForegroundColor Yellow

# Check if Docker is running
if (-not (Test-DockerRunning)) {
    Write-Host "❌ Docker is not running! Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is running" -ForegroundColor Green

# Check secret files
if (-not (Test-SecretFiles)) {
    Write-Host "❌ Secret files are missing or empty! Please run setup first." -ForegroundColor Red
    exit 1
}

# Cleanup any existing setup
Cleanup-Existing

Write-Host "`n🚀 Starting Docker Services..." -ForegroundColor Yellow
Write-Host "===============================" -ForegroundColor Yellow

# Build and start services
Write-Host "Building and starting services..." -ForegroundColor Gray
docker-compose -f docker-compose.secure.yml up --build -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Docker services!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker services started!" -ForegroundColor Green

# Wait a moment for services to initialize
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host "`n🔬 Running Tests..." -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow

# Test database connection
$dbTest = Test-DatabaseConnection

# Test Flask application  
$flaskTest = Test-FlaskApplication

# Test secrets management
$secretsTest = Test-SecretsManagement

Write-Host "`n📊 Test Results Summary:" -ForegroundColor Yellow
Write-Host "========================" -ForegroundColor Yellow

if ($dbTest) {
    Write-Host "✅ Database Connection: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Database Connection: FAILED" -ForegroundColor Red
}

if ($flaskTest) {
    Write-Host "✅ Flask Application: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Flask Application: FAILED" -ForegroundColor Red
}

if ($secretsTest) {
    Write-Host "✅ Secrets Management: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Secrets Management: FAILED" -ForegroundColor Red
}

# Show logs if any test failed
if (-not ($dbTest -and $flaskTest -and $secretsTest)) {
    Write-Host "`n🔍 Showing logs for debugging..." -ForegroundColor Yellow
    Show-ContainerLogs
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "==============" -ForegroundColor Yellow

if ($dbTest -and $flaskTest -and $secretsTest) {
    Write-Host "🎉 ALL TESTS PASSED! Your Docker setup is ready for production!" -ForegroundColor Green
    Write-Host "✅ You can access the application at: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "✅ Admin secrets dashboard: http://localhost:5000/admin/secrets" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To test manually:" -ForegroundColor Yellow
    Write-Host "  1. Open browser to http://localhost:5000" -ForegroundColor White
    Write-Host "  2. Test login functionality" -ForegroundColor White  
    Write-Host "  3. Navigate to admin/secrets to test configuration" -ForegroundColor White
    Write-Host ""
    Write-Host "To stop the test environment:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.secure.yml down --volumes" -ForegroundColor White
} else {
    Write-Host "❌ Some tests failed. Please check the logs above and fix issues before production deployment." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  1. Check secret files in secrets/ directory" -ForegroundColor White
    Write-Host "  2. Verify Docker has enough resources allocated" -ForegroundColor White
    Write-Host "  3. Check for port conflicts (5000, 3306)" -ForegroundColor White
    Write-Host ""
    Write-Host "To cleanup and retry:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.secure.yml down --volumes" -ForegroundColor White
}

Write-Host "`n🏁 Testing completed!" -ForegroundColor Cyan