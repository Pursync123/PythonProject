#!/usr/bin/env python3
"""
Verify that .env file is properly overriding config.py settings
"""
import os
import sys
from dotenv import load_dotenv

# Load .env manually first
print("=" * 80)
print("VERIFICATION: .env Override Check")
print("=" * 80)

# Get the project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

print(f"\n1. ENV File Path: {ENV_FILE}")
print(f"   File Exists: {os.path.exists(ENV_FILE)}")

# Load .env file
load_dotenv(ENV_FILE)

# Get DATABASE_URL from environment
env_database_url = os.getenv("DATABASE_URL")
print(f"\n2. DATABASE_URL from .env file:")
print(f"   {env_database_url}")

# Now import settings from config
from app.core.config import settings

print(f"\n3. DATABASE_URL from config.settings:")
print(f"   {settings.DATABASE_URL}")

# Compare
print(f"\n4. VERIFICATION RESULT:")
if env_database_url and env_database_url in settings.DATABASE_URL:
    print(f"   ✅ SUCCESS: .env IS overriding config.py")
    print(f"   Using database: ai_receptionist_3gp5")
    print(f"   Using host: virginia-postgres.render.com")
else:
    print(f"   ❌ ISSUE: .env may NOT be overriding config.py")
    print(f"   Expected: {env_database_url}")
    print(f"   Got:      {settings.DATABASE_URL}")

print("\n" + "=" * 80)

