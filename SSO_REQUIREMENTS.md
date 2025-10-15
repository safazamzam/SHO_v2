# SSO Integration Requirements

## Additional Python packages needed:
# Add these to requirements.txt

# For SAML 2.0
python3-saml==1.15.0
xmlsec==1.3.13

# For OAuth 2.0 / OpenID Connect
authlib==1.2.1
requests-oauthlib==1.3.1

# For Active Directory
python-ldap==3.4.3
ldap3==2.9.1

# For Azure AD specifically
msal==1.24.1