# Azure DevOps CI/CD Setup Guide for Shift Handover App

This guide will help you set up a complete CI/CD pipeline using Azure DevOps to build, push to Docker Hub, and deploy to your GCP VM.

## 📋 Prerequisites

1. **Azure DevOps** account and project
2. **Docker Hub** account
3. **GCP VM** instance running Ubuntu
4. **Git repository** in Azure Repos or GitHub

## 🚀 Step-by-Step Setup

### Step 1: Prepare Docker Hub

1. Create a Docker Hub account at https://hub.docker.com
2. Create a new repository named `shift-handover-app`
3. Generate an access token:
   - Go to Account Settings → Security → New Access Token
   - Save the token securely

### Step 2: Set Up GCP VM

```bash
# Create GCP VM (if not already created)
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

# SSH into VM and run setup
gcloud compute ssh shift-handover-vm --zone=us-central1-a

# On the VM, run:
curl -sSL https://raw.githubusercontent.com/your-repo/main/deployment/setup-vm.sh | bash
```

### Step 3: Configure SSH Access for Azure DevOps

On your GCP VM:

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "azure-devops@shift-handover"

# Display public key (copy this)
cat ~/.ssh/id_rsa.pub

# Add to authorized_keys if not already done
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

### Step 4: Create Azure DevOps Service Connections

#### Docker Hub Service Connection

1. Go to Azure DevOps → Project Settings → Service Connections
2. Click "New service connection" → "Docker Registry"
3. Select "Docker Hub"
4. Fill in:
   - **Connection name**: `DockerHubConnection`
   - **Docker ID**: Your Docker Hub username
   - **Password**: Your Docker Hub access token
5. Save the connection

#### SSH Service Connection for GCP VM

1. Click "New service connection" → "SSH"
2. Fill in:
   - **Connection name**: `GCPVMConnection`
   - **Host name**: Your GCP VM external IP
   - **Port**: 22
   - **User name**: Your VM username
   - **Private key**: Content of your VM's private key (`cat ~/.ssh/id_rsa`)
3. Save the connection

### Step 5: Update Pipeline Variables

Edit `azure-pipelines.yml` and update these variables:

```yaml
variables:
  dockerHubUsername: 'your-dockerhub-username'  # Your Docker Hub username
  vmExternalIP: 'YOUR-VM-EXTERNAL-IP'          # Your GCP VM external IP
  vmUsername: 'your-vm-username'               # Your VM username
```

### Step 6: Set Up Azure Pipeline

1. Go to Azure DevOps → Pipelines → Create Pipeline
2. Select your repository source (Azure Repos Git/GitHub)
3. Select your repository
4. Choose "Existing Azure Pipelines YAML file"
5. Select `/azure-pipelines.yml`
6. Review and run the pipeline

### Step 7: Configure Environment Variables on VM

SSH into your GCP VM and edit the environment file:

```bash
sudo nano /opt/shift-handover-app/.env
```

Update with your actual values:

```env
SECRET_KEY=your-actual-secret-key-here
FLASK_ENV=production
DATABASE_URI=sqlite:///shift_handover.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
TEAM_EMAIL=your-email@gmail.com
```

## 🔄 Pipeline Workflow

The pipeline performs these steps:

### Build Stage:
1. **Checkout** source code
2. **Login** to Docker Hub
3. **Build** Docker image using `Dockerfile.prod`
4. **Tag** image with build ID and 'latest'
5. **Push** image to Docker Hub
6. **Publish** deployment artifacts

### Deploy Stage (Production only):
1. **Download** deployment scripts
2. **SSH** into GCP VM
3. **Stop** existing container
4. **Pull** latest image from Docker Hub
5. **Run** new container
6. **Verify** deployment success
7. **Clean up** old images

## 🧪 Manual Testing

Before setting up the pipeline, test manually:

```bash
# Build and push image locally
docker build -f Dockerfile.prod -t your-username/shift-handover-app:test .
docker push your-username/shift-handover-app:test

# On GCP VM, test deployment
chmod +x /opt/shift-handover-app/deployment/deploy-manual.sh
sudo /opt/shift-handover-app/deployment/deploy-manual.sh
```

## 🔍 Monitoring and Troubleshooting

### Check Pipeline Logs
- Go to Azure DevOps → Pipelines → Your Pipeline → Latest Run
- Click on failed tasks to see detailed logs

### Check Container Status on VM
```bash
# SSH into VM
gcloud compute ssh shift-handover-vm --zone=us-central1-a

# Check container status
sudo docker ps
sudo docker logs shift-handover-app

# Check application health
curl http://localhost/
```

### Common Issues and Solutions

1. **SSH Connection Failed**
   - Verify SSH key is correct
   - Check VM external IP
   - Ensure firewall allows SSH (port 22)

2. **Docker Pull Failed**
   - Verify Docker Hub credentials
   - Check image name and tag
   - Ensure VM has internet access

3. **Container Won't Start**
   - Check environment variables
   - Verify Docker image
   - Check container logs: `sudo docker logs shift-handover-app`

4. **Health Check Failed**
   - Verify application starts correctly
   - Check port mapping (80:5000)
   - Review application logs

## 🔐 Security Best Practices

1. **Secrets Management**: Use Azure Key Vault for sensitive data
2. **SSH Keys**: Use separate keys for deployment
3. **Firewall**: Only allow necessary ports
4. **SSL**: Set up SSL certificate for production
5. **Access Control**: Limit Azure DevOps permissions

## 📊 Cost Estimation

- **Azure DevOps**: Free for up to 5 users
- **GCP VM** (e2-medium): ~$13-30/month
- **Docker Hub**: Free for public repos
- **Total**: ~$13-30/month

## 🎯 Next Steps

1. Set up monitoring and alerting
2. Configure SSL certificate
3. Set up database backups
4. Implement blue-green deployment
5. Add integration tests to pipeline

## 📞 Support

If you encounter issues:
1. Check Azure DevOps pipeline logs
2. Verify service connections
3. Test manual deployment
4. Check GCP VM logs
5. Review Docker Hub repository