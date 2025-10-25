# Add a notice about EPAM SSO issue
import re

# Read the login template
with open('templates/login.html', 'r') as f:
    content = f.read()

# Add a notice about SSO issue
notice = '''                    <!-- SSO Notice -->
                    <div class="alert alert-warning mb-3" style="border-radius: 10px;">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        <strong>SSO Notice:</strong> EPAM SSO is currently requiring additional security compliance (OPSWAT). 
                        Please use the username/password login below or contact IT support for SSO access.
                    </div>
'''

# Insert the notice before the SSO options
if '<!-- SSO Notice -->' not in content:
    content = content.replace('<!-- SSO Options -->', notice + '                <!-- SSO Options -->')
    
    # Write back the file
    with open('templates/login.html', 'w') as f:
        f.write(content)
    
    print('✅ Added SSO notice to login template')
else:
    print('✅ SSO notice already exists')