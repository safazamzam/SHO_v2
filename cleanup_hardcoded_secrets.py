#!/usr/bin/env python3
"""
🧹 CLEANUP HARDCODED SECRETS
Clean up hardcoded secrets from configuration files after migration
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Configuration files to clean
FILES_TO_CLEAN = [
    'config.py',
    'app.py',
    'app_backup.py'
]

# Patterns to replace or comment out
REPLACEMENTS = {
    # Gmail credentials
    r"'mdsajid020@gmail\.com'": "'*** MIGRATED TO DATABASE ***'",
    r'"mdsajid020@gmail\.com"': '"*** MIGRATED TO DATABASE ***"',
    r"'uovrivxvitovrjcu'": "'*** MIGRATED TO DATABASE - ROTATE IMMEDIATELY ***'",
    r'"uovrivxvitovrjcu"': '"*** MIGRATED TO DATABASE - ROTATE IMMEDIATELY ***"',
    
    # ServiceNow credentials  
    r"'dev284357\.service-now\.com'": "'*** MIGRATED TO DATABASE ***'",
    r'"dev284357\.service-now\.com"': '"*** MIGRATED TO DATABASE ***"',
    r"'admin'": "'*** MIGRATED TO DATABASE ***'",
    r'"admin"': '"*** MIGRATED TO DATABASE ***"',
    r"'f\*X=u2QeWeP2'": "'*** MIGRATED TO DATABASE - ROTATE IMMEDIATELY ***'",
    r'"f\*X=u2QeWeP2"': '"*** MIGRATED TO DATABASE - ROTATE IMMEDIATELY ***"',
    
    # Flask secret keys
    r"'supersecretkey'": "'*** MIGRATED TO DATABASE ***'",
    r'"supersecretkey"': '"*** MIGRATED TO DATABASE ***"',
    
    # SSO keys
    r"'sso_secret_key_here'": "'*** MIGRATED TO DATABASE ***'",
    r'"sso_secret_key_here"': '"*** MIGRATED TO DATABASE ***"',
}

def backup_file(file_path):
    """Create a backup of the file before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"📁 Backup created: {backup_path}")
    return backup_path

def clean_hardcoded_secrets(file_path):
    """Clean hardcoded secrets from a file"""
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return False
    
    print(f"\n🧹 Cleaning secrets from: {file_path}")
    
    # Create backup
    backup_path = backup_file(file_path)
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Apply replacements
    for pattern, replacement in REPLACEMENTS.items():
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            print(f"   ✅ Replaced pattern: {pattern}")
    
    # Write cleaned content
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ File cleaned: {file_path}")
        return True
    else:
        print(f"   ℹ️ No secrets found to clean in: {file_path}")
        return False

def main():
    print("🧹 HARDCODED SECRETS CLEANUP")
    print("=" * 50)
    
    workspace_dir = os.getcwd()
    print(f"📁 Working directory: {workspace_dir}")
    
    files_cleaned = 0
    
    for file_name in FILES_TO_CLEAN:
        file_path = os.path.join(workspace_dir, file_name)
        if clean_hardcoded_secrets(file_path):
            files_cleaned += 1
    
    print(f"\n🎉 CLEANUP COMPLETED!")
    print(f"   📊 Files processed: {len(FILES_TO_CLEAN)}")
    print(f"   ✅ Files cleaned: {files_cleaned}")
    
    print(f"\n🚨 CRITICAL NEXT STEPS:")
    print(f"   1. 🔄 ROTATE Gmail password: uovrivxvitovrjcu")
    print(f"   2. 🔄 ROTATE ServiceNow password: f*X=u2QeWeP2")
    print(f"   3. 🔐 Update rotated credentials in secrets dashboard")
    print(f"   4. ✅ Test application with new secure configuration")

if __name__ == "__main__":
    main()