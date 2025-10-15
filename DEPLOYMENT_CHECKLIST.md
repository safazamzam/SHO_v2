# Azure DevOps CI/CD Setup Checklist

## 📋 Pre-Setup Checklist

### Accounts & Services
- [ ] Azure DevOps account created
- [ ] Azure DevOps project created
- [ ] Docker Hub account created
- [ ] GCP account with billing enabled
- [ ] Git repository ready (Azure Repos or GitHub)

### Local Environment
- [ ] Docker Desktop installed and running
- [ ] gcloud CLI installed (for GCP VM management)
- [ ] Git configured with your repository

---

## 🔧 Setup Phase 1: Prepare Docker Image

### Step 1: Update Configuration Files
- [ ] Edit `build-and-push.ps1` - Update `$DOCKER_USERNAME`
- [ ] Edit `azure-pipelines.yml` - Update `dockerHubUsername` variable
- [ ] Create Docker Hub repository named `shift-handover-app`

### Step 2: Test Docker Build Locally
```powershell
# Run this in PowerShell
.\build-and-push.ps1
```
- [ ] Docker image builds successfully
- [ ] Image pushes to Docker Hub
- [ ] Local test passes
- [ ] Verify image exists in Docker Hub

---

## 🏗️ Setup Phase 2: Prepare GCP VM

### Step 1: Create GCP VM
```bash
# Set your project
gcloud config set project YOUR-PROJECT-ID

# Create VM
gcloud compute instances create shift-handover-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --tags=http-server,https-server \
    --image=ubuntu-2004-focal-v20231101 \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB

# Create firewall rules
gcloud compute firewall-rules create allow-http --allow tcp:80 --target-tags http-server
gcloud compute firewall-rules create allow-https --allow tcp:443 --target-tags https-server
```
- [ ] GCP VM created successfully
- [ ] Firewall rules configured
- [ ] Can SSH into VM

### Step 2: Setup VM for Deployment
```bash
# SSH into VM
gcloud compute ssh shift-handover-vm --zone=us-central1-a

# Copy and run setup script (update the URL with your repository)
curl -sSL https://raw.githubusercontent.com/YOUR-REPO/main/deployment/setup-vm.sh | bash
```
- [ ] Docker installed on VM
- [ ] Environment file created at `/opt/shift-handover-app/.env`
- [ ] SSH key generated for Azure DevOps

### Step 3: Configure Environment Variables
```bash
# Edit environment file
sudo nano /opt/shift-handover-app/.env
```
- [ ] SECRET_KEY updated with secure value
- [ ] Database configuration set
- [ ] Email configuration set
- [ ] ServiceNow configuration set (if needed)

---

## 🔐 Setup Phase 3: Configure Azure DevOps

### Step 1: Create Service Connections

#### Docker Hub Connection
1. Go to Project Settings → Service Connections
2. New service connection → Docker Registry → Docker Hub
3. Fill in details:
   - [ ] Connection name: `DockerHubConnection`
   - [ ] Docker ID: Your Docker Hub username
   - [ ] Password: Docker Hub access token
   - [ ] Connection created and tested

#### SSH Connection for GCP VM
1. New service connection → SSH
2. Fill in details:
   - [ ] Connection name: `GCPVMConnection`
   - [ ] Host name: VM external IP address
   - [ ] User name: VM username
   - [ ] Private key: Content from `cat ~/.ssh/id_rsa` on VM
   - [ ] Connection created and tested

### Step 2: Update Pipeline Variables
Edit `azure-pipelines.yml`:
- [ ] `dockerHubUsername` updated with your Docker Hub username
- [ ] `vmExternalIP` updated with your VM's external IP
- [ ] `vmUsername` updated with your VM username

### Step 3: Create Pipeline
1. Go to Pipelines → Create Pipeline
2. Select repository source
3. Choose "Existing Azure Pipelines YAML file"
4. Select `/azure-pipelines.yml`
- [ ] Pipeline created successfully
- [ ] Pipeline runs without errors

---

## 🧪 Testing Phase

### Test 1: Manual Docker Deployment
On your GCP VM:
```bash
# Update the script with your Docker Hub username
sudo nano /opt/shift-handover-app/deployment/deploy-manual.sh

# Run manual deployment
chmod +x /opt/shift-handover-app/deployment/deploy-manual.sh
sudo /opt/shift-handover-app/deployment/deploy-manual.sh
```
- [ ] Container starts successfully
- [ ] Application responds on port 80
- [ ] Health check passes

### Test 2: Pipeline Deployment
1. Make a small change to your code
2. Commit and push to main branch
3. Watch pipeline execution
- [ ] Build stage completes successfully
- [ ] Deploy stage completes successfully
- [ ] Application accessible via VM external IP

---

## 🎯 Post-Deployment Tasks

### Security & SSL
- [ ] Configure SSL certificate (if using domain)
- [ ] Set up proper secrets management
- [ ] Review firewall settings

### Monitoring
- [ ] Set up application monitoring
- [ ] Configure Azure DevOps alerts
- [ ] Set up log aggregation

### Documentation
- [ ] Document deployment process
- [ ] Create runbook for troubleshooting
- [ ] Update team with access details

---

## 📞 Troubleshooting Checklist

### Pipeline Issues
- [ ] Check service connection configurations
- [ ] Verify Docker Hub credentials
- [ ] Check SSH connection to VM
- [ ] Review pipeline logs

### VM Deployment Issues
- [ ] Check container logs: `sudo docker logs shift-handover-app`
- [ ] Verify environment variables
- [ ] Check port accessibility
- [ ] Verify image pull from Docker Hub

### Application Issues
- [ ] Check application logs
- [ ] Verify database connectivity
- [ ] Test email configuration
- [ ] Check ServiceNow integration

---

## 📝 Important URLs & Commands

### Useful Commands
```bash
# Check VM external IP
gcloud compute instances describe shift-handover-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"

# SSH to VM
gcloud compute ssh shift-handover-vm --zone=us-central1-a

# Check container status
sudo docker ps
sudo docker logs shift-handover-app

# Restart container
sudo docker restart shift-handover-app
```

### Important URLs
- Docker Hub Repository: `https://hub.docker.com/r/YOUR-USERNAME/shift-handover-app`
- Application URL: `http://YOUR-VM-EXTERNAL-IP`
- Azure DevOps Pipeline: `https://dev.azure.com/YOUR-ORG/YOUR-PROJECT/_build`

---

## ✅ Completion Status

- [ ] Docker image builds and pushes successfully
- [ ] GCP VM configured and accessible
- [ ] Azure DevOps pipeline configured
- [ ] Application deploys via pipeline
- [ ] Application accessible via browser
- [ ] All tests pass

**Date Completed:** ___________
**Deployed By:** ___________
**Application URL:** ___________