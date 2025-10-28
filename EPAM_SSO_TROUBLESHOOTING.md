# EPAM SSO Troubleshooting Guide for GCP VM

## Quick Manual Steps (Run on your VM)

### 1. Check Current SSO Configuration
```bash
# Connect to your VM
ssh -i ~/.ssh/my-gcp-key shifthandoversajid@35.200.202.18

# Navigate to application directory
cd ~/shift_handover_app

# Check current SSO config
docker exec shift-handover-web sqlite3 data/app.db "SELECT provider_name, config_key, config_value FROM sso_config ORDER BY provider_name, config_key;"
```

### 2. Common EPAM SSO Issues and Fixes

#### Issue 1: Wrong Redirect URI
**Problem**: Redirect URI points to localhost instead of production IP

**Check**:
```bash
docker exec shift-handover-web sqlite3 data/app.db "SELECT config_value FROM sso_config WHERE config_key='redirect_uri';"
```

**Fix**:
```bash
docker exec shift-handover-web sqlite3 data/app.db "UPDATE sso_config SET config_value='http://35.200.202.18/auth/sso/callback/oauth' WHERE config_key='redirect_uri';"
```

#### Issue 2: Client Secret Encryption Problem
**Check if client secret is encrypted**:
```bash
docker exec shift-handover-web sqlite3 data/app.db "SELECT config_value FROM sso_config WHERE config_key='client_secret';"
```

**If it starts with 'gAAAA', it's encrypted and may need manual decryption**

#### Issue 3: EPAM Keycloak Console Configuration
**Your redirect URI should be**: `http://35.200.202.18/auth/sso/callback/oauth`

**EPAM Keycloak Console Location**:
- Staging: `https://access-staging.epam.com/auth/admin/`
- Production: `https://access.epam.com/auth/admin/`

### 3. Test SSO Flow
```bash
# Check application logs for SSO attempts
docker logs shift-handover-web --tail 20 | grep -i "sso\|oauth"

# Test connectivity to EPAM
curl -I "https://access-staging.epam.com/auth/realms/plusx"
```

### 4. Required EPAM Keycloak Configuration

In your EPAM Keycloak console, verify:

1. **Client ID**: Should match what's in your database
2. **Client Secret**: Should match what's in your database  
3. **Valid Redirect URIs**: Should include `http://35.200.202.18/auth/sso/callback/oauth`
4. **Client Protocol**: Should be `openid-connect`
5. **Access Type**: Should be `confidential`

### 5. Debugging Steps

#### Check ProxyFix is Working
```bash
# Check if ProxyFix middleware is active (should see in startup logs)
docker logs shift-handover-web | grep -i "proxyfix"
```

#### Manual SSO Test
1. Go to: `http://35.200.202.18/login`
2. Click SSO login button
3. Check browser developer tools network tab
4. Should redirect to: `https://access-staging.epam.com/auth/realms/plusx/protocol/openid-connect/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://35.200.202.18/auth/sso/callback/oauth&...`

### 6. Common Error Patterns

#### "Invalid redirect URI"
- **Cause**: Redirect URI not configured in EPAM Keycloak console
- **Fix**: Add `http://35.200.202.18/auth/sso/callback/oauth` to Keycloak client

#### "Invalid client credentials"
- **Cause**: Wrong client ID or client secret
- **Fix**: Verify credentials in EPAM Keycloak console match database

#### "Connection timeout"
- **Cause**: VPN connection issues or EPAM endpoint unreachable
- **Fix**: Verify EPAM VPN connection, test endpoint connectivity

### 7. Restart Application After Changes
```bash
docker restart shift-handover-web
```

### 8. Complete Test Flow
1. Navigate to: `http://35.200.202.18/login`
2. Click SSO button
3. Redirects to EPAM Keycloak
4. Enter EPAM credentials
5. Should redirect back and log you in

## Quick Fix Commands (Copy & Paste)

```bash
# Fix redirect URI
docker exec shift-handover-web sqlite3 data/app.db "UPDATE sso_config SET config_value='http://35.200.202.18/auth/sso/callback/oauth' WHERE config_key='redirect_uri';"

# Restart application
docker restart shift-handover-web

# Check logs
docker logs shift-handover-web --tail 10

# Test endpoint
curl -s -o /dev/null -w "HTTP %{http_code}" http://35.200.202.18/health
```