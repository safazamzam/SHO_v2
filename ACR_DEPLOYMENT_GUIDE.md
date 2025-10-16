# 🚀 Updated Azure Pipeline with Azure Container Registry (ACR)

## 🏗️ **Why Azure Container Registry?**

### ✅ **Key Benefits:**
- **🔗 Native Integration**: Seamless Azure DevOps integration
- **🔐 Enhanced Security**: Private registry with Azure AD authentication
- **🚀 Better Performance**: Faster image pulls within Azure ecosystem
- **💰 Cost Effective**: Pay-per-use model, no subscription tiers
- **🛡️ Advanced Security**: Vulnerability scanning, compliance features
- **🌍 Geo-Replication**: Deploy images closer to your applications

### 📊 **ACR vs Docker Hub:**
| Feature | Azure Container Registry | Docker Hub |
|---------|-------------------------|------------|
| **Security** | ✅ Private, Azure AD | ⚠️ Public by default |
| **Integration** | ✅ Native Azure DevOps | ⚠️ External credentials |
| **Performance** | ✅ Azure optimized | ⚠️ Internet dependent |
| **Cost** | ✅ Pay-as-you-use | ⚠️ Monthly subscriptions |

## 🔧 **Setup Steps**

### 1. 🏗️ Create Azure Container Registry

#### Option A: Azure Portal
```
1. Go to Azure Portal → Create Resource → Container Registry
2. Registry name: shifthandoverregistry (globally unique)
3. Resource group: rg-shift-handover-prod
4. Location: East US
5. SKU: Basic (upgrade to Standard for production)
6. Admin user: Enable
7. Create
```

#### Option B: Azure CLI
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-shift-handover-prod --location eastus

# Create ACR
az acr create \
  --resource-group rg-shift-handover-prod \
  --name shifthandoverregistry \
  --sku Basic \
  --admin-enabled true

# Get login server
az acr show --name shifthandoverregistry --query loginServer
```

### 2. 🔐 Configure Azure DevOps Service Connection

#### Create ACR Service Connection:
```
1. Azure DevOps → Project Settings → Service connections
2. New service connection → Docker Registry
3. Select "Azure Container Registry"
4. Connection name: ACRConnection
5. Azure subscription: Select your subscription
6. Azure container registry: shifthandoverregistry
7. Save
```

### 3. 📊 Update Variable Groups

#### Update `pipeline-config` Variable Group:
```yaml
# Replace Docker Hub variables with ACR variables
acrName: "shifthandoverregistry"
acrLoginServer: "shifthandoverregistry.azurecr.io"
dockerRepository: "shift-handover-app"
pythonVersion: "3.11"
vmProjectPath: "/opt/shift-handover-app"
```

#### Keep `production-secrets` Variable Group (remove Docker Hub):
```yaml
# Remove DOCKER_HUB_USERNAME, keep these:
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

## 🚀 **Updated Pipeline Features**

### ✅ **What Changed:**
1. **Service Connection**: `ACRConnection` instead of `DockerHubConnection`
2. **Registry URL**: `$(acrLoginServer)` instead of Docker Hub
3. **Authentication**: Azure AD instead of username/password
4. **Image Names**: `$(acrLoginServer)/$(dockerRepository):$(imageTag)`
5. **GCP VM Access**: Automatic Azure CLI installation for ACR access

### 🔄 **Pipeline Flow:**
```
1. 🔨 Build → Validate Python application
2. 🏗️ Docker Build → Build image and push to ACR
3. 🚀 Deploy → Pull from ACR and deploy to GCP VM
4. ✅ Verify → Health checks and monitoring
5. 🧹 Cleanup → Remove old images from VM
```

## 📋 **Updated Deployment Checklist**

### ✅ **Pre-Deployment (ACR Version):**
- [ ] **Azure Container Registry** created and configured
- [ ] **Service connection** `ACRConnection` set up in Azure DevOps
- [ ] **Variable groups** updated with ACR details
- [ ] **GCP VM** prepared with setup script
- [ ] **Azure CLI** will be auto-installed on GCP VM during first deployment

### 🚀 **Deployment Process:**
1. **Commit** your changes to main branch
2. **Pipeline** automatically triggers
3. **Monitor** in Azure DevOps → Pipelines
4. **Verify** application at `http://your-vm-ip/`

## 🔍 **Monitoring Your ACR**

### Azure Portal:
```
1. Go to your Container Registry
2. Navigate to Repositories
3. View shift-handover-app images and tags
4. Check vulnerabilities and metrics
```

### Azure CLI:
```bash
# List repositories
az acr repository list --name shifthandoverregistry

# List tags
az acr repository show-tags --name shifthandoverregistry --repository shift-handover-app

# Delete old images
az acr repository delete --name shifthandoverregistry --image shift-handover-app:old-tag
```

## 💰 **Cost Optimization**

### **ACR Pricing:**
- **Basic**: ~$5/month + storage ($0.10/GB/month)
- **Standard**: ~$20/month + enhanced features
- **Premium**: ~$50/month + geo-replication

### **Cost Savings vs Docker Hub:**
- No monthly subscription fees
- Pay only for actual usage
- Free tier available for small projects

## 🛡️ **Security Enhancements**

### **Built-in Security:**
- ✅ **Private Registry**: Images not publicly accessible
- ✅ **Azure AD Integration**: No external credentials to manage
- ✅ **Vulnerability Scanning**: Built-in image security scanning
- ✅ **Compliance**: Meets enterprise security requirements

### **Access Control:**
- ✅ **Role-based Access**: Fine-grained permissions
- ✅ **Service Principal**: Secure automated access
- ✅ **Network Security**: VNet integration available

## 🎯 **Next Steps After Setup**

1. **✅ Run Pipeline**: Push to main branch to trigger deployment
2. **✅ Monitor Logs**: Watch Azure DevOps pipeline execution
3. **✅ Verify Deployment**: Check application at your GCP VM IP
4. **✅ Test Features**: Verify SSO and ServiceNow integration
5. **✅ Set up Monitoring**: Configure alerts and health checks

This Azure Container Registry setup provides a more secure, integrated, and cost-effective solution for your container image management!