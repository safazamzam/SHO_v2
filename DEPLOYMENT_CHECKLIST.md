# 🚀 Azure Pipeline to GCP VM Deployment Checklist# Azure DevOps CI/CD Setup Checklist



## ✅ Pre-Deployment Checklist## 📋 Pre-Setup Checklist



### 1. 🖥️ GCP VM Preparation### Accounts & Services

- [ ] **VM is running** and accessible via SSH- [ ] Azure DevOps account created

- [ ] **External IP** is available and noted- [ ] Azure DevOps project created

- [ ] **Firewall rules** allow HTTP (80), HTTPS (443), and SSH (22)- [ ] Docker Hub account created

- [ ] **Run setup script**: Upload and execute `setup-gcp-vm.sh`- [ ] GCP account with billing enabled

  ```bash- [ ] Git repository ready (Azure Repos or GitHub)

  # Upload the script to your GCP VM

  scp setup-gcp-vm.sh username@your-vm-ip:~/### Local Environment

  - [ ] Docker Desktop installed and running

  # SSH to VM and run setup- [ ] gcloud CLI installed (for GCP VM management)

  ssh username@your-vm-ip- [ ] Git configured with your repository

  chmod +x setup-gcp-vm.sh

  ./setup-gcp-vm.sh---

  ```

## 🔧 Setup Phase 1: Prepare Docker Image

### 2. 🐳 Docker Hub Setup

- [ ] **Docker Hub account** created### Step 1: Update Configuration Files

- [ ] **Repository created**: `shift-handover-app`- [ ] Edit `build-and-push.ps1` - Update `$DOCKER_USERNAME`

- [ ] **Access token** generated and saved securely- [ ] Edit `azure-pipelines.yml` - Update `dockerHubUsername` variable

- [ ] Create Docker Hub repository named `shift-handover-app`

### 3. 🔐 Azure DevOps Service Connections

### Step 2: Test Docker Build Locally

#### A. Docker Hub Connection```powershell

- [ ] Navigate to: Project Settings → Service connections# Run this in PowerShell

- [ ] Create **Docker Registry** connection.\build-and-push.ps1

- [ ] Connection name: `DockerHubConnection````

- [ ] Docker Hub username and access token configured- [ ] Docker image builds successfully

- [ ] Image pushes to Docker Hub

#### B. GCP VM SSH Connection  - [ ] Local test passes

- [ ] **SSH key pair** generated for Azure DevOps- [ ] Verify image exists in Docker Hub

- [ ] **Public key** added to GCP VM: `~/.ssh/authorized_keys`

- [ ] **SSH connection** created in Azure DevOps---

- [ ] Connection name: `GCPVMConnection`

- [ ] Connection tested successfully## 🏗️ Setup Phase 2: Prepare GCP VM



### 4. 📊 Azure DevOps Variable Groups### Step 1: Create GCP VM

```bash

#### Create Variable Group: `production-secrets`# Set your project

- [ ] Navigate to: Pipelines → Library → Variable groupsgcloud config set project YOUR-PROJECT-ID

- [ ] Create group: `production-secrets`

- [ ] Add variables (mark sensitive ones as secret):# Create VM

gcloud compute instances create shift-handover-vm \

```yaml    --zone=us-central1-a \

SECRET_KEY: "your-super-secret-flask-key"  # [Secret]    --machine-type=e2-medium \

DATABASE_URI: "sqlite:///shift_handover.db"    --tags=http-server,https-server \

SMTP_USERNAME: "your-email@gmail.com"    --image=ubuntu-2004-focal-v20231101 \

SMTP_PASSWORD: "your-app-password"  # [Secret]    --image-project=ubuntu-os-cloud \

SERVICENOW_INSTANCE: "your-instance.service-now.com"    --boot-disk-size=20GB

SERVICENOW_USERNAME: "service-account"

SERVICENOW_PASSWORD: "service-password"  # [Secret]# Create firewall rules

SSO_ENCRYPTION_KEY: "your-fernet-key"  # [Secret]gcloud compute firewall-rules create allow-http --allow tcp:80 --target-tags http-server

GOOGLE_OAUTH_CLIENT_ID: "your-google-client-id"gcloud compute firewall-rules create allow-https --allow tcp:443 --target-tags https-server

GOOGLE_OAUTH_CLIENT_SECRET: "your-google-secret"  # [Secret]```

GCP_VM_EXTERNAL_IP: "your-vm-external-ip"- [ ] GCP VM created successfully

GCP_VM_USERNAME: "your-vm-username"- [ ] Firewall rules configured

DOCKER_HUB_USERNAME: "your-dockerhub-username"- [ ] Can SSH into VM

```

### Step 2: Setup VM for Deployment

#### Create Variable Group: `pipeline-config````bash

- [ ] Create group: `pipeline-config`# SSH into VM

- [ ] Add variables:gcloud compute ssh shift-handover-vm --zone=us-central1-a



```yaml# Copy and run setup script (update the URL with your repository)

dockerRepository: "shift-handover-app"curl -sSL https://raw.githubusercontent.com/YOUR-REPO/main/deployment/setup-vm.sh | bash

pythonVersion: "3.11"```

vmProjectPath: "/opt/shift-handover-app"- [ ] Docker installed on VM

```- [ ] Environment file created at `/opt/shift-handover-app/.env`

- [ ] SSH key generated for Azure DevOps

### 5. 🌍 Environment Setup

- [ ] Navigate to: Pipelines → Environments### Step 3: Configure Environment Variables

- [ ] Create environment: `production-gcp````bash

- [ ] Add approvals/checks if needed# Edit environment file

sudo nano /opt/shift-handover-app/.env

## 🚀 Deployment Steps```

- [ ] SECRET_KEY updated with secure value

### 1. 📝 Commit and Push Pipeline- [ ] Database configuration set

- [ ] Verify `azure-pipelines.yml` is in repository root- [ ] Email configuration set

- [ ] Commit all changes to main branch- [ ] ServiceNow configuration set (if needed)

- [ ] Push to Azure DevOps repository

---

### 2. 🔄 Create Pipeline

- [ ] Go to Azure DevOps → Pipelines → New pipeline## 🔐 Setup Phase 3: Configure Azure DevOps

- [ ] Select your repository

- [ ] Choose "Existing Azure Pipelines YAML file"### Step 1: Create Service Connections

- [ ] Select `azure-pipelines.yml`

- [ ] Review and save the pipeline#### Docker Hub Connection

1. Go to Project Settings → Service Connections

### 3. ▶️ Run First Deployment2. New service connection → Docker Registry → Docker Hub

- [ ] Trigger pipeline manually or push to main branch3. Fill in details:

- [ ] Monitor pipeline execution   - [ ] Connection name: `DockerHubConnection`

- [ ] Check for any errors in build/deploy stages   - [ ] Docker ID: Your Docker Hub username

   - [ ] Password: Docker Hub access token

### 4. ✅ Verify Deployment   - [ ] Connection created and tested

- [ ] Check container status on GCP VM:

  ```bash#### SSH Connection for GCP VM

  ssh username@your-vm-ip1. New service connection → SSH

  /opt/shift-handover-status.sh2. Fill in details:

  ```   - [ ] Connection name: `GCPVMConnection`

- [ ] Test application access: `http://your-vm-ip/`   - [ ] Host name: VM external IP address

- [ ] Verify login page: `http://your-vm-ip/login`   - [ ] User name: VM username

- [ ] Check SSO functionality if configured   - [ ] Private key: Content from `cat ~/.ssh/id_rsa` on VM

   - [ ] Connection created and tested

## 🔍 Troubleshooting Common Issues

### Step 2: Update Pipeline Variables

### Build Stage IssuesEdit `azure-pipelines.yml`:

- [ ] **Python dependencies**: Check `requirements.txt` is up to date- [ ] `dockerHubUsername` updated with your Docker Hub username

- [ ] **Import errors**: Verify all modules are properly installed- [ ] `vmExternalIP` updated with your VM's external IP

- [ ] **Docker build fails**: Check Dockerfile syntax- [ ] `vmUsername` updated with your VM username



### Docker Stage Issues  ### Step 3: Create Pipeline

- [ ] **Login failed**: Verify Docker Hub service connection1. Go to Pipelines → Create Pipeline

- [ ] **Push failed**: Check Docker Hub permissions and repository name2. Select repository source

- [ ] **Image size**: Optimize Dockerfile if image is too large3. Choose "Existing Azure Pipelines YAML file"

4. Select `/azure-pipelines.yml`

### Deploy Stage Issues- [ ] Pipeline created successfully

- [ ] **SSH connection failed**: - [ ] Pipeline runs without errors

  - Verify SSH service connection configuration

  - Check GCP VM firewall allows SSH (port 22)---

  - Ensure SSH key is properly configured

- [ ] **Container won't start**:## 🧪 Testing Phase

  - Check environment variables are set correctly

  - Verify Docker image exists and is accessible### Test 1: Manual Docker Deployment

  - Check GCP VM has sufficient resourcesOn your GCP VM:

- [ ] **Application not responding**:```bash

  - Check container logs: `docker logs shift-handover-app`# Update the script with your Docker Hub username

  - Verify port mapping: `-p 80:5000`sudo nano /opt/shift-handover-app/deployment/deploy-manual.sh

  - Check GCP VM firewall allows HTTP (port 80)

# Run manual deployment

### Health Check Issueschmod +x /opt/shift-handover-app/deployment/deploy-manual.sh

- [ ] **Timeout errors**: Increase wait time in pipelinesudo /opt/shift-handover-app/deployment/deploy-manual.sh

- [ ] **404 errors**: Verify application routes are correct```

- [ ] **500 errors**: Check application configuration and logs- [ ] Container starts successfully

- [ ] Application responds on port 80

## 📊 Post-Deployment Monitoring- [ ] Health check passes



### Daily Checks### Test 2: Pipeline Deployment

- [ ] Monitor pipeline success/failure notifications1. Make a small change to your code

- [ ] Check application availability2. Commit and push to main branch

- [ ] Review container resource usage3. Watch pipeline execution

- [ ] Build stage completes successfully

### Weekly Maintenance- [ ] Deploy stage completes successfully

- [ ] Run cleanup script: `/opt/shift-handover-maintenance.sh`- [ ] Application accessible via VM external IP

- [ ] Check backup script: `/opt/shift-handover-backup.sh`

- [ ] Review application logs for errors---

- [ ] Update system packages if needed

## 🎯 Post-Deployment Tasks

### Monthly Reviews

- [ ] Review and rotate secrets/passwords### Security & SSL

- [ ] Check and update dependencies- [ ] Configure SSL certificate (if using domain)

- [ ] Optimize Docker images if needed- [ ] Set up proper secrets management

- [ ] Review backup retention policy- [ ] Review firewall settings



## 🆘 Emergency Procedures### Monitoring

- [ ] Set up application monitoring

### Application Down- [ ] Configure Azure DevOps alerts

```bash- [ ] Set up log aggregation

# SSH to GCP VM

ssh username@your-vm-ip### Documentation

- [ ] Document deployment process

# Check container status- [ ] Create runbook for troubleshooting

docker ps -a | grep shift-handover-app- [ ] Update team with access details



# View recent logs---

docker logs shift-handover-app --tail 100

## 📞 Troubleshooting Checklist

# Restart container

docker restart shift-handover-app### Pipeline Issues

- [ ] Check service connection configurations

# If container missing, re-run deployment- [ ] Verify Docker Hub credentials

docker pull your-dockerhub-username/shift-handover-app:latest- [ ] Check SSH connection to VM

# (Check pipeline for exact run command)- [ ] Review pipeline logs

```

### VM Deployment Issues

### Rollback to Previous Version- [ ] Check container logs: `sudo docker logs shift-handover-app`

```bash- [ ] Verify environment variables

# Check available images- [ ] Check port accessibility

docker images your-dockerhub-username/shift-handover-app- [ ] Verify image pull from Docker Hub



# Stop current container### Application Issues

docker stop shift-handover-app- [ ] Check application logs

docker rm shift-handover-app- [ ] Verify database connectivity

- [ ] Test email configuration

# Run previous version- [ ] Check ServiceNow integration

docker run -d --name shift-handover-app \

  --restart unless-stopped \---

  -p 80:5000 \

  [environment variables] \## 📝 Important URLs & Commands

  your-dockerhub-username/shift-handover-app:previous-tag

```### Useful Commands

```bash

## 📞 Support Contacts# Check VM external IP

gcloud compute instances describe shift-handover-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"

- **Azure DevOps Issues**: Check pipeline logs and Azure DevOps documentation

- **GCP VM Issues**: Monitor GCP Console and check VM logs# SSH to VM

- **Application Issues**: Review container logs and application documentationgcloud compute ssh shift-handover-vm --zone=us-central1-a

- **Docker Issues**: Check Docker documentation and container status

# Check container status

---sudo docker ps

sudo docker logs shift-handover-app

**Repository**: https://dev.azure.com/mdsajid020/shift_handover_v2

**Last Updated**: October 15, 2025# Restart container
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