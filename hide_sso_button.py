# Hide SSO button until EPAM OAuth is fixed
import re

with open('templates/login.html', 'r') as f:
    content = f.read()

# Add CSS to hide SSO section
css_hide = '''
    <style>
        .sso-providers { display: none !important; }
        .sso-divider { display: none !important; }
    </style>
'''

# Insert CSS before closing head tag
content = content.replace('</head>', css_hide + '</head>')

with open('templates/login.html', 'w') as f:
    f.write(content)

print('✅ SSO section hidden via CSS due to EPAM OAuth server issues')