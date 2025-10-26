# 🌐 HTTP-Only Setup Guide for handover.lab.com
# Quick setup without SSL certificates for testing domain configuration

## 🎯 Goal
Configure your application to work with `handover.lab.com` using HTTP (no SSL required)

**From**: `http://35.200.202.18:5000/login`  
**To**: `http://handover.lab.com/login`

## 🚀 Quick Setup for Your Existing Docker Compose

Since your app is already running on Docker Compose, here's the simple process:

### Step 1: Run HTTP-Only Setup Script

```bash
# Make script executable
chmod +x setup-http-only.sh

# Test first (recommended)
./setup-http-only.sh --test

# Run actual setup
./setup-http-only.sh
```

### Step 2: What the Script Does

✅ **Creates `.env.domain`** with HTTP-only configuration  
✅ **Updates nginx config** for `handover.lab.com` (no SSL)  
✅ **Restarts Docker services** with new configuration  
✅ **Sets up monitoring** with `monitor-http.sh`  
✅ **Tests local access** to verify setup  

### Step 3: Verify Local Setup

```bash
# Test local access (should work immediately)
curl http://localhost:80/health

# Check services are running
docker-compose ps

# Monitor the setup
./monitor-http.sh
```

## 🔧 Manual Setup (Alternative)

If you prefer to do it manually:

### 1. Create Environment Configuration
```bash
cat > .env.domain << EOF
DOMAIN_NAME=handover.lab.com
FLASK_ENV=production
SSL_ENABLED=false
HTTP_PORT=80
FORCE_HTTPS=false
EOF
```

### 2. Update Nginx Configuration
Replace your current nginx config with HTTP-only version:

```nginx
# HTTP server for handover.lab.com
server {
    listen 80;
    server_name handover.lab.com;
    
    # Health check
    location /health {
        proxy_pass http://web:5000/health;
        proxy_set_header Host $host;
    }
    
    # Main application
    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Restart Services
```bash
# Stop and restart with new configuration
docker-compose down
docker-compose up -d
```

## 🧪 Testing the Setup

### Local Testing (Works Immediately)
```bash
# Health check
curl http://localhost:80/health

# Login page
curl http://localhost:80/login

# Check nginx logs
docker-compose logs nginx
```

### Domain Testing (Requires Domain Mapping)
```bash
# After domain is configured by NAT team
curl http://handover.lab.com/health
curl http://handover.lab.com/login
```

## 📊 Monitoring

### Use the Created Monitoring Script
```bash
./monitor-http.sh
```

### Manual Monitoring Commands
```bash
# Service status
docker-compose ps

# Application logs
docker-compose logs -f web

# Nginx logs
docker-compose logs -f nginx

# Real-time logs
docker-compose logs -f
```

## 🌐 Domain Configuration (For NAT Team)

Your NAT team needs to configure:

```
handover.lab.com → [NAT Gateway] → 35.200.202.18:80
```

**Important**: Only port 80 is needed for HTTP-only setup.

## ✅ Success Criteria

After running the setup script, you should see:

### ✅ Services Running
```bash
$ docker-compose ps
NAME                COMMAND             SERVICE             STATUS              PORTS
app-nginx-1         nginx               nginx               running             0.0.0.0:80->80/tcp
app-web-1           python app.py       web                 running             5000/tcp
app-mysql-1         mysqld              mysql               running             3306/tcp
```

### ✅ Local Access Working
```bash
$ curl -I http://localhost:80/health
HTTP/1.1 200 OK
Server: nginx/1.21.6
X-Powered-By: EPAM-Labs-HTTP
```

### ✅ Application URLs
- **Health**: `http://handover.lab.com/health`
- **Login**: `http://handover.lab.com/login`
- **Main App**: `http://handover.lab.com`

## 🔄 Upgrade to HTTPS Later

When you're ready to add SSL certificates:

```bash
# Use the full setup script
./setup-epam-lab.sh --email your-email@epam.com
```

This will:
- Obtain SSL certificates automatically
- Configure HTTPS
- Set up HTTP → HTTPS redirects
- Update all configurations

## 🎯 What's Different from SSL Setup

**HTTP-Only Benefits:**
- ✅ No SSL certificates needed
- ✅ No domain validation required for SSL
- ✅ Faster setup and testing
- ✅ Works immediately for local testing
- ✅ Perfect for development/testing

**Limitations:**
- ⚠️ Not secure for production
- ⚠️ No encryption
- ⚠️ SSO might have issues with HTTP

## 📋 Next Steps

1. **Run setup**: `./setup-http-only.sh`
2. **Test locally**: `curl http://localhost/health`
3. **Coordinate with NAT team**: Configure `handover.lab.com` → `35.200.202.18:80`
4. **Test domain**: `curl http://handover.lab.com/health`
5. **Add SSL later**: When ready for production

## 🛠️ Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Check if ports are available
sudo netstat -tlnp | grep :80
```

### Can't Access Localhost
```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# Check if web service is running
docker-compose logs web
```

### Domain Doesn't Work
```bash
# Test local first
curl http://localhost:80/health

# Check with NAT team if domain mapping is configured
# Verify: handover.lab.com should point to your server
```

This HTTP-only setup gives you a working domain configuration that you can test immediately, even before SSL certificates and proper domain mapping are in place!