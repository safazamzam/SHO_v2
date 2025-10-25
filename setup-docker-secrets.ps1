# Setup Docker Secrets for Shift Handover App (PowerShell)
# Run this script to create all required Docker secrets

Write-Host "Setting up Docker Secrets for Shift Handover App" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

function Create-DockerSecret {
    param(
        [string]$Name,
        [string]$Description,
        [string]$Value = $null
    )
    
    if (-not $Value) {
        $Value = Read-Host -Prompt "Enter $Description" -AsSecureString
        $Value = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Value))
    }
    
    try {
        $Value | docker secret create $Name - 2>$null
        Write-Host "Created secret: $Name" -ForegroundColor Green
    }
    catch {
        Write-Host "Secret $Name already exists or failed to create" -ForegroundColor Yellow
    }
}

# Database secrets
Write-Host "`nDatabase Secrets" -ForegroundColor Blue
Create-DockerSecret "shift_handover_mysql_password" "MySQL app user password"
Create-DockerSecret "shift_handover_mysql_root_password" "MySQL root password"

# Database URL construction
$dbHost = Read-Host -Prompt "Enter database host (default: db)"
if (-not $dbHost) { $dbHost = "db" }

$dbName = Read-Host -Prompt "Enter database name (default: shift_handover)"
if (-not $dbName) { $dbName = "shift_handover" }

$dbUser = Read-Host -Prompt "Enter database username (default: app_user)"
if (-not $dbUser) { $dbUser = "app_user" }

$mysqlPass = Read-Host -Prompt "Re-enter MySQL app user password for DATABASE_URL" -AsSecureString
$mysqlPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPass))

$databaseUrl = "mysql+pymysql://$dbUser`:$mysqlPassPlain@$dbHost`:3306/$dbName"
Create-DockerSecret "shift_handover_database_url" "Database connection URL" $databaseUrl

# Application secrets
Write-Host "`nApplication Secrets" -ForegroundColor Blue
$secretsKey = "tSo-GG44Oa9MGWQmXv470mdCPxMRwhuejU87skv22ZQ="
Create-DockerSecret "shift_handover_secrets_master_key" "Secrets master key" $secretsKey

Write-Host "`nAll secrets created successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Deploy with: docker-compose -f docker-compose.production-secrets.yml up -d"
Write-Host "2. Check logs: docker-compose -f docker-compose.production-secrets.yml logs"
Write-Host "3. Access app: http://localhost:5000"
Write-Host "`nAccess secrets dashboard:" -ForegroundColor Cyan
Write-Host "- URL: http://localhost:5000/admin/secrets/"
Write-Host "- Login: admin / admin123"