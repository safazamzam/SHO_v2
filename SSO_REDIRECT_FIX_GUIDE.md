# 🔧 SSO Redirect URI Fix Guide

## Problem

After enabling nginx reverse proxy (port mapping 80 → 5000), SSO authentication fails because:

1. **Old Redirect URI**: `http://35.200.202.18:5000/auth/sso/callback/google_oauth`
2. **New Redirect URI**: `http://35.200.202.18/auth/sso/callback/google_oauth` (no port)

## 🚀 Quick Fix

### Option 1: Automated Fix (Recommended)

```bash
# Run the automated fix script
python fix_sso_redirect_uri.py

# Restart the application
docker-compose -f docker-compose.prod.yml restart web
```

### Option 2: Manual Database Update

```sql
-- Connect to MySQL
docker-compose -f docker-compose.prod.yml exec db mysql -u root -p shift_handover

-- Check current redirect URIs
SELECT provider_type, provider_name, config_value 
FROM sso_config 
WHERE config_key = 'redirect_uri';

-- Update redirect URIs (remove :5000 port)
UPDATE sso_config 
SET config_value = REPLACE(config_value, ':5000', '') 
WHERE config_key = 'redirect_uri' AND config_value LIKE '%:5000%';

-- Verify changes
SELECT provider_type, provider_name, config_value 
FROM sso_config 
WHERE config_key = 'redirect_uri';
```

## 🔐 Google OAuth Console Update

**IMPORTANT**: You must also update the Google OAuth console with the new redirect URI.

### Steps:

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Navigate to: APIs & Services > Credentials

2. **Edit OAuth 2.0 Client**
   - Find your OAuth 2.0 Client ID
   - Click Edit

3. **Update Authorized Redirect URIs**
   - **Remove**: `http://35.200.202.18:5000/auth/sso/callback/google_oauth`
   - **Add**: `http://35.200.202.18/auth/sso/callback/google_oauth`

4. **Save Changes**

## 🧪 Testing SSO Fix

### Test the Login Flow

```bash
# 1. Test health endpoint first
curl http://35.200.202.18/health

# 2. Test login redirect
curl -I http://35.200.202.18/login

# 3. Test SSO initiation
curl -I http://35.200.202.18/auth/sso/initiate/google_oauth
```

### Manual Browser Test

1. **Open**: http://35.200.202.18/login
2. **Click**: "Sign in with Google" button
3. **Verify**: Redirects to Google OAuth (no port in URL)
4. **Complete**: OAuth flow and return to application

## 🔍 Troubleshooting

### Check Current Configuration

```bash
# Show current SSO configuration
python fix_sso_redirect_uri.py --show
```

### Common Issues

#### Issue 1: "redirect_uri_mismatch" Error
**Cause**: Google OAuth console still has old redirect URI  
**Fix**: Update Google OAuth console as described above

#### Issue 2: SSO Button Not Working
**Cause**: Application not restarted after database update  
**Fix**: 
```bash
docker-compose -f docker-compose.prod.yml restart web
```

#### Issue 3: Database Connection Error
**Cause**: MySQL container not running  
**Fix**: 
```bash
docker-compose -f docker-compose.prod.yml up -d db
```

### Debug SSO Claims

Visit the debug endpoint to see SSO claim data:
```
http://35.200.202.18/auth/sso/debug/claims
```

## 📋 Verification Checklist

- [ ] Database redirect URI updated (no :5000 port)
- [ ] Google OAuth console redirect URI updated
- [ ] Application restarted
- [ ] Health endpoint responding
- [ ] SSO login button redirects to Google
- [ ] OAuth flow completes successfully
- [ ] User profile displays correctly

## 🎯 Expected URLs After Fix

### Before (Broken)
- Login: `http://35.200.202.18:5000/login`
- Callback: `http://35.200.202.18:5000/auth/sso/callback/google_oauth`

### After (Working)
- Login: `http://35.200.202.18/login`
- Callback: `http://35.200.202.18/auth/sso/callback/google_oauth`

## 🚀 Future Domain Setup

When you set up `handover.lab.epam.com`, you'll need to:

1. **Update redirect URI again**:
   ```
   http://handover.lab.epam.com/auth/sso/callback/google_oauth
   ```

2. **Update Google OAuth console** with domain-based URI

3. **Run the fix script** again to update database

---

**💡 Pro Tip**: Always update both the database configuration AND the OAuth provider console when changing redirect URIs!