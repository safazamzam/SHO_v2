# Production Configuration Management Guide

## 🏭 Best Practices for Production Credentials & Configuration

### ❌ **What NOT to do in Production:**
- Store credentials in `.env` files
- Commit sensitive data to Git repositories
- Use hardcoded secrets in application code
- Share credentials through insecure channels

### ✅ **Recommended Production Approaches:**

## 1. 🔐 Azure Key Vault (Recommended for Azure)

### Benefits:
- Centralized secret management
- Automatic rotation capabilities
- Access policies and audit logging
- Integration with Azure services
- Hardware Security Module (HSM) backing

### Implementation:

#### A. Create Azure Key Vault
```bash
# Create resource group
az group create --name rg-shift-handover-prod --location eastus

# Create Key Vault
az keyvault create --name kv-shift-handover-prod \
    --resource-group rg-shift-handover-prod \
    --location eastus \
    --sku standard
```

#### B. Add Secrets to Key Vault
```bash
# Add database connection string
az keyvault secret set --vault-name kv-shift-handover-prod \
    --name "DATABASE-URL" \
    --value "postgresql://user:pass@server:5432/db"

# Add SSO secrets
az keyvault secret set --vault-name kv-shift-handover-prod \
    --name "GOOGLE-OAUTH-CLIENT-ID" \
    --value "your-google-client-id"

az keyvault secret set --vault-name kv-shift-handover-prod \
    --name "GOOGLE-OAUTH-CLIENT-SECRET" \
    --value "your-google-client-secret"

# Add encryption key
az keyvault secret set --vault-name kv-shift-handover-prod \
    --name "SSO-ENCRYPTION-KEY" \
    --value "your-fernet-encryption-key"

# Add Flask secret key
az keyvault secret set --vault-name kv-shift-handover-prod \
    --name "FLASK-SECRET-KEY" \
    --value "your-flask-secret-key"
```

#### C. Configure Application to Use Key Vault
```python
# config_production.py
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class ProductionConfig:
    def __init__(self):
        # Initialize Key Vault client
        credential = DefaultAzureCredential()
        vault_url = "https://kv-shift-handover-prod.vault.azure.net/"
        self.client = SecretClient(vault_url=vault_url, credential=credential)
    
    def get_secret(self, secret_name):
        """Retrieve secret from Azure Key Vault"""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {e}")
            return None
    
    @property
    def DATABASE_URL(self):
        return self.get_secret("DATABASE-URL")
    
    @property
    def GOOGLE_OAUTH_CLIENT_ID(self):
        return self.get_secret("GOOGLE-OAUTH-CLIENT-ID")
    
    @property
    def GOOGLE_OAUTH_CLIENT_SECRET(self):
        return self.get_secret("GOOGLE-OAUTH-CLIENT-SECRET")
    
    @property
    def SSO_ENCRYPTION_KEY(self):
        return self.get_secret("SSO-ENCRYPTION-KEY")
    
    @property
    def FLASK_SECRET_KEY(self):
        return self.get_secret("FLASK-SECRET-KEY")
```

## 2. 🌐 Azure App Service Application Settings

### Benefits:
- Native integration with Azure App Service
- Environment-specific configuration
- Secure storage (encrypted at rest)
- Easy management through Azure Portal or CLI

### Implementation:

#### A. Set Application Settings via Azure CLI
```bash
# Set database configuration
az webapp config appsettings set \
    --resource-group rg-shift-handover-prod \
    --name shift-handover-app-prod \
    --settings \
    DATABASE_URL="postgresql://user:pass@server:5432/db" \
    FLASK_ENV="production" \
    FLASK_SECRET_KEY="your-secret-key"

# Set SSO configuration
az webapp config appsettings set \
    --resource-group rg-shift-handover-prod \
    --name shift-handover-app-prod \
    --settings \
    GOOGLE_OAUTH_CLIENT_ID="your-client-id" \
    GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret" \
    SSO_ENCRYPTION_KEY="your-encryption-key"

# Set ServiceNow configuration
az webapp config appsettings set \
    --resource-group rg-shift-handover-prod \
    --name shift-handover-app-prod \
    --settings \
    SERVICENOW_INSTANCE="your-instance.service-now.com" \
    SERVICENOW_USERNAME="service-account" \
    SERVICENOW_PASSWORD="service-password"
```

#### B. Access in Python Application
```python
# config.py - Updated for production
import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # SSO Configuration
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    SSO_ENCRYPTION_KEY = os.environ.get('SSO_ENCRYPTION_KEY')
    
    # ServiceNow Configuration
    SERVICENOW_INSTANCE = os.environ.get('SERVICENOW_INSTANCE')
    SERVICENOW_USERNAME = os.environ.get('SERVICENOW_USERNAME')
    SERVICENOW_PASSWORD = os.environ.get('SERVICENOW_PASSWORD')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # HTTPS enforcement
    PREFERRED_URL_SCHEME = 'https'
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        required_vars = [
            'FLASK_SECRET_KEY',
            'DATABASE_URL',
            'SSO_ENCRYPTION_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
```

## 3. 🔄 Azure DevOps Variable Groups

### Benefits:
- Centralized configuration for CI/CD pipelines
- Environment-specific variable groups
- Secret variables (encrypted)
- Easy integration with Azure Key Vault

### Implementation:

#### A. Create Variable Groups in Azure DevOps
```yaml
# azure-pipelines.yml
variables:
- group: 'shift-handover-prod-secrets'
- group: 'shift-handover-prod-config'

stages:
- stage: Deploy
  jobs:
  - deployment: DeployToProduction
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              appSettings: |
                -FLASK_SECRET_KEY "$(FLASK_SECRET_KEY)"
                -DATABASE_URL "$(DATABASE_URL)"
                -GOOGLE_OAUTH_CLIENT_ID "$(GOOGLE_OAUTH_CLIENT_ID)"
                -GOOGLE_OAUTH_CLIENT_SECRET "$(GOOGLE_OAUTH_CLIENT_SECRET)"
                -SSO_ENCRYPTION_KEY "$(SSO_ENCRYPTION_KEY)"
```

#### B. Link Variable Group to Key Vault
```bash
# Create variable group linked to Key Vault
az pipelines variable-group create \
    --name "shift-handover-prod-secrets" \
    --variables PLACEHOLDER=placeholder \
    --authorize true \
    --organization https://dev.azure.com/mdsajid020 \
    --project shift_handover_v2

# Link to Key Vault (via Azure DevOps UI)
# Go to Pipelines > Library > Variable groups > Link secrets from Azure Key Vault
```

## 4. 🐳 Docker Secrets (for Container Deployment)

### Benefits:
- Secure secret management in containerized environments
- Integration with orchestration platforms
- Runtime secret injection

### Implementation:

#### A. Docker Compose with Secrets
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    image: shift-handover-app:latest
    environment:
      - FLASK_SECRET_KEY_FILE=/run/secrets/flask_secret_key
      - DATABASE_URL_FILE=/run/secrets/database_url
    secrets:
      - flask_secret_key
      - database_url
      - google_oauth_client_id
      - google_oauth_client_secret
    ports:
      - "80:5000"

secrets:
  flask_secret_key:
    external: true
  database_url:
    external: true
  google_oauth_client_id:
    external: true
  google_oauth_client_secret:
    external: true
```

#### B. Application Code for Docker Secrets
```python
# utils/secrets.py
import os

def get_secret(secret_name, default=None):
    """Get secret from file or environment variable"""
    # First try to read from Docker secret file
    secret_file = os.environ.get(f'{secret_name.upper()}_FILE')
    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()
    
    # Fallback to environment variable
    return os.environ.get(secret_name.upper(), default)

# Usage in config.py
from utils.secrets import get_secret

class Config:
    SECRET_KEY = get_secret('FLASK_SECRET_KEY')
    DATABASE_URL = get_secret('DATABASE_URL')
    GOOGLE_OAUTH_CLIENT_ID = get_secret('GOOGLE_OAUTH_CLIENT_ID')
```

## 5. 🏢 HashiCorp Vault (Enterprise Solution)

### Benefits:
- Dynamic secrets
- Secret rotation
- Detailed audit logs
- Multi-cloud support

### Basic Implementation:
```python
# vault_config.py
import hvac

class VaultConfig:
    def __init__(self):
        self.client = hvac.Client(url='https://vault.company.com')
        # Authenticate using various methods (AWS IAM, Kubernetes, etc.)
        
    def get_secret(self, path):
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response['data']['data']
```

## 🚀 Recommended Production Setup

### For Azure Deployment:
1. **Primary**: Azure Key Vault + App Service Application Settings
2. **Backup**: Azure DevOps Variable Groups for CI/CD
3. **Local Development**: `.env` files (excluded from Git)

### Configuration Hierarchy:
```python
# config.py - Final production-ready version
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class ProductionConfigManager:
    def __init__(self):
        self.use_key_vault = os.environ.get('USE_KEY_VAULT', 'false').lower() == 'true'
        if self.use_key_vault:
            try:
                credential = DefaultAzureCredential()
                vault_url = os.environ.get('KEY_VAULT_URL')
                self.kv_client = SecretClient(vault_url=vault_url, credential=credential)
            except Exception as e:
                print(f"Key Vault initialization failed: {e}")
                self.use_key_vault = False
    
    def get_config_value(self, key, default=None):
        """Get configuration with fallback hierarchy"""
        # 1. Try Key Vault (if configured)
        if self.use_key_vault:
            try:
                secret = self.kv_client.get_secret(key.replace('_', '-'))
                return secret.value
            except:
                pass
        
        # 2. Try App Service Application Settings / Environment Variables
        env_value = os.environ.get(key)
        if env_value:
            return env_value
        
        # 3. Return default
        return default

# Usage
config_manager = ProductionConfigManager()

class Config:
    SECRET_KEY = config_manager.get_config_value('FLASK_SECRET_KEY')
    DATABASE_URL = config_manager.get_config_value('DATABASE_URL')
    GOOGLE_OAUTH_CLIENT_ID = config_manager.get_config_value('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = config_manager.get_config_value('GOOGLE_OAUTH_CLIENT_SECRET')
    SSO_ENCRYPTION_KEY = config_manager.get_config_value('SSO_ENCRYPTION_KEY')
```

## 🛡️ Security Best Practices

1. **Principle of Least Privilege**: Grant minimal required access
2. **Regular Rotation**: Rotate secrets regularly (automate where possible)
3. **Audit Logging**: Enable and monitor secret access logs
4. **Environment Separation**: Use separate configurations for dev/staging/prod
5. **Network Security**: Use private endpoints and VNets where possible
6. **Backup**: Ensure secrets are backed up securely
7. **Monitoring**: Set up alerts for unauthorized access attempts

## 📋 Migration Checklist

- [ ] Set up Azure Key Vault or chosen secret management solution
- [ ] Migrate all secrets from `.env` to secure storage
- [ ] Update application code to use new configuration method
- [ ] Configure CI/CD pipeline with secure variable injection
- [ ] Test secret rotation procedures
- [ ] Set up monitoring and alerting
- [ ] Document access procedures for team
- [ ] Remove `.env` files from production deployments
- [ ] Audit and verify no secrets are in Git history

This approach ensures your production deployment is secure, scalable, and follows industry best practices for credential management.