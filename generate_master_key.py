#!/usr/bin/env python3
"""
🔑 GENERATE PROPER SECRETS MASTER KEY
"""

from cryptography.fernet import Fernet

# Generate a proper Fernet key
master_key = Fernet.generate_key().decode()

print("🔑 PROPER SECRETS MASTER KEY GENERATED:")
print("=" * 60)
print(f"SECRETS_MASTER_KEY={master_key}")
print()
print("💡 How to use:")
print(f"$env:SECRETS_MASTER_KEY = \"{master_key}\"")
print()
print("⚠️ IMPORTANT: Save this key securely!")
print("   - Store in environment variables")
print("   - Keep backup in secure location")
print("   - Never commit to version control")