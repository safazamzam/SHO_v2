# Simple Local Testing Script (Updated)
Write-Host "Local Environment Testing" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Yellow

# Test 1: Configuration Loading
Write-Host "1. Testing configuration loading..." -ForegroundColor Yellow
try {
    $result = .venv/Scripts/python.exe verify_config_clean.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Configuration loading: PASSED" -ForegroundColor Green
        $configTest = $true
    } else {
        Write-Host "   Configuration loading: FAILED" -ForegroundColor Red
        Write-Host "   Error: $result" -ForegroundColor Gray
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
    $result = .venv/Scripts/python.exe init_config_clean.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Database initialization: PASSED" -ForegroundColor Green
        $dbTest = $true
    } else {
        Write-Host "   Database initialization: FAILED" -ForegroundColor Red
        Write-Host "   Error: $result" -ForegroundColor Gray
        $dbTest = $false
    }
}
catch {
    Write-Host "   Database initialization: ERROR" -ForegroundColor Red
    $dbTest = $false
}

# Test 3: Flask App Quick Start Test
Write-Host "3. Testing Flask application startup..." -ForegroundColor Yellow
try {
    # Kill any existing Python processes
    taskkill /f /im python.exe 2>$null
    Start-Sleep -Seconds 2
    
    # Start Flask in background
    $process = Start-Process -FilePath ".venv/Scripts/python.exe" -ArgumentList "app.py" -NoNewWindow -PassThru
    
    # Wait for startup
    Start-Sleep -Seconds 5
    
    # Check if process is still running
    if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
        Write-Host "   Flask startup: PASSED" -ForegroundColor Green
        $flaskTest = $true
        
        # Try HTTP test
        try {
            Start-Sleep -Seconds 2
            $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 5 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "   HTTP response: PASSED" -ForegroundColor Green
            } else {
                Write-Host "   HTTP response: WARNING (Status: $($response.StatusCode))" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "   HTTP response: WARNING (Connection issue)" -ForegroundColor Yellow
        }
        
        # Stop Flask
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "   Flask startup: FAILED" -ForegroundColor Red
        $flaskTest = $false
    }
}
catch {
    Write-Host "   Flask startup: ERROR" -ForegroundColor Red
    $flaskTest = $false
}

# Test 4: Docker Configuration Files
Write-Host "4. Checking Docker configuration files..." -ForegroundColor Yellow

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
            Write-Host "   secrets/$file`: EXISTS" -ForegroundColor Green
        } else {
            Write-Host "   secrets/$file`: MISSING" -ForegroundColor Red
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

if ($flaskTest) {
    Write-Host "Flask Application: PASSED" -ForegroundColor Green
} else {
    Write-Host "Flask Application: FAILED" -ForegroundColor Red
}

if ($dockerTest) {
    Write-Host "Docker Configuration: PASSED" -ForegroundColor Green
} else {
    Write-Host "Docker Configuration: FAILED" -ForegroundColor Red
}

Write-Host ""
if ($configTest -and $dbTest -and $flaskTest -and $dockerTest) {
    Write-Host "ALL TESTS PASSED! Ready for Docker deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Docker Deployment Instructions:" -ForegroundColor Yellow
    Write-Host "1. Install Docker Desktop from https://docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "2. Start Docker Desktop" -ForegroundColor White
    Write-Host "3. Run: docker-compose -f docker-compose.secure.yml up --build" -ForegroundColor White
    Write-Host "4. Access application at http://localhost:5000" -ForegroundColor White
    Write-Host "5. Test admin dashboard at http://localhost:5000/admin/secrets" -ForegroundColor White
} else {
    Write-Host "Some tests failed. Please fix issues before Docker deployment." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common Fixes:" -ForegroundColor Yellow
    if (-not $configTest) {
        Write-Host "- Check database and secrets configuration" -ForegroundColor White
    }
    if (-not $dbTest) {
        Write-Host "- Ensure .env.backup file exists with proper secrets" -ForegroundColor White
    }
    if (-not $flaskTest) {
        Write-Host "- Check Flask app dependencies and configuration" -ForegroundColor White
    }
    if (-not $dockerTest) {
        Write-Host "- Ensure all Docker files and secrets exist" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "Testing completed!" -ForegroundColor Cyan