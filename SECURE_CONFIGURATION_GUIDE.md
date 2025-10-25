# 🔐 Secure Configuration Management

This document explains how your application now uses a **hybrid security approach** with Docker secrets for critical credentials and encrypted database storage for application configurations.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Docker        │    │   Flask App      │    │   Database      │
│   Secrets       │────│   Config         │────│   Encrypted     │
│   (Critical)    │    │   Layer          │    │   Secrets       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **🔒 Security Layers:**

1. **Docker Secrets** (Highest Security)
   - Database credentials
   - Flask SECRET_KEY
   - Master encryption key
   - **Never stored in database**

2. **Encrypted Database** (Managed via UI)
   - SMTP settings
   - ServiceNow configuration
   - Application settings
   - OAuth credentials

## 🚀 **Getting Started**

### **1. Initial Setup**

```bash
# 1. Initialize database secrets (one-time setup)
python init_database_secrets.py

# 2. Verify configuration
python verify_secrets.py

# 3. Start with secure Docker Compose
docker-compose -f docker-compose.secure.yml up
```

### **2. Accessing the Secrets Management Dashboard**

- URL: `http://localhost:5000/admin/secrets`
- **Requirements:** Admin user account
- **Features:**
  - ✅ Edit SMTP configuration
  - ✅ Manage ServiceNow settings
  - ✅ Configure application settings
  - ✅ Real-time validation
  - ✅ Audit logging

## 📁 **Files Structure**

```
├── secrets/                          # Docker secrets directory
│   ├── mysql_root_password.txt       # Database root password
│   ├── mysql_user_password.txt       # Database user password
│   ├── secret_key.txt                # Flask SECRET_KEY
│   └── secrets_master_key.txt        # Master encryption key
├── docker-compose.secure.yml         # Secure Docker configuration
├── config.py                         # Updated configuration system
├── init_database_secrets.py          # Database initialization script
└── verify_secrets.py                 # Configuration verification script
```

## 🔧 **Configuration Sources (Priority Order)**

### **Critical Secrets (Docker Secrets Only):**
- `secret_key` → Flask SECRET_KEY
- `mysql_user_password` → Database password
- `secrets_master_key` → Encryption key for database secrets

### **Application Configuration (Database Storage):**
- **SMTP Settings:**
  - `smtp_server` (e.g., smtp.gmail.com)
  - `smtp_port` (e.g., 587)
  - `smtp_username` (your email)
  - `smtp_password` (app password)
  - `smtp_from` (from address)

- **ServiceNow Integration:**
  - `servicenow_instance` (instance URL)
  - `servicenow_username` (ServiceNow user)
  - `servicenow_password` (ServiceNow password)
  - `servicenow_assignment_groups` (groups to monitor)
  - `servicenow_timeout` (API timeout)
  - `servicenow_enabled` (enable/disable)

- **Application Settings:**
  - `session_timeout` (user session timeout)
  - `max_workers` (worker processes)
  - `log_level` (logging level)

## 🛠️ **Management Commands**

### **Initialize Database Secrets:**
```bash
python init_database_secrets.py
```
- Populates database with initial configuration
- Uses values from your backup .env file
- Creates encrypted storage

### **Verify Configuration:**
```bash
python verify_secrets.py
```
- Checks Docker secrets availability
- Verifies database secrets accessibility
- Reports missing configurations

### **Start Secure Application:**
```bash
# Development with Docker secrets
docker-compose -f docker-compose.secure.yml up

# Production deployment
docker-compose -f docker-compose.secure.yml up -d
```

## 🔐 **Security Features**

### **✅ What's Secured:**
- **Database credentials** → Docker secrets only
- **Flask SECRET_KEY** → Docker secrets only
- **Master encryption key** → Docker secrets only
- **All other configs** → Encrypted database with audit logs

### **✅ Security Benefits:**
- 🔒 **No plaintext credentials** in code or environment
- 🔐 **Encrypted database storage** with master key
- 📝 **Comprehensive audit logging** for all changes
- 🔑 **Role-based access control** (admin only)
- 🚫 **No .env file dependencies**

## 🎯 **Usage Examples**

### **Managing SMTP Configuration:**
```javascript
// Via Secrets Management Dashboard UI
1. Navigate to /admin/secrets
2. Click "SMTP Email" tab
3. Click "Edit Configuration"
4. Update settings
5. Click "Save Configuration"
```

### **Programmatic Access:**
```python
from models.secrets_manager import secrets_manager

# Get configuration
smtp_server = secrets_manager.get_secret('smtp_server')
smtp_port = int(secrets_manager.get_secret('smtp_port', 587))

# Set configuration
secrets_manager.set_secret('smtp_server', 'smtp.office365.com', 
                          SecretCategory.EXTERNAL, 'Office 365 SMTP')
```

## 🚨 **Security Warnings**

### **⚠️ Critical Security Notes:**

1. **Never commit secrets/ directory** to version control
2. **Backup Docker secrets securely** (master keys cannot be recovered)
3. **Rotate credentials regularly** using the management dashboard
4. **Monitor audit logs** for unauthorized access attempts
5. **Use strong passwords** for ServiceNow/SMTP accounts

### **🔒 Production Deployment:**

1. **Generate new secrets** for production:
   ```bash
   # Generate new master key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. **Set proper file permissions**:
   ```bash
   chmod 600 secrets/*
   chown root:root secrets/*
   ```

3. **Use external secret management** (AWS Secrets Manager, Azure Key Vault, etc.)

## 📊 **Monitoring & Audit**

### **Audit Logging:**
- All secret access logged to `secret_audit_log` table
- Includes user, timestamp, action, IP address
- Password changes tracked with hashed values

### **Health Checks:**
```bash
# Verify all secrets are accessible
python verify_secrets.py

# Check audit logs
SELECT * FROM secret_audit_log ORDER BY timestamp DESC LIMIT 10;
```

## 🔄 **Migration from .env**

Your application has been migrated from `.env` file to the secure system:

### **Before (Insecure):**
```bash
# .env file (plaintext, in repository)
SMTP_PASSWORD=uovrivxvitovrjcu
SERVICENOW_PASSWORD=f*X=u2QeWeP2
```

### **After (Secure):**
```bash
# Docker secrets (encrypted, external files)
/run/secrets/secrets_master_key

# Database storage (encrypted with master key)
# Managed via UI with audit logging
```

## 🆘 **Troubleshooting**

### **Common Issues:**

**1. "SECRETS_MASTER_KEY not found"**
```bash
# Check Docker secrets are mounted
ls -la /run/secrets/
# Verify file exists and is readable
cat /run/secrets/secrets_master_key
```

**2. "Database connection failed"**
```bash
# Check database password secret
cat /run/secrets/mysql_user_password
# Verify database is running
docker-compose ps
```

**3. "Configuration not loading"**
```bash
# Run verification script
python verify_secrets.py
# Check application logs
docker-compose logs web
```

### **Emergency Recovery:**

If master key is lost, you'll need to:
1. Generate new master key
2. Re-initialize database secrets
3. Reconfigure all settings via UI

---

🎉 **Your application now has enterprise-grade security with Docker secrets and encrypted database storage!**