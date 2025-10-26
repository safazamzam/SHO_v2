# 🏢 EPAM Lab NAT Configuration Guide
# Setting up handover.lab.epam.com with NAT to 35.200.202.18

## 📋 Overview

This guide helps you configure NAT (Network Address Translation) to access your Shift Handover application at `handover.lab.epam.com` instead of `http://35.200.202.18:5000`.

## 🎯 Goal
- **From**: `http://35.200.202.18:5000/login`
- **To**: `https://handover.lab.epam.com/login`

## 🔧 Prerequisites

### 1. Network Infrastructure
- **NAT Gateway/Load Balancer** with public IP
- **DNS Control** for `lab.epam.com` domain
- **Firewall Rules** allowing ports 80 and 443

### 2. Application Server
- **Server**: 35.200.202.18 (your current GCP instance)
- **Application**: Running on port 5000
- **Docker**: With nginx reverse proxy capability

## 🌐 Step-by-Step Setup

### Step 1: DNS Configuration

Configure DNS record for `handover.lab.epam.com`:

```dns
Type: A
Name: handover.lab.epam.com
Value: [NAT_GATEWAY_PUBLIC_IP]  # Your NAT gateway's public IP
TTL: 300
```

**Note**: Replace `[NAT_GATEWAY_PUBLIC_IP]` with your actual NAT gateway's public IP address.

### Step 2: NAT Gateway Configuration

Configure your NAT gateway to forward traffic:

#### For AWS ALB/NLB:
```yaml
Target Groups:
  - Protocol: HTTP
    Port: 80
    Target: 35.200.202.18:80
  - Protocol: HTTPS  
    Port: 443
    Target: 35.200.202.18:443

Health Check:
  - Path: /health
  - Protocol: HTTP
  - Port: 80
  - Interval: 30s
```

#### For Google Cloud Load Balancer:
```yaml
Backend Services:
  - Name: handover-backend
    Protocol: HTTP
    Port: 80
    Instance: 35.200.202.18
    
  - Name: handover-backend-ssl
    Protocol: HTTPS
    Port: 443
    Instance: 35.200.202.18

Health Check:
  - Request path: /health
  - Port: 80
```

#### For HAProxy (if using custom NAT):
```haproxy
frontend handover_frontend
    bind *:80
    bind *:443 ssl crt /path/to/certificate.pem
    redirect scheme https if !{ ssl_fc }
    default_backend handover_backend

backend handover_backend
    balance roundrobin
    option httpchk GET /health
    server app1 35.200.202.18:80 check
    server app1-ssl 35.200.202.18:443 check ssl verify none
```

### Step 3: Application Configuration

Run the EPAM Lab setup on your application server (35.200.202.18):

```powershell
# Copy setup files to your server
# Then run:
.\setup-epam-lab.ps1 -Email your-email@epam.com
```

### Step 4: SSL Certificate Setup

The setup script will automatically obtain SSL certificates. For NAT environments, you might need to:

#### Option A: Let's Encrypt (Recommended)
```powershell
# The setup script handles this automatically
# Certificates will be obtained for handover.lab.epam.com
```

#### Option B: Corporate Certificate
If EPAM provides corporate certificates:
```powershell
# Place certificates in:
# - certbot_conf/live/handover.lab.epam.com/fullchain.pem
# - certbot_conf/live/handover.lab.epam.com/privkey.pem
```

### Step 5: Firewall Configuration

Ensure these ports are open:

#### On NAT Gateway:
- **Port 80** (HTTP) → Forward to 35.200.202.18:80
- **Port 443** (HTTPS) → Forward to 35.200.202.18:443

#### On Application Server (35.200.202.18):
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Keep existing port 5000 for local access
sudo ufw allow 5000/tcp
```

## 🚀 Quick Setup Commands

### On Your Local Machine:
```powershell
# Test the setup first
.\setup-epam-lab.ps1 -TestMode

# Run actual setup
.\setup-epam-lab.ps1 -Email your-email@epam.com

# Monitor the application
.\monitor-epam-lab.ps1
```

### Verification Commands:
```powershell
# Test DNS resolution
nslookup handover.lab.epam.com

# Test HTTP access
curl http://handover.lab.epam.com/health

# Test HTTPS access
curl https://handover.lab.epam.com/health

# Check application status
docker-compose -f docker-compose.prod.yml ps
```

## 🔍 Troubleshooting

### Common Issues:

#### 1. DNS Not Resolving
```powershell
# Check DNS
nslookup handover.lab.epam.com
# Should return your NAT gateway IP
```

#### 2. NAT Not Forwarding
```bash
# On application server, check if traffic is reaching
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

#### 3. SSL Certificate Issues
```powershell
# Check certificate status
docker run --rm -v ${PWD}/certbot_conf:/etc/letsencrypt certbot/certbot certificates

# Test SSL manually
openssl s_client -connect handover.lab.epam.com:443
```

#### 4. Application Not Starting
```powershell
# Check logs
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs nginx
```

## 📊 Monitoring and Maintenance

### Health Monitoring:
```powershell
# Application health
Invoke-WebRequest https://handover.lab.epam.com/health

# Service status
docker-compose -f docker-compose.prod.yml ps

# View logs
.\monitor-epam-lab.ps1
```

### Log Files:
- **Application**: `docker-compose logs web`
- **Nginx**: `docker-compose logs nginx`
- **Access logs**: Stored in nginx container at `/var/log/nginx/`

### Performance Metrics:
- **Response time**: Monitor `/health` endpoint
- **Error rate**: Check nginx error logs
- **Resource usage**: `docker stats`

## 🔒 Security Considerations

### EPAM Security Standards:
1. **SSL/TLS encryption** (enforced)
2. **Security headers** (implemented)
3. **Rate limiting** (configured)
4. **Access logging** (enabled)
5. **Regular certificate renewal** (automated)

### Additional Security:
```nginx
# Already included in configuration:
- Strict-Transport-Security
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Content Security Policy
```

## 📁 File Structure

After setup, your structure will be:
```
├── .env.epam-lab              # EPAM Lab configuration
├── .env.domain                # Active domain configuration  
├── nginx/conf.d/
│   ├── epam-lab.conf         # EPAM specific nginx config
│   └── app.conf              # Active nginx configuration
├── certbot_conf/             # SSL certificates
├── certbot_www/              # Let's Encrypt challenges
├── setup-epam-lab.ps1        # Setup script
└── monitor-epam-lab.ps1      # Monitoring script
```

## 🎯 Expected Results

After successful setup:

### URLs:
- **Production**: `https://handover.lab.epam.com`
- **Login**: `https://handover.lab.epam.com/login`
- **Health Check**: `https://handover.lab.epam.com/health`

### Traffic Flow:
```
User Request → NAT Gateway → 35.200.202.18:80/443 → Nginx → Flask App:5000
```

### Security:
- **SSL/TLS encryption** end-to-end
- **EPAM security headers** applied
- **Rate limiting** for protection
- **Access logging** for monitoring

## 📞 Support

For EPAM Lab specific issues:
1. **Check NAT gateway configuration**
2. **Verify DNS propagation** (can take 5-15 minutes)
3. **Test direct server access**: `http://35.200.202.18:5000`
4. **Review logs**: `.\monitor-epam-lab.ps1`

## 🔄 Maintenance Tasks

### Daily:
- Monitor application health: `https://handover.lab.epam.com/health`

### Weekly:
- Check certificate expiration: `.\monitor-epam-lab.ps1`
- Review access logs for unusual activity

### Monthly:
- Update Docker images: `docker-compose pull && docker-compose up -d`
- Backup application data and configuration

---

**Ready to proceed?** Run `.\setup-epam-lab.ps1` to begin the EPAM Lab domain setup!