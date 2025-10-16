# Azure Container Registry Setup Guide

## 🏗️ Setting Up Azure Container Registry (ACR)

### Step 1: Create Azure Container Registry

#### Option A: Using Azure CLI
```bash
# Login to Azure
az login

# Create resource group (if not exists)
az group create --name rg-shift-handover-prod --location eastus

# Create Azure Container Registry
az acr create \
  --resource-group rg-shift-handover-prod \
  --name shifthandoverregistry \
  --sku Basic \
  --admin-enabled true

# Get login server and credentials
az acr show --name shifthandoverregistry --query loginServer --output table
az acr credential show --name shifthandoverregistry
```

#### Option B: Using Azure Portal
1. Go to Azure Portal → Create a resource → Container Registry
2. Fill details:
   - **Registry name**: `shifthandoverregistry` (must be globally unique)
   - **Resource group**: `rg-shift-handover-prod`
   - **Location**: `East US`
   - **SKU**: `Basic` (or Standard for production)
3. **Admin user**: Enable
4. Create the registry

### Step 2: Configure Azure DevOps Service Connection

#### Create Azure Container Registry Service Connection
1. Go to Azure DevOps → Project Settings → Service connections
2. Click "New service connection" → "Docker Registry"
3. Select "Azure Container Registry"
4. Fill details:
   - **Connection name**: `AzureContainerRegistry`
   - **Azure subscription**: Select your subscription
   - **Azure container registry**: Select `shifthandoverregistry`
   - **Service connection name**: `ACRConnection`
5. Save the connection

### Step 3: Update Variable Groups

#### Update `pipeline-config` Variable Group:
```yaml
# Remove Docker Hub variables, add ACR variables
acrName: "shifthandoverregistry"
acrLoginServer: "shifthandoverregistry.azurecr.io"
dockerRepository: "shift-handover-app"
pythonVersion: "3.11"
vmProjectPath: "/opt/shift-handover-app"
```

#### Update `production-secrets` Variable Group:
```yaml
# Remove DOCKER_HUB_USERNAME, keep others
SECRET_KEY: "your-super-secret-flask-key"  # [Secret]
DATABASE_URI: "sqlite:///shift_handover.db"
SMTP_USERNAME: "your-email@gmail.com"
SMTP_PASSWORD: "your-app-password"  # [Secret]
SERVICENOW_INSTANCE: "your-instance.service-now.com"
SERVICENOW_USERNAME: "service-account"
SERVICENOW_PASSWORD: "service-password"  # [Secret]
SSO_ENCRYPTION_KEY: "your-fernet-key"  # [Secret]
GOOGLE_OAUTH_CLIENT_ID: "your-google-client-id"
GOOGLE_OAUTH_CLIENT_SECRET: "your-google-secret"  # [Secret]
GCP_VM_EXTERNAL_IP: "your-vm-external-ip"
GCP_VM_USERNAME: "your-vm-username"
```

## 🔧 Updated Pipeline Configuration

The updated `azure-pipelines.yml` will use ACR instead of Docker Hub:

### Key Changes:
1. **Service Connection**: `ACRConnection` instead of `DockerHubConnection`
2. **Registry**: `$(acrLoginServer)` instead of Docker Hub
3. **Repository**: `$(acrLoginServer)/$(dockerRepository)` format
4. **Authentication**: Azure AD instead of username/password

### Benefits:
- 🔐 **Better Security**: No need to manage Docker Hub credentials
- 🚀 **Faster Builds**: ACR is in same Azure region
- 🎯 **Better Integration**: Native Azure DevOps support
- 💰 **Cost Optimization**: Pay only for what you use
- 🛡️ **Advanced Features**: Vulnerability scanning, geo-replication

## 📊 ACR Pricing (Approximate)
- **Basic SKU**: ~$5/month + storage (~$0.10/GB/month)
- **Standard SKU**: ~$20/month + storage (recommended for production)
- **Premium SKU**: ~$50/month + storage (geo-replication, advanced security)

For your application size, Basic SKU should be sufficient initially.

## 🔍 Monitoring and Management

### View Images in ACR:
```bash
# List repositories
az acr repository list --name shifthandoverregistry

# List tags for repository
az acr repository show-tags --name shifthandoverregistry --repository shift-handover-app

# Delete old tags (cleanup)
az acr repository delete --name shifthandoverregistry --image shift-handover-app:old-tag
```

### Azure Portal:
- Go to your ACR → Repositories → shift-handover-app
- View tags, vulnerabilities, and metrics

This setup provides a more integrated, secure, and cost-effective solution for your container registry needs!