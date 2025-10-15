# GCP VM Deployment Guide for Shift Handover App

## Prerequisites

1. **GCP Account** with billing enabled
2. **GCP Project** created
3. **Compute Engine API** enabled
4. **gcloud CLI** installed on your local machine

## Step 1: Create GCP VM Instance

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Create a VM instance
gcloud compute instances create shift-handover-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --network-tier=PREMIUM \
    --maintenance-policy=MIGRATE \
    --service-account=your-service-account@$PROJECT_ID.iam.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server,https-server \
    --image=ubuntu-2004-focal-v20231101 \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --boot-disk-device-name=shift-handover-vm

# Create firewall rules
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server

gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server
```

## Step 2: Connect to VM and Deploy

```bash
# SSH into the VM
gcloud compute ssh shift-handover-vm --zone=us-central1-a

# On the VM, create and run deployment
sudo apt-get update -y
sudo apt-get install -y git

# Clone your repository (replace with your actual repo)
git clone <your-repository-url> /opt/shift-handover-app
cd /opt/shift-handover-app

# Make deployment script executable and run it
chmod +x deploy-gcp.sh
./deploy-gcp.sh
```

## Step 3: Configure Environment

Edit the `.env` file with your actual configuration:

```bash
nano /opt/shift-handover-app/.env
```

Update these key variables:
- `SECRET_KEY`: Generate a strong secret key
- `DATABASE_URI`: Your database connection string
- `SMTP_*`: Your email configuration
- `SERVICENOW_*`: ServiceNow configuration (if needed)

## Step 4: Database Setup Options

### Option A: Use Cloud SQL (Recommended for production)

```bash
# Create Cloud SQL instance
gcloud sql instances create shift-handover-db \
    --database-version=MYSQL_8_0 \
    --cpu=1 \
    --memory=3840MB \
    --region=us-central1

# Create database
gcloud sql databases create shift_handover --instance=shift-handover-db

# Create user
gcloud sql users create appuser --instance=shift-handover-db --password=your-secure-password

# Get connection name
gcloud sql instances describe shift-handover-db --format="value(connectionName)"
```

Update your `.env` with:
```
DATABASE_URI=mysql+pymysql://appuser:your-secure-password@/shift_handover?unix_socket=/cloudsql/your-connection-name
```

### Option B: Use SQLite (Simple setup)

Keep the default SQLite configuration:
```
DATABASE_URI=sqlite:///shift_handover.db
```

## Step 5: Start the Application

```bash
cd /opt/shift-handover-app

# Start the application
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Step 6: Access Your Application

1. Get your VM's external IP:
```bash
gcloud compute instances describe shift-handover-vm --zone=us-central1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
```

2. Access your application at: `http://YOUR-VM-EXTERNAL-IP`

## Step 7: Domain and SSL Setup (Optional)

### If you have a domain:

1. Point your domain to the VM's external IP
2. Install Nginx and Certbot:

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/shift-handover
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/shift-handover /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Useful Commands

```bash
# Check application status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart application
docker-compose -f docker-compose.prod.yml restart

# Stop application
docker-compose -f docker-compose.prod.yml down

# Update application
git pull
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Database migration (if needed)
docker-compose -f docker-compose.prod.yml exec web flask db upgrade
```

## Security Considerations

1. **Firewall**: Only allow necessary ports (80, 443, 22)
2. **SSH**: Use SSH keys instead of passwords
3. **Database**: Use strong passwords and consider VPC
4. **SSL**: Always use SSL in production
5. **Secrets**: Use GCP Secret Manager for sensitive data
6. **Backups**: Set up regular database backups

## Monitoring

Consider setting up:
- GCP Monitoring for VM metrics
- Application logs aggregation
- Health checks and alerts
- Database monitoring

## Costs

- VM: ~$13-30/month (e2-medium)
- Cloud SQL: ~$15-50/month (small instance)
- Storage: ~$2-5/month
- Network: Minimal for small apps

Total estimated cost: $30-85/month depending on usage and configuration.