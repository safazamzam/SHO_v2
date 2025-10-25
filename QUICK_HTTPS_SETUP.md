# 🚀 Quick HTTPS Setup Guide for Your Shift Handover Application

## 📋 What You Need

1. **Domain Name**: A domain that you will NAT to your server IP (e.g., `shifthandover.yourcompany.com`)
2. **Server**: Your current Windows server with Docker Desktop running
3. **NAT Configuration**: Router/firewall configured to forward ports 80 and 443 to your server
4. **Email**: Valid email for SSL certificate registration

## 🔧 Step 1: Configure Your Domain

1. **Set up NAT on your router/firewall**:
   - Forward external port 80 → your server IP:80
   - Forward external port 443 → your server IP:443

2. **DNS Configuration**:
   - Create an A record for your domain pointing to your public IP
   - Test with: `nslookup your-domain.com`

## ⚙️ Step 2: Prepare Environment Configuration

1. **Copy the environment template**:
   ```powershell
   Copy-Item .env.https.template .env.production
   ```

2. **Edit `.env.production`** with your details:
   ```env
   # REPLACE THESE WITH YOUR ACTUAL VALUES
   DOMAIN_NAME=shifthandover.yourcompany.com
   CERTBOT_EMAIL=your-email@yourcompany.com

   # Generate secure passwords
   MYSQL_PASSWORD=VerySecurePassword123!
   MYSQL_ROOT_PASSWORD=AnotherSecurePassword456!

   # Generate a secret key (run in Python):
   # import secrets; print(secrets.token_urlsafe(64))
   SECRET_KEY=your_generated_64_character_secret_key_here

   # Keep your existing SMTP settings
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=mdsajid020@gmail.com
   SMTP_PASSWORD=uovrivxvitovrjcu
   TEAM_EMAIL=mdsajid020@gmail.com

   # Application URLs
   APP_DOMAIN=shifthandover.yourcompany.com
   APP_BASE_URL=https://shifthandover.yourcompany.com

   # Security settings
   FLASK_ENV=production
   FORCE_HTTPS=true
   SECURE_HEADERS=true
   ```

## 🔑 Step 3: Generate Secure Keys

Run this in Python to generate secure keys:

```python
import secrets
from cryptography.fernet import Fernet

# Generate SECRET_KEY
print("SECRET_KEY=", secrets.token_urlsafe(64))

# Generate SECRETS_MASTER_KEY  
print("SECRETS_MASTER_KEY=", Fernet.generate_key().decode())
```

## 🌐 Step 4: Update Nginx Configuration

Update the domain in your Nginx config:

```powershell
# Replace 'your-domain.com' with your actual domain
(Get-Content nginx\conf.d\default.conf) -replace 'your-domain.com', 'shifthandover.yourcompany.com' | Set-Content nginx\conf.d\default.conf
```

## 🚀 Step 5: Deploy with HTTPS

### Option A: Quick Deployment (Windows)

```powershell
# 1. Create required directories
New-Item -ItemType Directory -Path "certbot\conf", "certbot\www", "nginx\logs", "backups", "uploads" -Force

# 2. Stop current containers
docker-compose down

# 3. Start nginx for certificate generation
docker-compose -f docker-compose.https.yml up -d nginx

# 4. Wait a moment for nginx to start
Start-Sleep -Seconds 10

# 5. Generate SSL certificate (REPLACE WITH YOUR DOMAIN AND EMAIL)
docker-compose -f docker-compose.https.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@yourcompany.com --agree-tos --no-eff-email -d shifthandover.yourcompany.com

# 6. Deploy full application with HTTPS
docker-compose -f docker-compose.https.yml build
docker-compose -f docker-compose.https.yml up -d
```

### Option B: Manual Step-by-Step

1. **Stop current development containers**:
   ```powershell
   docker-compose down
   ```

2. **Create directories**:
   ```powershell
   New-Item -ItemType Directory -Path "certbot\conf" -Force
   New-Item -ItemType Directory -Path "certbot\www" -Force
   New-Item -ItemType Directory -Path "nginx\logs" -Force
   ```

3. **Start nginx only (for certificate)**:
   ```powershell
   docker-compose -f docker-compose.https.yml up -d nginx
   ```

4. **Generate SSL certificate**:
   ```powershell
   docker-compose -f docker-compose.https.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email YOUR_EMAIL@company.com --agree-tos --no-eff-email -d YOUR_DOMAIN.com
   ```

5. **Deploy full application**:
   ```powershell
   docker-compose -f docker-compose.https.yml build
   docker-compose -f docker-compose.https.yml up -d
   ```

## ✅ Step 6: Verify Your Deployment

1. **Check if services are running**:
   ```powershell
   docker-compose -f docker-compose.https.yml ps
   ```

2. **Test your application**:
   - Main app: `https://your-domain.com`
   - Health check: `https://your-domain.com/health`
   - Admin panel: `https://your-domain.com/admin`

3. **Check SSL certificate**:
   ```powershell
   curl -I https://your-domain.com
   ```

## 📧 Step 7: Configure Email Recipients

1. Navigate to `https://your-domain.com/admin`
2. Go to "Secrets Management"
3. Click on the "Email Recipients" tab
4. Configure your handover email recipients
5. Test the email configuration

## 🔄 Step 8: Set Up Certificate Renewal

Create a PowerShell script for certificate renewal:

```powershell
# Create renew-cert.ps1
@"
# Certificate Renewal Script
cd "$(Split-Path -Parent `$MyInvocation.MyCommand.Path)"
docker-compose -f docker-compose.https.yml run --rm certbot renew
docker-compose -f docker-compose.https.yml exec nginx nginx -s reload
"@ | Out-File -FilePath "renew-cert.ps1" -Encoding UTF8
```

Set up a Windows scheduled task to run this script twice daily.

## 🛠️ Troubleshooting

### If certificate generation fails:
1. Verify your domain points to your server's public IP
2. Check that ports 80 and 443 are properly forwarded
3. Ensure nginx is running: `docker-compose -f docker-compose.https.yml ps`

### If application won't start:
1. Check logs: `docker-compose -f docker-compose.https.yml logs -f`
2. Verify your `.env.production` file has correct values
3. Make sure database passwords are properly set

### View application logs:
```powershell
docker-compose -f docker-compose.https.yml logs -f web
```

## 📋 Production Checklist

- [ ] Domain configured and pointing to server
- [ ] NAT/Port forwarding configured (80, 443)
- [ ] Environment variables configured in `.env.production`
- [ ] SSL certificate generated successfully
- [ ] Application accessible via HTTPS
- [ ] Email configuration tested
- [ ] Admin panel accessible
- [ ] Certificate renewal script created

## 🎉 Success!

Your Shift Handover Application should now be running securely with HTTPS at `https://your-domain.com`!

## 🔧 Additional Commands

```powershell
# Stop all services
docker-compose -f docker-compose.https.yml down

# Restart services
docker-compose -f docker-compose.https.yml restart

# View all logs
docker-compose -f docker-compose.https.yml logs -f

# Check certificate expiration
docker-compose -f docker-compose.https.yml run --rm certbot certificates
```

**Note**: Remember to replace all placeholder domains and emails with your actual values!