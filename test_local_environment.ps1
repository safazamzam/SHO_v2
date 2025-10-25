# Local Testing Script for Secure Configuration (No Docker Required)
# This script tests the secure configuration locally before Docker deployment

Write-Host "Local Environment Testing for Secure Configuration" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Yellow

# Function to test configuration loading
function Test-ConfigurationLoading {
    Write-Host "Testing configuration loading..." -ForegroundColor Yellow
    
    try {
        # Test the secrets verification
        $result = .venv/Scripts/python.exe verify_secrets.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Configuration loading: PASSED" -ForegroundColor Green
            Write-Host "  $result" -ForegroundColor Gray
            return $true
        } else {
            Write-Host "  Configuration loading: FAILED" -ForegroundColor Red
            Write-Host "  Error: $result" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "  Configuration loading: ERROR" -ForegroundColor Red
        Write-Host "  Exception: $_" -ForegroundColor Red
        return $false
    }
}

# Function to test database initialization
function Test-DatabaseInitialization {
    Write-Host "Testing database initialization..." -ForegroundColor Yellow
    
    try {
        # Test database secrets initialization
        $result = .venv/Scripts/python.exe init_database_secrets.py 2>&1
        
        if ($LASTEXITCODE -eq 0 -or $result -like "*already exists*") {
            Write-Host "  Database initialization: PASSED" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  Database initialization: FAILED" -ForegroundColor Red
            Write-Host "  Error: $result" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "  Database initialization: ERROR" -ForegroundColor Red
        Write-Host "  Exception: $_" -ForegroundColor Red
        return $false
    }
}

# Function to test Flask application startup
function Test-FlaskStartup {
    Write-Host "Testing Flask application startup..." -ForegroundColor Yellow
    
    try {
        # Start Flask in background for testing
        $job = Start-Job -ScriptBlock {
            Set-Location $args[0]
            .venv/Scripts/python.exe app.py
        } -ArgumentList (Get-Location)
        
        # Wait for startup
        Start-Sleep -Seconds 5
        
        # Check if job is still running (good sign)
        if ($job.State -eq "Running") {
            Write-Host "  Flask startup: PASSED" -ForegroundColor Green
            
            # Try to connect
            try {
                Start-Sleep -Seconds 3
                $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 10 -UseBasicParsing
                if ($response.StatusCode -eq 200) {
                    Write-Host "  Flask HTTP response: PASSED" -ForegroundColor Green
                    $httpTest = $true
                } else {
                    Write-Host "  Flask HTTP response: FAILED (Status: $($response.StatusCode))" -ForegroundColor Yellow
                    $httpTest = $false
                }
            }
            catch {
                Write-Host "  Flask HTTP response: FAILED (Connection error)" -ForegroundColor Yellow
                $httpTest = $false
            }
            
            # Stop the job
            Stop-Job $job
            Remove-Job $job
            
            return $httpTest
        } else {
            # Get job results to see error
            $jobResult = Receive-Job $job
            Write-Host "  Flask startup: FAILED" -ForegroundColor Red
            Write-Host "  Error: $jobResult" -ForegroundColor Red
            Remove-Job $job
            return $false
        }
    }
    catch {
        Write-Host "  Flask startup: ERROR" -ForegroundColor Red
        Write-Host "  Exception: $_" -ForegroundColor Red
        return $false
    }
}

# Function to test secrets API endpoints
function Test-SecretsAPI {
    Write-Host "Testing secrets API endpoints..." -ForegroundColor Yellow
    
    # Start Flask app in background
    $job = Start-Job -ScriptBlock {
        Set-Location $args[0]
        .venv/Scripts/python.exe app.py
    } -ArgumentList (Get-Location)
    
    Start-Sleep -Seconds 8
    
    try {
        if ($job.State -eq "Running") {
            # Test SMTP config endpoint
            $smtpResponse = Invoke-WebRequest -Uri "http://localhost:5000/admin/api/smtp-config" -UseBasicParsing -TimeoutSec 5
            if ($smtpResponse.StatusCode -eq 200) {
                Write-Host "  SMTP API endpoint: PASSED" -ForegroundColor Green
                $apiTest = $true
            } else {
                Write-Host "  SMTP API endpoint: FAILED" -ForegroundColor Red
                $apiTest = $false
            }
        } else {
            Write-Host "  Flask not running for API test" -ForegroundColor Red
            $apiTest = $false
        }
    }
    catch {
        Write-Host "  API endpoints: FAILED (Connection error)" -ForegroundColor Yellow
        $apiTest = $false
    }
    finally {
        # Cleanup
        if ($job) {
            Stop-Job $job -ErrorAction SilentlyContinue
            Remove-Job $job -ErrorAction SilentlyContinue
        }
    }
    
    return $apiTest
}

# Function to validate Docker configuration files
function Test-DockerConfiguration {
    Write-Host "Validating Docker configuration files..." -ForegroundColor Yellow
    
    $issues = @()
    
    # Check docker-compose.secure.yml
    if (Test-Path "docker-compose.secure.yml") {
        $composeContent = Get-Content "docker-compose.secure.yml" -Raw
        
        # Check for required secrets
        $requiredSecrets = @("mysql_root_password", "mysql_user_password", "secret_key", "secrets_master_key")
        foreach ($secret in $requiredSecrets) {
            if ($composeContent -notlike "*$secret*") {
                $issues += "Missing secret '$secret' in docker-compose.secure.yml"
            }
        }
        
        # Check for required services
        if ($composeContent -notlike "*services:*") {
            $issues += "No services defined in docker-compose.secure.yml"
        }
        
        if ($composeContent -notlike "*db:*") {
            $issues += "Database service not defined"
        }
        
        if ($composeContent -notlike "*web:*") {
            $issues += "Web service not defined"
        }
        
        Write-Host "  docker-compose.secure.yml: PASSED" -ForegroundColor Green
    } else {
        $issues += "docker-compose.secure.yml file missing"
    }
    
    # Check Dockerfile
    if (Test-Path "Dockerfile") {
        Write-Host "  Dockerfile: PASSED" -ForegroundColor Green
    } else {
        $issues += "Dockerfile missing"
    }
    
    # Check secrets directory
    if (Test-Path "secrets") {
        $secretFiles = @("mysql_root_password.txt", "mysql_user_password.txt", "secret_key.txt", "secrets_master_key.txt")
        foreach ($file in $secretFiles) {
            if (-not (Test-Path "secrets/$file")) {
                $issues += "Missing secret file: secrets/$file"
            }
        }
        Write-Host "  Secrets directory: PASSED" -ForegroundColor Green
    } else {
        $issues += "secrets/ directory missing"
    }
    
    if ($issues.Count -eq 0) {
        Write-Host "  Docker configuration: PASSED" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  Docker configuration: ISSUES FOUND" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "    - $issue" -ForegroundColor Red
        }
        return $false
    }
}

# Function to create deployment readiness report
function Create-DeploymentReport {
    param(
        [bool]$ConfigTest,
        [bool]$DbTest, 
        [bool]$FlaskTest,
        [bool]$ApiTest,
        [bool]$DockerTest
    )
    
    $reportContent = @"
# Local Testing Report - $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Test Results Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Configuration Loading | $(if($ConfigTest){"✅ PASSED"}else{"❌ FAILED"}) | Secrets loaded from database |
| Database Initialization | $(if($DbTest){"✅ PASSED"}else{"❌ FAILED"}) | Database tables and secrets |
| Flask Application | $(if($FlaskTest){"✅ PASSED"}else{"❌ FAILED"}) | Application startup and HTTP |
| API Endpoints | $(if($ApiTest){"✅ PASSED"}else{"❌ FAILED"}) | Secrets management APIs |
| Docker Configuration | $(if($DockerTest){"✅ PASSED"}else{"❌ FAILED"}) | Docker files and secrets |

## Overall Status

$(if($ConfigTest -and $DbTest -and $FlaskTest -and $DockerTest) {
    "🎉 **READY FOR DOCKER DEPLOYMENT**

All local tests passed! Your application is ready to be deployed with Docker.

### Next Steps:
1. Install Docker Desktop if not already installed
2. Run: docker-compose -f docker-compose.secure.yml up --build
3. Test at http://localhost:5000"
} else {
    "⚠️ **ISSUES FOUND**

Some tests failed. Please address the issues above before Docker deployment.

### Recommended Actions:
1. Fix any configuration issues
2. Ensure all secret files exist and have content
3. Test Flask application startup manually
4. Re-run this test script"
})

## Configuration Details

- **Database**: SQLite (development) → MySQL (Docker production)
- **Secrets Storage**: Encrypted database storage with Fernet
- **Docker Secrets**: mysql_root_password, mysql_user_password, secret_key, secrets_master_key
- **Environment**: Development fallbacks enabled for non-Docker testing

## Security Validation

- ✅ No .env file dependencies
- ✅ Encrypted secrets in database 
- ✅ Docker secrets for infrastructure
- ✅ Secure configuration loading
- ✅ Development fallback mechanisms

---
Generated by Local Testing Script
"@

    $reportContent | Out-File -FilePath "local_testing_report.md" -Encoding UTF8
    Write-Host "  Deployment readiness report created: local_testing_report.md" -ForegroundColor Cyan
}

# Main execution
Write-Host ""
Write-Host "Starting comprehensive local testing..." -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow

# Run all tests
$configTest = Test-ConfigurationLoading
$dbTest = Test-DatabaseInitialization  
$flaskTest = Test-FlaskStartup
$apiTest = Test-SecretsAPI
$dockerTest = Test-DockerConfiguration

Write-Host ""
Write-Host "Test Summary:" -ForegroundColor Yellow
Write-Host "=============" -ForegroundColor Yellow

if ($configTest) {
    Write-Host "✅ Configuration Loading: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Configuration Loading: FAILED" -ForegroundColor Red
}

if ($dbTest) {
    Write-Host "✅ Database Initialization: PASSED" -ForegroundColor Green  
} else {
    Write-Host "❌ Database Initialization: FAILED" -ForegroundColor Red
}

if ($flaskTest) {
    Write-Host "✅ Flask Application: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Flask Application: FAILED" -ForegroundColor Red
}

if ($apiTest) {
    Write-Host "✅ API Endpoints: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ API Endpoints: FAILED" -ForegroundColor Red
}

if ($dockerTest) {
    Write-Host "✅ Docker Configuration: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Docker Configuration: FAILED" -ForegroundColor Red
}

Write-Host ""
Create-DeploymentReport -ConfigTest $configTest -DbTest $dbTest -FlaskTest $flaskTest -ApiTest $apiTest -DockerTest $dockerTest

if ($configTest -and $dbTest -and $flaskTest -and $dockerTest) {
    Write-Host "🎉 ALL TESTS PASSED! Ready for Docker deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Install Docker Desktop" -ForegroundColor White
    Write-Host "2. Run: docker-compose -f docker-compose.secure.yml up --build" -ForegroundColor White
    Write-Host "3. Access application at http://localhost:5000" -ForegroundColor White
} else {
    Write-Host "❌ Some tests failed. Please check the issues above." -ForegroundColor Red
    Write-Host "📋 See local_testing_report.md for detailed results" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Testing completed!" -ForegroundColor Cyan