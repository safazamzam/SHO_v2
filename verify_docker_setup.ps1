#!/usr/bin/env powershell
# Quick Setup Verification for Docker Testing
# This script ensures all prerequisites are ready before testing

Write-Host "Docker Setup Verification" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Yellow

# Check Docker installation
Write-Host "📦 Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "  ✅ Docker found: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ Docker not found! Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host "🐙 Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "  ✅ Docker Compose found: $composeVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ Docker Compose not found! Please install Docker Compose." -ForegroundColor Red
    exit 1
}

# Check if Docker daemon is running
Write-Host "🏃 Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "  ✅ Docker daemon is running" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ Docker daemon is not running! Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check required files
Write-Host "📄 Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "docker-compose.secure.yml",
    "Dockerfile",
    "app.py",
    "config.py",
    "requirements.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file is missing!" -ForegroundColor Red
        $missingFiles = $true
    }
}

# Check secrets directory
Write-Host "🔐 Checking secrets setup..." -ForegroundColor Yellow
if (Test-Path "secrets") {
    Write-Host "  ✅ secrets/ directory exists" -ForegroundColor Green
    
    $secretFiles = @(
        "secrets/mysql_root_password.txt",
        "secrets/mysql_user_password.txt",
        "secrets/secret_key.txt", 
        "secrets/secrets_master_key.txt"
    )
    
    foreach ($secretFile in $secretFiles) {
        if (Test-Path $secretFile) {
            $content = Get-Content $secretFile -Raw
            if ($content.Trim().Length -gt 10) {
                Write-Host "  ✅ $secretFile has content" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️  $secretFile exists but content seems short" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ❌ $secretFile is missing!" -ForegroundColor Red
            $missingSecrets = $true
        }
    }
} else {
    Write-Host "  ❌ secrets/ directory is missing!" -ForegroundColor Red
    $missingSecrets = $true
}

# Check for port conflicts
Write-Host "🔌 Checking for port conflicts..." -ForegroundColor Yellow

$ports = @(5000, 3306)
foreach ($port in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "  ⚠️  Port $port is already in use" -ForegroundColor Yellow
        } else {
            Write-Host "  ✅ Port $port is available" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ✅ Port $port is available" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n📋 Summary:" -ForegroundColor Yellow
Write-Host "===========" -ForegroundColor Yellow

if ($missingFiles) {
    Write-Host "❌ Some required files are missing!" -ForegroundColor Red
    exit 1
}

if ($missingSecrets) {
    Write-Host "❌ Some secret files are missing!" -ForegroundColor Red
    Write-Host "Run this to create missing secrets:" -ForegroundColor Yellow
    Write-Host "   .venv/Scripts/python.exe init_database_secrets.py" -ForegroundColor White
    exit 1
}

Write-Host "✅ All prerequisites are ready!" -ForegroundColor Green
Write-Host "🚀 You can now run: .\test_docker_local.ps1" -ForegroundColor Cyan