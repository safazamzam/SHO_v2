# Google OAuth 2.0 SSO Integration Guide

## Overview
This guide shows how to integrate Google OAuth 2.0 (Gmail authentication) with your Flask shift handover application using the SSO system we just implemented.

## Google Cloud Console Setup

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Navigate to "APIs & Services" → "Credentials"

### Step 2: Configure OAuth Consent Screen
1. Go to "OAuth consent screen"
2. Choose "External" (for any Gmail users) or "Internal" (for your organization only)
3. Fill required fields:
   - **App name**: "Shift Handover Application"
   - **User support email**: Your email
   - **Developer contact**: Your email
   - **Authorized domains**: Add your domain (e.g., yourdomain.com)

### Step 3: Create OAuth 2.0 Credentials
1. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
2. Application type: **Web application**
3. Name: "Shift Handover SSO"
4. **Authorized redirect URIs**: 
   ```
   http://localhost:5000/auth/sso/callback/oauth
   https://yourdomain.com/auth/sso/callback/oauth
   ```
5. Click "Create" and save the **Client ID** and **Client Secret**

## Application Configuration

### Step 1: Update Login Template
Add Google SSO button to your login page:

```html
<!-- Add this to your login template -->
<div class="sso-options mt-3">
    <h6>Or sign in with:</h6>
    <div class="d-grid gap-2">
        <a href="/auth/sso/initiate/oauth?provider=google" class="btn btn-danger">
            <i class="fab fa-google"></i> Sign in with Google
        </a>
    </div>
</div>
```

### Step 2: Configure Google OAuth in Admin Panel
1. Start your Flask application
2. Login as super_admin or account_admin
3. Navigate to `/admin/sso/`
4. Click "Configure" on the "OAuth 2.0" card
5. Fill in the Google OAuth configuration:

**Google OAuth 2.0 Configuration:**
- **Provider Name**: Google
- **Client ID**: Your Google Client ID
- **Client Secret**: Your Google Client Secret
- **Authorization Endpoint**: `https://accounts.google.com/o/oauth2/v2/auth`
- **Token Endpoint**: `https://oauth2.googleapis.com/token`
- **User Info Endpoint**: `https://www.googleapis.com/oauth2/v2/userinfo`
- **Redirect URI**: `http://localhost:5000/auth/sso/callback/oauth` (or your domain)
- **Scope**: `openid profile email`
- **Auto-provision Users**: ✅ (Enable if you want automatic user creation)
- **Default Role**: `user` (or `team_admin` based on your needs)

## User Authentication Flow

### How it Works:
1. **User clicks "Sign in with Google"**
2. **Redirected to Google OAuth** (accounts.google.com)
3. **User authorizes with Gmail account**
4. **Google redirects back** with authorization code
5. **App exchanges code for access token**
6. **App fetches user profile** (name, email, picture)
7. **User provisioned or logged in** based on email
8. **Account/Team selection** (if required by role)

### User Data Retrieved from Google:
- **Email**: Primary identifier
- **Name**: First and last name
- **Profile Picture**: Avatar URL
- **Google ID**: Unique identifier
- **Verified Email**: Email verification status

## Testing the Integration

### Step 1: Test Configuration
1. Go to `/admin/sso/`
2. Click "Test" button on OAuth 2.0 card
3. Should show "OAuth endpoints accessible"

### Step 2: Test Login Flow
1. Go to login page
2. Click "Sign in with Google"
3. Should redirect to Google OAuth
4. Login with your Gmail account
5. Should redirect back and create/login user

## Security & Privacy Features

### Data Handling
- **Minimal Data Collection**: Only email, name, and profile info
- **No Password Storage**: Users authenticate via Google
- **Token Security**: Access tokens not stored permanently
- **Audit Logging**: All Google SSO events logged

### Privacy Compliance
- **GDPR Compliant**: Users control their Google account data
- **Revocable Access**: Users can revoke access in Google account settings
- **No Email Access**: App doesn't read Gmail emails, only profile info

## Advanced Configuration

### Custom Google OAuth Settings

You can customize the OAuth flow by modifying the SSO configuration:

```python
# Enhanced Google OAuth config with additional parameters
google_config = {
    'client_id': 'your-google-client-id',
    'client_secret': 'your-google-client-secret',
    'authorization_endpoint': 'https://accounts.google.com/o/oauth2/v2/auth',
    'token_endpoint': 'https://oauth2.googleapis.com/token',
    'userinfo_endpoint': 'https://www.googleapis.com/oauth2/v2/userinfo',
    'redirect_uri': 'https://yourdomain.com/auth/sso/callback/oauth',
    'scope': 'openid profile email',
    'auto_provision': 'true',
    'default_role': 'user',
    
    # Additional Google-specific parameters
    'access_type': 'online',  # or 'offline' for refresh tokens
    'prompt': 'select_account',  # Force account selection
    'hd': 'yourdomain.com'  # Restrict to specific domain
}
```

### Domain Restriction
To restrict to specific Gmail domains (e.g., company Gmail accounts):

1. Add `hd` parameter in configuration: `"hd": "yourcompany.com"`
2. This restricts login to only emails from that domain

### Profile Picture Integration
Google provides profile pictures that you can display:

```python
# In your user model, add:
profile_picture_url = db.Column(db.String(500), nullable=True)

# In SSO callback, save the picture URL:
user.profile_picture_url = user_data.get('picture')
```

## Troubleshooting

### Common Issues:

1. **"Invalid Redirect URI"**
   - Ensure redirect URI in Google Console matches exactly
   - Check for HTTP vs HTTPS
   - Verify port numbers for localhost

2. **"Access Blocked"**
   - Complete OAuth consent screen configuration
   - Add your email as test user during development
   - Verify authorized domains

3. **"User Not Provisioned"**
   - Enable auto-provisioning in SSO config
   - Check default role assignment
   - Verify email attribute mapping

### Debug Mode:
Enable OAuth debugging:
```python
import logging
logging.getLogger('requests_oauthlib').setLevel(logging.DEBUG)
```

## Production Deployment

### Security Checklist:
- ✅ Use HTTPS in production
- ✅ Verify OAuth consent screen is approved
- ✅ Set proper authorized domains
- ✅ Use environment variables for client secrets
- ✅ Monitor failed authentication attempts
- ✅ Regular security reviews

### Google Console Production Settings:
1. **OAuth Consent Screen**: Submit for verification if using external users
2. **Authorized Domains**: Add your production domain
3. **Redirect URIs**: Use HTTPS URLs only
4. **API Quotas**: Monitor OAuth API usage

This integration provides seamless Gmail authentication while maintaining your existing multi-tenant architecture and role-based access control!