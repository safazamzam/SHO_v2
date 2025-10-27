# 🚀 Quick Setup Guide

## One-Command Deployment

```bash
# Clone and deploy in one go
git clone https://git.garage.epam.com/shift-handover-automation/shifthandover.git && \
cd shifthandover && \
chmod +x simple-port-mapping.sh && \
./simple-port-mapping.sh
```

## ✅ What This Does

1. **Clones the repository** from GitLab
2. **Sets up nginx reverse proxy** (Port 80 → 5000)
3. **Starts Docker Compose** with production configuration
4. **Configures health monitoring**
5. **Tests deployment** automatically

## 🌐 Access Your Application

After successful deployment:

- **Main App**: http://35.200.202.18
- **Health Check**: http://35.200.202.18/health
- **SSO Login**: http://35.200.202.18/login

## 🔍 Verify Installation

```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# Test health endpoint
curl http://35.200.202.18/health

# Should return:
{
  "services": {
    "application": "up", 
    "database": "up"
  },
  "status": "healthy"
}
```

## 🔧 Management Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop services
docker-compose -f docker-compose.prod.yml down

# Update application
git pull origin main && docker-compose -f docker-compose.prod.yml up -d --build web
```

## 🚨 Troubleshooting

If deployment fails:

```bash
# Clean nginx conflicts
./cleanup-nginx.sh

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View error logs
docker-compose -f docker-compose.prod.yml logs
```

## 📚 Full Documentation

- **Complete Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **README**: [README.md](README.md)
- **Scripts**: [scripts/README.md](scripts/README.md)

---

**🎉 That's it! Your Shift Handover Application is ready to use.**