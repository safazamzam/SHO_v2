# 🔧 Quick Fix for Nginx Mount Error

## 🎯 Problem
The error indicates that nginx configuration files are missing or incorrectly mounted. Your docker-compose.prod.yml is trying to mount files that don't exist.

## 🚀 Quick Solution

### Option 1: Automated Fix (Recommended)
Run this PowerShell script from your Windows machine:

```powershell
.\fix-nginx-remote.ps1
```

This will:
- Transfer all necessary nginx files to your Linux host
- Run the automated setup script
- Test the configuration
- Start services with HTTP-only setup

### Option 2: Manual Fix on Linux Host

If the automated script doesn't work, SSH to your Linux host and run:

```bash
# SSH to your server
ssh -i ~/.ssh/my-gcp-key shifthandoversajid@35.200.202.18

# Navigate to app directory
cd ~/shift_handover_app

# Create nginx directory structure
mkdir -p nginx/conf.d

# Create nginx.conf
cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    sendfile on;
    keepalive_timeout 65;
    
    include /etc/nginx/conf.d/*.conf;
}
EOF

# Create app.conf for HTTP-only
cat > nginx/conf.d/app.conf << 'EOF'
upstream flask_app {
    server web:5000;
}

server {
    listen 80;
    server_name handover.lab.com localhost;
    
    location /health {
        proxy_pass http://flask_app/health;
        proxy_set_header Host $host;
    }
    
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Create environment config
cat > .env.domain << 'EOF'
DOMAIN_NAME=handover.lab.com
SSL_ENABLED=false
FLASK_ENV=production
EOF

# Stop existing services
docker-compose -f docker-compose.prod.yml down

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# Test local access
curl http://localhost/health
```

## ✅ Expected Results

After the fix:

### Services Running:
```bash
$ docker-compose -f docker-compose.prod.yml ps
NAME                COMMAND             SERVICE             STATUS              PORTS
app-nginx-1         nginx               nginx               running             0.0.0.0:80->80/tcp
app-web-1           python app.py       web                 running             5000/tcp
app-db-1            mysqld              db                  running             3306/tcp
```

### Local Access Working:
```bash
$ curl http://localhost/health
{"status": "healthy"}
```

### URLs Available:
- **Local**: `http://35.200.202.18/health` ✅
- **Domain**: `http://handover.lab.com/health` (after domain mapping)

## 🔍 Troubleshooting

### If nginx still fails to start:
```bash
# Check nginx configuration
docker run --rm -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro -v $(pwd)/nginx/conf.d:/etc/nginx/conf.d:ro nginx:alpine nginx -t

# Check file existence
ls -la nginx/
ls -la nginx/conf.d/

# Check logs
docker-compose -f docker-compose.prod.yml logs nginx
```

### If web service fails:
```bash
# Check web service logs
docker-compose -f docker-compose.prod.yml logs web

# Check database connection
docker-compose -f docker-compose.prod.yml logs db
```

### If health check fails:
```bash
# Test direct Flask app
curl http://localhost:5000/health

# Check if Flask is listening
docker-compose -f docker-compose.prod.yml exec web netstat -tlnp
```

## 📋 File Structure After Fix

```
~/shift_handover_app/
├── docker-compose.prod.yml
├── .env.domain                    # Domain configuration
├── nginx/
│   ├── nginx.conf                 # Main nginx config
│   └── conf.d/
│       └── app.conf              # HTTP-only server config
├── app.py
├── requirements.txt
└── ...
```

## 🎯 Next Steps

1. **Run the fix**: `.\fix-nginx-remote.ps1` or manual commands above
2. **Test locally**: `curl http://35.200.202.18/health`
3. **Configure domain**: Ask NAT team to map `handover.lab.com` → `35.200.202.18:80`
4. **Test domain**: `curl http://handover.lab.com/health`

The issue was simply missing nginx configuration files. Once these are created, your docker-compose.prod.yml will work perfectly with HTTP-only access to handover.lab.com!