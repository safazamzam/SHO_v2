# Simple Local Testing Script for Secure Configuration
Write-Host "Local Environment Testing" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Yellow

# Test 1: Configuration Loading
Write-Host "1. Testing configuration loading..." -ForegroundColor Yellow
try {
    $result = .venv/Scripts/python.exe verify_secrets.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Configuration loading: PASSED" -ForegroundColor Green
        $configTest = $true
    } else {
        Write-Host "   Configuration loading: FAILED" -ForegroundColor Red
        $configTest = $false
    }
}
catch {
    Write-Host "   Configuration loading: ERROR" -ForegroundColor Red
    $configTest = $false
}

# Test 2: Database Initialization
Write-Host "2. Testing database initialization..." -ForegroundColor Yellow
try {
    $result = .venv/Scripts/python.exe init_database_secrets.py
    if ($LASTEXITCODE -eq 0 -or $result -like "*already exists*") {
        Write-Host "   Database initialization: PASSED" -ForegroundColor Green
        $dbTest = $true
    } else {
        Write-Host "   Database initialization: FAILED" -ForegroundColor Red
        $dbTest = $false
    }
}
catch {
    Write-Host "   Database initialization: ERROR" -ForegroundColor Red
    $dbTest = $false
}

# Test 3: Docker Configuration Files
Write-Host "3. Checking Docker configuration files..." -ForegroundColor Yellow

$dockerTest = $true

if (Test-Path "docker-compose.secure.yml") {
    Write-Host "   docker-compose.secure.yml: EXISTS" -ForegroundColor Green
} else {
    Write-Host "   docker-compose.secure.yml: MISSING" -ForegroundColor Red
    $dockerTest = $false
}

if (Test-Path "Dockerfile") {
    Write-Host "   Dockerfile: EXISTS" -ForegroundColor Green
} else {
    Write-Host "   Dockerfile: MISSING" -ForegroundColor Red
    $dockerTest = $false
}

if (Test-Path "secrets") {
    Write-Host "   secrets/ directory: EXISTS" -ForegroundColor Green
    
    $secretFiles = @("mysql_root_password.txt", "mysql_user_password.txt", "secret_key.txt", "secrets_master_key.txt")
    foreach ($file in $secretFiles) {
        if (Test-Path "secrets/$file") {
            Write-Host "   secrets/${file}: EXISTS" -ForegroundColor Green
        } else {
            Write-Host "   secrets/${file}: MISSING" -ForegroundColor Red
            $dockerTest = $false
        }
    }
} else {
    Write-Host "   secrets/ directory: MISSING" -ForegroundColor Red
    $dockerTest = $false
}

# Test Summary
Write-Host ""
Write-Host "Test Results Summary:" -ForegroundColor Yellow
Write-Host "====================" -ForegroundColor Yellow

if ($configTest) {
    Write-Host "Configuration Loading: PASSED" -ForegroundColor Green
} else {
    Write-Host "Configuration Loading: FAILED" -ForegroundColor Red
}

if ($dbTest) {
    Write-Host "Database Initialization: PASSED" -ForegroundColor Green
} else {
    Write-Host "Database Initialization: FAILED" -ForegroundColor Red
}

if ($dockerTest) {
    Write-Host "Docker Configuration: PASSED" -ForegroundColor Green
} else {
    Write-Host "Docker Configuration: FAILED" -ForegroundColor Red
}

Write-Host ""
if ($configTest -and $dbTest -and $dockerTest) {
    Write-Host "ALL TESTS PASSED! Ready for Docker deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Install Docker Desktop" -ForegroundColor White
    Write-Host "2. Run: docker-compose -f docker-compose.secure.yml up --build" -ForegroundColor White
    Write-Host "3. Access application at http://localhost:5000" -ForegroundColor White
} else {
    Write-Host "Some tests failed. Please fix issues before Docker deployment." -ForegroundColor Red
}

Write-Host ""
Write-Host "Testing completed!" -ForegroundColor Cyan