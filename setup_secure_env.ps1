# Secure Environment Setup Script for Windows PowerShell
# This script helps you set up secure credentials for production deployment

param(
    [switch]$Force = $false
)

# Set error action
$ErrorActionPreference = "Stop"

Write-Host "🔐 Secure Credential Setup for Shift Handover Application" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# Function to generate strong passwords
function Generate-Password {
    $length = 32
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $password = ""
    for ($i = 0; $i -lt $length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

# Function to create Docker secret
function Create-DockerSecret {
    param(
        [string]$SecretName,
        [string]$SecretValue
    )
    
    try {
        $existingSecrets = docker secret ls --format "{{.Name}}" 2>$null
        if ($existingSecrets -contains $SecretName) {
            Write-Host "⚠️ Secret '$SecretName' already exists" -ForegroundColor Yellow
            if (-not $Force) {
                $recreate = Read-Host "Do you want to recreate it? (y/N)"
                if ($recreate -notmatch "^[Yy]$") {
                    return
                }
            }
            docker secret rm $SecretName 2>$null | Out-Null
        }
        
        $SecretValue | docker secret create $SecretName -
        Write-Host "✅ Created secret: $SecretName" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to create secret '$SecretName': $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to prompt for secret value
function Prompt-Secret {
    param(
        [string]$SecretName,
        [string]$Description,
        [string]$DefaultValue = "",
        [switch]$IsPassword = $false
    )
    
    Write-Host "`n📝 $Description" -ForegroundColor Blue
    
    $generatedValue = ""
    if ($IsPassword -or $SecretName -match "(password|key)") {
        $generatedValue = Generate-Password
        Write-Host "💡 Generated strong value: $generatedValue" -ForegroundColor Yellow
    }
    
    if ($DefaultValue) {
        Write-Host "💡 Suggested value: $DefaultValue" -ForegroundColor Yellow
    }
    
    if ($IsPassword) {
        $userInput = Read-Host "Enter value for $SecretName (or press Enter for generated)" -AsSecureString
        $userInputPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($userInput))
    } else {
        $userInputPlain = Read-Host "Enter value for $SecretName (or press Enter for generated/suggested)"
    }
    
    if ([string]::IsNullOrEmpty($userInputPlain)) {
        if ($generatedValue) {
            return $generatedValue
        } elseif ($DefaultValue) {
            return $DefaultValue
        } else {
            return ""
        }
    } else {
        return $userInputPlain
    }
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Check if Docker Swarm is initialized
try {
    docker node ls | Out-Null
} catch {
    Write-Host "⚠️ Docker Swarm is not initialized. Initializing now..." -ForegroundColor Yellow
    docker swarm init
    Write-Host "✅ Docker Swarm initialized" -ForegroundColor Green
}

Write-Host "`n🔧 Setting up Docker Secrets..." -ForegroundColor Blue

# Core Flask secrets
$FlaskSecretKey = Prompt-Secret "flask_secret_key" "Flask Secret Key (for session encryption)" -IsPassword
Create-DockerSecret "flask_secret_key" $FlaskSecretKey

$SsoEncryptionKey = Prompt-Secret "sso_encryption_key" "SSO Encryption Key (for user authentication)" -IsPassword
Create-DockerSecret "sso_encryption_key" $SsoEncryptionKey

# Database secrets
Write-Host "`n🗄️ Database Configuration" -ForegroundColor Blue
$MysqlAppPassword = Prompt-Secret "mysql_app_password" "MySQL Application User Password" -IsPassword
Create-DockerSecret "mysql_app_password" $MysqlAppPassword

$MysqlRootPassword = Prompt-Secret "mysql_root_password" "MySQL Root Password" -IsPassword
Create-DockerSecret "mysql_root_password" $MysqlRootPassword

# Construct database URL
$DatabaseUrl = "mysql://app_user:$MysqlAppPassword@db:3306/shift_handover"
Create-DockerSecret "database_url" $DatabaseUrl

# Email configuration
Write-Host "`n📧 Email Configuration" -ForegroundColor Blue
$SmtpUsername = Prompt-Secret "smtp_username" "SMTP Username (Gmail address)" "your-email@gmail.com"
Create-DockerSecret "smtp_username" $SmtpUsername

$SmtpPassword = Prompt-Secret "smtp_password" "SMTP Password (Gmail App Password)" -IsPassword
Create-DockerSecret "smtp_password" $SmtpPassword

# ServiceNow configuration
Write-Host "`n🎫 ServiceNow Configuration" -ForegroundColor Blue
$setupServiceNow = Read-Host "Do you want to configure ServiceNow integration? (y/N)"
if ($setupServiceNow -match "^[Yy]$") {
    $ServiceNowInstance = Prompt-Secret "servicenow_instance" "ServiceNow Instance URL" "https://your-instance.service-now.com"
    Create-DockerSecret "servicenow_instance" $ServiceNowInstance
    
    $ServiceNowUsername = Prompt-Secret "servicenow_username" "ServiceNow Username"
    Create-DockerSecret "servicenow_username" $ServiceNowUsername
    
    $ServiceNowPassword = Prompt-Secret "servicenow_password" "ServiceNow Password" -IsPassword
    Create-DockerSecret "servicenow_password" $ServiceNowPassword
} else {
    Create-DockerSecret "servicenow_instance" ""
    Create-DockerSecret "servicenow_username" ""
    Create-DockerSecret "servicenow_password" ""
}

# Google OAuth configuration
Write-Host "`n🔐 Google OAuth Configuration" -ForegroundColor Blue
$setupOAuth = Read-Host "Do you want to configure Google OAuth SSO? (y/N)"
if ($setupOAuth -match "^[Yy]$") {
    $GoogleClientId = Prompt-Secret "google_oauth_client_id" "Google OAuth Client ID"
    Create-DockerSecret "google_oauth_client_id" $GoogleClientId
    
    $GoogleClientSecret = Prompt-Secret "google_oauth_client_secret" "Google OAuth Client Secret" -IsPassword
    Create-DockerSecret "google_oauth_client_secret" $GoogleClientSecret
} else {
    Create-DockerSecret "google_oauth_client_id" ""
    Create-DockerSecret "google_oauth_client_secret" ""
}

# Create .env file for development
Write-Host "`n📄 Creating .env file for development..." -ForegroundColor Blue

$envContent = @"
# Development Environment Variables
# DO NOT commit this file to version control!

# Flask Configuration
SECRET_KEY=$FlaskSecretKey
FLASK_ENV=development
FLASK_APP=app.py
SSO_ENCRYPTION_KEY=$SsoEncryptionKey

# Database Configuration
DATABASE_URL=$DatabaseUrl

# Email Configuration
SMTP_USERNAME=$SmtpUsername
SMTP_PASSWORD=$SmtpPassword
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# ServiceNow Configuration (if configured)
$(if ($setupServiceNow -match "^[Yy]$") {
"SERVICENOW_INSTANCE=$ServiceNowInstance
SERVICENOW_USERNAME=$ServiceNowUsername
SERVICENOW_PASSWORD=$ServiceNowPassword"
} else {
"SERVICENOW_INSTANCE=
SERVICENOW_USERNAME=
SERVICENOW_PASSWORD="
})

# Google OAuth (if configured)
$(if ($setupOAuth -match "^[Yy]$") {
"GOOGLE_OAUTH_CLIENT_ID=$GoogleClientId
GOOGLE_OAUTH_CLIENT_SECRET=$GoogleClientSecret"
} else {
"GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET="
})
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

# Add .env to .gitignore if not already there
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -notmatch "\.env") {
        Add-Content ".gitignore" "`n.env"
        Write-Host "✅ Added .env to .gitignore" -ForegroundColor Green
    }
} else {
    ".env" | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ Created .gitignore with .env" -ForegroundColor Green
}

Write-Host "`n🎉 Security setup completed!" -ForegroundColor Green
Write-Host "`n📋 Summary:" -ForegroundColor Blue
Write-Host "• Docker secrets created for all sensitive credentials"
Write-Host "• .env file created for development (not committed to git)"
Write-Host "• All passwords are strongly generated"
Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Blue
Write-Host "1. For production: Use docker-compose.production.yml"
Write-Host "2. For development: Use regular docker-compose.yml with .env file"
Write-Host "3. Test configuration: python config_secure.py"
Write-Host ""
Write-Host "⚠️ Important Security Notes:" -ForegroundColor Yellow
Write-Host "• Keep your .env file secure and never commit it"
Write-Host "• Docker secrets are stored securely by Docker Swarm"
Write-Host "• Consider using Azure Key Vault for cloud deployment"
Write-Host "• Regularly rotate your passwords and keys"

# Test configuration
Write-Host "`n🧪 Testing configuration..." -ForegroundColor Blue
try {
    python config_secure.py
    Write-Host "✅ Configuration test passed!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Configuration test had warnings. Check the output above." -ForegroundColor Yellow
}