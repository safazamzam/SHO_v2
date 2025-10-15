"""
SSO Authentication Routes
Handles Single Sign-On authentication flows for multiple providers
"""

from flask import Blueprint, request, redirect, url_for, flash, session, render_template, current_app
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse, urljoin
import requests
from datetime import datetime
from models.models import db, User, Account, Team
from models.sso_config import SSOConfig
# Remove audit import for now - will use Flask logging instead
import xml.etree.ElementTree as ET
import base64
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import hashlib
import secrets

sso_auth = Blueprint('sso_auth', __name__, url_prefix='/auth/sso')

@sso_auth.route('/initiate/<provider>')
def initiate_sso(provider):
    """Initiate SSO login for specified provider"""
    try:
        # Get account context if specified
        account_id = request.args.get('account_id')
        
        # Handle Google provider specifically
        if provider == 'oauth' and request.args.get('provider') == 'google':
            provider = 'google_oauth'
        
        # Check if provider is enabled
        if not SSOConfig.is_provider_enabled(provider, account_id):
            flash(f'SSO provider {provider} is not enabled', 'error')
            return redirect(url_for('auth.login'))
        
        # Get provider configuration
        config = SSOConfig.get_provider_config(provider, account_id)
        
        if provider == 'saml':
            return _initiate_saml_login(config, account_id)
        elif provider == 'azure_ad':
            return _initiate_azure_ad_login(config, account_id)
        elif provider in ['oauth', 'google_oauth']:
            return _initiate_oauth_login(config, account_id)
        else:
            flash(f'Unknown SSO provider: {provider}', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        current_app.logger.error(f"SSO initiation error for {provider}: {str(e)}")
        flash('SSO authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@sso_auth.route('/callback/<provider>', methods=['GET', 'POST'])
def sso_callback(provider):
    """Handle SSO callback from provider"""
    try:
        account_id = session.get('sso_account_id')
        
        # Handle Google OAuth callback
        if provider == 'oauth' and session.get('oauth_provider') == 'google':
            provider = 'google_oauth'
        
        if provider == 'saml':
            return _handle_saml_callback(account_id)
        elif provider == 'azure_ad':
            return _handle_azure_ad_callback(account_id)
        elif provider in ['oauth', 'google_oauth']:
            return _handle_oauth_callback(account_id)
        else:
            flash(f'Unknown SSO provider: {provider}', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        current_app.logger.error(f"SSO callback error for {provider}: {str(e)}")
        flash('SSO authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

def _initiate_saml_login(config, account_id):
    """Initiate SAML 2.0 login"""
    # Store account context in session
    session['sso_account_id'] = account_id
    
    # Generate SAML request
    request_id = secrets.token_hex(16)
    session['saml_request_id'] = request_id
    
    saml_request = f"""
    <samlp:AuthnRequest
        xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
        ID="{request_id}"
        Version="2.0"
        IssueInstant="{datetime.utcnow().isoformat()}Z"
        AssertionConsumerServiceURL="{config.get('acs_url')}"
        Destination="{config.get('sso_url')}">
        <saml:Issuer>{config.get('entity_id')}</saml:Issuer>
    </samlp:AuthnRequest>
    """
    
    # Encode and redirect
    encoded_request = base64.b64encode(saml_request.encode()).decode()
    redirect_url = f"{config.get('sso_url')}?SAMLRequest={encoded_request}"
    
    return redirect(redirect_url)

def _initiate_azure_ad_login(config, account_id):
    """Initiate Azure AD OAuth login"""
    session['sso_account_id'] = account_id
    
    # Generate state parameter for security
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    
    # Build authorization URL
    params = {
        'client_id': config.get('client_id'),
        'response_type': 'code',
        'redirect_uri': config.get('redirect_uri'),
        'response_mode': 'query',
        'scope': 'openid profile email',
        'state': state
    }
    
    auth_url = config.get('auth_endpoint')
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    redirect_url = f"{auth_url}?{query_string}"
    
    return redirect(redirect_url)

def _initiate_oauth_login(config, account_id):
    """Initiate generic OAuth 2.0 login"""
    session['sso_account_id'] = account_id
    
    # Store provider type for callback handling
    if 'accounts.google.com' in config.get('authorization_endpoint', ''):
        session['oauth_provider'] = 'google'
    
    # Generate state parameter
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    
    # Build authorization URL
    params = {
        'client_id': config.get('client_id'),
        'response_type': 'code',
        'redirect_uri': config.get('redirect_uri'),
        'scope': config.get('scope', 'openid profile email'),
        'state': state
    }
    
    auth_url = config.get('authorization_endpoint')
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    redirect_url = f"{auth_url}?{query_string}"
    
    return redirect(redirect_url)

def _handle_saml_callback(account_id):
    """Handle SAML assertion callback"""
    saml_response = request.form.get('SAMLResponse')
    if not saml_response:
        flash('Invalid SAML response', 'error')
        return redirect(url_for('auth.login'))
    
    # Decode and parse SAML response
    decoded_response = base64.b64decode(saml_response).decode()
    root = ET.fromstring(decoded_response)
    
    # Extract user attributes (simplified - in production, validate signature!)
    attributes = {}
    for attribute in root.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        name = attribute.get('Name')
        value = attribute.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue').text
        attributes[name] = value
    
    # Map SAML attributes to user data
    user_data = {
        'email': attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'),
        'first_name': attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname'),
        'last_name': attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'),
        'username': attributes.get('http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name')
    }
    
    return _process_sso_user(user_data, 'saml', account_id)

def _handle_azure_ad_callback(account_id):
    """Handle Azure AD OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verify state parameter
    if state != session.get('oauth_state'):
        flash('Invalid OAuth state', 'error')
        return redirect(url_for('auth.login'))
    
    # Get provider configuration
    config = SSOConfig.get_provider_config('azure_ad', account_id)
    
    # Exchange code for token
    token_data = {
        'client_id': config.get('client_id'),
        'client_secret': config.get('client_secret'),
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': config.get('redirect_uri')
    }
    
    token_response = requests.post(config.get('token_endpoint'), data=token_data)
    token_json = token_response.json()
    
    if 'access_token' not in token_json:
        flash('Failed to obtain access token', 'error')
        return redirect(url_for('auth.login'))
    
    # Get user info
    headers = {'Authorization': f"Bearer {token_json['access_token']}"}
    user_response = requests.get(config.get('userinfo_endpoint'), headers=headers)
    user_data = user_response.json()
    
    return _process_sso_user(user_data, 'azure_ad', account_id)

def _handle_oauth_callback(account_id):
    """Handle generic OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verify state parameter
    if state != session.get('oauth_state'):
        flash('Invalid OAuth state', 'error')
        return redirect(url_for('auth.login'))
    
    # Get provider configuration
    config = SSOConfig.get_provider_config('oauth', account_id)
    
    # Exchange code for token
    token_data = {
        'client_id': config.get('client_id'),
        'client_secret': config.get('client_secret'),
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': config.get('redirect_uri')
    }
    
    token_response = requests.post(config.get('token_endpoint'), data=token_data)
    token_json = token_response.json()
    
    if 'access_token' not in token_json:
        flash('Failed to obtain access token', 'error')
        return redirect(url_for('auth.login'))
    
    # Get user info
    headers = {'Authorization': f"Bearer {token_json['access_token']}"}
    user_response = requests.get(config.get('userinfo_endpoint'), headers=headers)
    user_data = user_response.json()
    
    return _process_sso_user(user_data, 'oauth', account_id)

def _process_sso_user(user_data, provider_type, account_id):
    """Process SSO user data and create/login user"""
    try:
        # Extract email (primary identifier)
        email = user_data.get('email') or user_data.get('mail') or user_data.get('preferred_username')
        if not email:
            flash('No email found in SSO response', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Auto-provision user if enabled
            config = SSOConfig.get_provider_config(provider_type, account_id)
            if config.get('auto_provision') == 'true':
                user = _create_sso_user(user_data, provider_type, account_id)
            else:
                flash('User not found and auto-provisioning is disabled', 'error')
                return redirect(url_for('auth.login'))
        
        # Update user info from SSO
        _update_user_from_sso(user, user_data)
        
        # Log the user in
        login_user(user)
        
        # Log SSO authentication
        current_app.logger.info(f'SSO login successful for user {user.email} via {provider_type}')
        
        # Handle account/team selection for multi-tenant users
        if user.role in ['account_admin', 'team_admin', 'user']:
            return _handle_account_team_selection(user, account_id)
        
        # Direct redirect for super_admin
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.dashboard')
        
        return redirect(next_page)
        
    except Exception as e:
        current_app.logger.error(f"SSO user processing error: {str(e)}")
        flash('SSO authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

def _create_sso_user(user_data, provider_type, account_id):
    """Create new user from SSO data"""
    email = user_data.get('email') or user_data.get('mail') or user_data.get('preferred_username')
    
    # Extract name components
    first_name = user_data.get('first_name') or user_data.get('given_name') or user_data.get('givenName', '')
    last_name = user_data.get('last_name') or user_data.get('family_name') or user_data.get('surname', '')
    
    # Generate username from email if not provided
    username = user_data.get('username') or user_data.get('preferred_username') or email.split('@')[0]
    
    # Determine default role
    config = SSOConfig.get_provider_config(provider_type, account_id)
    default_role = config.get('default_role', 'user')
    
    # Create user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=default_role,
        account_id=account_id if default_role in ['account_admin', 'team_admin', 'user'] else None,
        team_id=None,  # Will be set during team selection
        is_active=True,
        password_hash='',  # SSO users don't have local passwords
        sso_provider=provider_type
    )
    
    db.session.add(user)
    db.session.commit()
    
    current_app.logger.info(f"Created new SSO user: {email} via {provider_type}")
    return user

def _update_user_from_sso(user, user_data):
    """Update existing user with fresh SSO data"""
    # Update names if provided
    if user_data.get('first_name') or user_data.get('given_name') or user_data.get('givenName'):
        user.first_name = user_data.get('first_name') or user_data.get('given_name') or user_data.get('givenName')
    
    if user_data.get('last_name') or user_data.get('family_name') or user_data.get('surname'):
        user.last_name = user_data.get('last_name') or user_data.get('family_name') or user_data.get('surname')
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    
    db.session.commit()

def _handle_account_team_selection(user, account_id):
    """Handle account and team selection for multi-tenant SSO users"""
    # If account_id was specified in SSO initiation, use it
    if account_id and user.role in ['account_admin', 'team_admin', 'user']:
        account = Account.query.get(account_id)
        if account and (user.role == 'account_admin' or user.account_id == account_id):
            session['selected_account_id'] = account_id
            
            # For team roles, redirect to team selection
            if user.role in ['team_admin', 'user']:
                return redirect(url_for('auth.select_team'))
            else:
                return redirect(url_for('dashboard.dashboard'))
    
    # Otherwise, redirect to account selection
    return redirect(url_for('auth.select_account'))

@sso_auth.route('/providers')
def list_providers():
    """List available SSO providers for account"""
    account_id = request.args.get('account_id')
    
    # Get enabled providers
    providers = db.session.query(SSOConfig.provider_type, SSOConfig.provider_name).filter_by(
        enabled=True, account_id=account_id
    ).distinct().all()
    
    return render_template('auth/sso_providers.html', providers=providers, account_id=account_id)