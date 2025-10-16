# 🚀 Azure Pipeline to Google Cloud VM Deployment Guide

This guide will help you set up a complete CI/CD pipeline using Azure DevOps to deploy your Shift Handover Application to your Google Cloud VM.

## 📋 Prerequisites

### ✅ What You Need:
1. **Azure DevOps Project**: `https://dev.azure.com/mdsajid020/shift_handover_v2`
2. **Google Cloud VM**: Running and accessible via SSH
3. **Docker Hub Account**: For storing Docker images
4. **SSH Access**: To your GCP VM from Azure DevOps

### 🖥️ GCP VM Requirements:
- **Docker installed** on your VM
- **SSH access** configured
- **Firewall rules** allowing HTTP (port 80) and HTTPS (port 443)
- **Sufficient resources** (recommended: 2+ vCPU, 4GB+ RAM)

## 🔧 Step-by-Step Setup

### Step 1: Prepare Your GCP VM

```bash
# SSH into your GCP VM
gcloud compute ssh your-vm-name --zone=your-zone

# Install Docker (if not already installed)
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
# Logout and login again for group changes to take effect

# Create application directories
sudo mkdir -p /opt/shift-handover-data
sudo mkdir -p /opt/shift-handover-uploads
sudo chown -R $USER:$USER /opt/shift-handover-*

# Test Docker
docker --version
docker ps
```

### Step 2: Set Up Docker Hub

1. **Create Docker Hub Account**: https://hub.docker.com
2. **Create Repository**: 
   - Repository name: `shift-handover-app`
   - Visibility: Public (or Private if you prefer)
3. **Generate Access Token**:
   - Go to Account Settings → Security → New Access Token
   - Save the token securely

### Step 3: Configure Azure DevOps Service Connections

#### A. Docker Hub Service Connection
1. Go to Azure DevOps → Project Settings → Service connections
2. Click "New service connection" → "Docker Registry"
3. Select "Docker Hub"
4. Fill in:
   - **Connection name**: `DockerHubConnection`
   - **Docker Hub username**: Your Docker Hub username
   - **Password**: Your Docker Hub access token
5. Save the connection

#### B. SSH Service Connection for GCP VM
1. Generate SSH key pair on your local machine:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "azure-devops@yourdomain.com"
   # Save as: azure-devops-gcp-key
   ```

2. Add public key to your GCP VM:
   ```bash
   # Copy public key content
   cat azure-devops-gcp-key.pub
   
   # SSH to your GCP VM and add to authorized_keys
   echo "your-public-key-content" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

3. Create SSH service connection in Azure DevOps:
   - Go to Service connections → New → SSH
   - **Connection name**: `GCPVMConnection`
   - **Host name**: Your GCP VM external IP
   - **Username**: Your VM username
   - **Private key**: Paste your private key content
   - Test the connection

### Step 4: Configure Pipeline Variables

In Azure DevOps → Pipelines → Library → Variable groups:

#### Create Variable Group: `production-secrets`
```yaml
Variables:
- DATABASE_URI: "sqlite:///shift_handover.db"  # or PostgreSQL connection string
- SECRET_KEY: "your-super-secret-key-here"
- SMTP_USERNAME: "your-email@gmail.com"
- SMTP_PASSWORD: "your-app-password"
- SERVICENOW_INSTANCE: "your-instance.service-now.com"
- SERVICENOW_USERNAME: "service-account"
- SERVICENOW_PASSWORD: "service-password"  # Mark as secret
- SSO_ENCRYPTION_KEY: "your-fernet-encryption-key"  # Mark as secret
- GCP_VM_EXTERNAL_IP: "your-vm-external-ip"
- GCP_VM_USERNAME: "your-vm-username"
- DOCKER_HUB_USERNAME: "your-dockerhub-username"
```

#### Create Variable Group: `pipeline-config`
```yaml
Variables:
- dockerRepository: "shift-handover-app"
- pythonVersion: "3.11"
- vmProjectPath: "/opt/shift-handover-app"
```

### Step 5: Update Pipeline File

Your `azure-pipelines.yml` should be configured to:
1. Build the Docker image
2. Push to Docker Hub
3. Deploy to GCP VM
4. Perform health checks

### Step 6: Create Environment Configuration

1. **Create Environment File on GCP VM**:
   ```bash
   # SSH to your GCP VM
   sudo mkdir -p /opt/shift-handover-app
   sudo vim /opt/shift-handover-app/.env.production
   ```

2. **Add Production Environment Variables**:
   ```bash
   # Production Configuration
   FLASK_ENV=production
   SECRET_KEY=your-super-secret-key
   DATABASE_URI=postgresql://user:pass@db-server:5432/shift_handover
   
   # Email Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   
   # ServiceNow Configuration
   SERVICENOW_INSTANCE=your-instance.service-now.com
   SERVICENOW_USERNAME=service-account
   SERVICENOW_PASSWORD=service-password
   SERVICENOW_ENABLED=true
   
   # SSO Configuration
   SSO_ENCRYPTION_KEY=your-fernet-encryption-key
   GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
   GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
   ```

3. **Secure the file**:
   ```bash
   sudo chmod 600 /opt/shift-handover-app/.env.production
   sudo chown $USER:$USER /opt/shift-handover-app/.env.production
   ```

## 🚀 Deployment Process

### Manual Trigger:
1. Push code to `main` branch
2. Azure Pipeline automatically triggers
3. Monitor pipeline execution in Azure DevOps

### Pipeline Stages:
1. **🔨 Build**: Install dependencies, validate code
2. **🐳 Docker Build**: Build and push Docker image
3. **🚀 Deploy**: Deploy to GCP VM
4. **✅ Verify**: Health checks and validation
5. **🧹 Cleanup**: Remove old Docker images

### Monitoring Deployment:
```bash
# SSH to your GCP VM to monitor
ssh your-username@your-vm-ip

# Check container status
docker ps

# View application logs
docker logs shift-handover-app -f

# Check application health
curl http://localhost/
```

## 🔍 Troubleshooting

### Common Issues:

1. **SSH Connection Failed**:
   ```bash
   # Test SSH connection manually
   ssh -i azure-devops-gcp-key your-username@your-vm-ip
   ```

2. **Docker Permission Denied**:
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

3. **Container Not Starting**:
   ```bash
   # Check container logs
   docker logs shift-handover-app
   
   # Check if port is already in use
   sudo netstat -tulpn | grep :80
   ```

4. **Database Issues**:
   ```bash
   # Check if database directory is accessible
   ls -la /opt/shift-handover-data
   
   # Initialize database if needed
   docker exec -it shift-handover-app flask db upgrade
   ```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **SSH Keys**: Use dedicated keys for Azure DevOps
3. **Firewall**: Only open necessary ports (80, 443, 22)
4. **SSL/TLS**: Configure HTTPS with Let's Encrypt
5. **Database**: Use PostgreSQL with proper authentication
6. **Updates**: Keep VM and Docker updated

## 📊 Monitoring and Maintenance

### Application Monitoring:
```bash
# Container health
docker stats shift-handover-app

# Application logs
docker logs shift-handover-app --tail 100

# Disk usage
df -h
docker system df
```

### Regular Maintenance:
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Clean up Docker
docker system prune -f
docker image prune -f

# Backup database
docker exec shift-handover-app backup-command
```

## 🎯 Next Steps

1. **SSL Certificate**: Set up Let's Encrypt for HTTPS
2. **Database**: Migrate to managed PostgreSQL
3. **Monitoring**: Add application monitoring (Prometheus/Grafana)
4. **Backup**: Implement automated backups
5. **Scaling**: Consider load balancer for multiple instances

## 📞 Support

- **Azure DevOps**: Check pipeline logs for build/deploy issues
- **GCP Console**: Monitor VM performance and networking
- **Application Logs**: Check container logs for runtime issues
- **Documentation**: Refer to Flask, Docker, and Azure DevOps docs

---

**Repository**: https://dev.azure.com/mdsajid020/shift_handover_v2
**Last Updated**: October 15, 2025