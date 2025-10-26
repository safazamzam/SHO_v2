# 🐧 Linux Host Setup Guide for EPAM Lab Domain
# Setting up handover.lab.epam.com on 35.200.202.18

## 📋 Prerequisites (NAT Team Handles)
✅ **NAT Configuration**: Another team will handle NAT setup  
✅ **DNS Configuration**: `handover.lab.epam.com` → NAT Gateway → `35.200.202.18`  
✅ **Firewall**: Ports 80 and 443 forwarded to this Linux host  

## 🎯 Your Task: Configure Application on Linux Host

### Step 1: Prepare Linux Host (35.200.202.18)

#### 1.1 Update System
```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install required tools
sudo apt install -y curl wget git unzip
```

#### 1.2 Install Docker and Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### 1.3 Configure Firewall (if needed)
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Keep SSH access
sudo ufw allow 22/tcp

# Enable firewall (if not already enabled)
sudo ufw --force enable

# Check status
sudo ufw status
```

### Step 2: Transfer Files to Linux Host

Upload these files to your Linux host (35.200.202.18):

#### Required Files:
```
📁 Application Files:
├── app.py
├── requirements.txt
├── docker-compose.prod.yml
├── .env.domain (will be created by setup script)
├── models/
├── routes/
├── templates/
├── static/
└── secrets/

📁 Configuration Files:
├── setup-epam-lab.sh        # Main setup script
├── nginx/conf.d/app.conf     # Will be created by setup script
└── docker-compose.prod.yml  # Production Docker configuration
```

#### Transfer Methods:

**Option A: Using SCP**
```bash
# From your Windows machine
scp -r /path/to/your/app/* user@35.200.202.18:/home/user/shift-handover-app/
```

**Option B: Using Git** (Recommended)
```bash
# On Linux host
git clone https://github.com/safazamzam/SHO_v2.git
cd SHO_v2/shift_handover_app_flash_bkp
```

**Option C: Using SFTP**
```bash
# Upload files using SFTP client or VS Code Remote SSH
```

### Step 3: Run Setup Script on Linux Host

#### 3.1 Make Script Executable
```bash
# Navigate to application directory
cd /path/to/your/shift-handover-app

# Make setup script executable
chmod +x setup-epam-lab.sh
```

#### 3.2 Test Setup (Recommended)
```bash
# Test run (no changes applied)
./setup-epam-lab.sh --test --email admin@epam.com
```

#### 3.3 Run Actual Setup
```bash
# Run with your EPAM email
./setup-epam-lab.sh --email your-email@epam.com

# Or skip SSL if you want HTTP only
./setup-epam-lab.sh --email your-email@epam.com --skip-ssl
```

### Step 4: Monitor and Verify

#### 4.1 Check Services
```bash
# Check Docker services
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Use monitoring script
./monitor-epam-lab.sh
```

#### 4.2 Test Local Access
```bash
# Test health endpoint locally
curl http://localhost:80/health

# Test with domain (if NAT is configured)
curl https://handover.lab.epam.com/health
```

#### 4.3 Check SSL Certificate (if enabled)
```bash
# Check certificate status
docker run --rm -v $(pwd)/certbot_conf:/etc/letsencrypt certbot/certbot certificates

# Test SSL
openssl s_client -connect handover.lab.epam.com:443 -servername handover.lab.epam.com
```

## 🚀 Complete Setup Commands

Here's the complete sequence to run on your Linux host:

```bash
# 1. Prepare environment
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git unzip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Configure firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

# 5. Clone or upload your application
# (Use git clone or upload files)

# 6. Navigate to app directory
cd /path/to/your/shift-handover-app

# 7. Run setup
chmod +x setup-epam-lab.sh
./setup-epam-lab.sh --email your-email@epam.com

# 8. Monitor
./monitor-epam-lab.sh
```

## 📊 Expected Results

After successful setup:

### ✅ Services Running:
```bash
$ docker-compose -f docker-compose.prod.yml ps
     Name                    Command               State           Ports         
--------------------------------------------------------------------------------
app_nginx_1      /docker-entrypoint.sh ngin ...   Up      0.0.0.0:80->80/tcp,   
                                                           0.0.0.0:443->443/tcp  
app_web_1        python app.py                     Up      5000/tcp              
app_mysql_1      docker-entrypoint.sh mysqld      Up      3306/tcp              
```

### ✅ URLs Accessible:
- **Health Check**: `https://handover.lab.epam.com/health`
- **Login Page**: `https://handover.lab.epam.com/login`
- **Main App**: `https://handover.lab.epam.com`

### ✅ SSL Certificate:
```bash
$ curl -I https://handover.lab.epam.com
HTTP/2 200 
server: nginx/1.21.6
content-type: text/html; charset=utf-8
strict-transport-security: max-age=31536000; includeSubDomains; preload
```

## 🔧 Troubleshooting

### Issue 1: Services Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check Docker daemon
sudo systemctl status docker

# Restart Docker if needed
sudo systemctl restart docker
```

### Issue 2: SSL Certificate Fails
```bash
# Check domain accessibility
curl http://handover.lab.epam.com/.well-known/acme-challenge/test

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Manually retry SSL
docker run --rm \
  -v $(pwd)/certbot_conf:/etc/letsencrypt \
  -v $(pwd)/certbot_www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@epam.com \
  --agree-tos \
  --no-eff-email \
  -d handover.lab.epam.com
```

### Issue 3: Domain Not Accessible
```bash
# Test local access first
curl http://localhost:80/health

# Check if ports are open
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Check firewall
sudo ufw status

# Check NAT configuration with NAT team
```

### Issue 4: Application Errors
```bash
# Check application logs
docker-compose -f docker-compose.prod.yml logs web

# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## 📁 File Structure After Setup

```
/path/to/your/shift-handover-app/
├── app.py
├── docker-compose.prod.yml
├── .env.domain                    # EPAM Lab configuration
├── setup-epam-lab.sh              # Setup script
├── monitor-epam-lab.sh            # Monitoring script  
├── renew-ssl.sh                   # SSL renewal script
├── nginx/
│   └── conf.d/
│       └── app.conf               # EPAM Lab nginx config
├── certbot_conf/                  # SSL certificates
│   └── live/handover.lab.epam.com/
├── certbot_www/                   # Let's Encrypt challenges
├── models/
├── routes/
├── templates/
├── static/
└── secrets/
```

## 🎯 Success Criteria

✅ **Docker services running**  
✅ **Nginx responding on ports 80/443**  
✅ **SSL certificate obtained and valid**  
✅ **Health check returning 200 OK**  
✅ **Application accessible via domain**  
✅ **Monitoring scripts created**  

## 📞 Next Steps

1. **Run the setup script**: `./setup-epam-lab.sh --email your-email@epam.com`
2. **Verify local access**: `curl http://localhost:80/health`
3. **Coordinate with NAT team**: Ensure traffic forwarding is working
4. **Test domain access**: `curl https://handover.lab.epam.com/health`
5. **Set up monitoring**: Use `./monitor-epam-lab.sh` regularly

The setup script handles all the nginx configuration, SSL certificates, and service startup automatically. The NAT team just needs to ensure traffic for `handover.lab.epam.com` reaches your Linux host on ports 80 and 443.