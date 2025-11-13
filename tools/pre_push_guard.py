#!/usr/bin/env python3
"""
VerzekAutoTrader - Pre-Push Protection Script
Validates environment, configuration, and code quality before pushing to GitHub

Usage: python tools/pre_push_guard.py [--fix]
"""

import os
import sys
import re
import base64
import subprocess
from pathlib import Path

# Color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

class PrePushGuard:
    def __init__(self, auto_fix=False):
        self.auto_fix = auto_fix
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_failed = 0
    
    def log_success(self, message):
        print(f"{GREEN}✅ {message}{NC}")
        self.checks_passed += 1
    
    def log_error(self, message):
        print(f"{RED}❌ {message}{NC}")
        self.errors.append(message)
        self.checks_failed += 1
    
    def log_warning(self, message):
        print(f"{YELLOW}⚠️  {message}{NC}")
        self.warnings.append(message)
    
    def log_info(self, message):
        print(f"{BLUE}ℹ️  {message}{NC}")
    
    def check_required_env_vars(self):
        """Check for required environment variables"""
        print("\n🔐 Checking Required Environment Variables...")
        
        required_vars = [
            'ENCRYPTION_MASTER_KEY',
            'TELEGRAM_BOT_TOKEN',
            'RESEND_API_KEY',
            'API_BASE_URL',
            'DOMAIN'
        ]
        
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                # Check if it's in .env file (for local dev)
                if os.path.exists('backend/.env'):
                    with open('backend/.env', 'r') as f:
                        if f'"{var}="' not in f.read() and f"{var}=" not in f.read():
                            missing_vars.append(var)
                else:
                    missing_vars.append(var)
        
        if missing_vars:
            self.log_error(f"Missing environment variables: {', '.join(missing_vars)}")
            self.log_info("Check Replit Secrets or backend/.env file")
        else:
            self.log_success("All required environment variables present")
    
    def check_fernet_key(self):
        """Validate Fernet encryption key"""
        print("\n🔑 Checking Fernet Encryption Key...")
        
        key = os.getenv('ENCRYPTION_MASTER_KEY')
        if not key:
            self.log_warning("ENCRYPTION_MASTER_KEY not set (checking .env)")
            return
        
        # Fernet key should be 44 characters (32 bytes base64 encoded)
        if len(key) != 44:
            self.log_error(f"Invalid Fernet key length: {len(key)} (expected 44)")
            return
        
        # Try to decode as base64
        try:
            decoded = base64.urlsafe_b64decode(key)
            if len(decoded) == 32:
                self.log_success("Fernet encryption key is valid")
            else:
                self.log_error(f"Decoded key length invalid: {len(decoded)} bytes (expected 32)")
        except Exception as e:
            self.log_error(f"Fernet key is not valid base64: {str(e)}")
    
    def check_critical_files(self):
        """Check for critical files and directories"""
        print("\n📁 Checking Critical Files...")
        
        critical_files = [
            'backend/api_server.py',
            'backend/requirements.txt',
            'backend/models.py',
            'backend/db.py',
            'backend/utils/email.py',
            'backend/utils/security.py',
            'backend/api_version.txt',
            'mobile_app/VerzekApp/app.json',
            'mobile_app/VerzekApp/src/config/api.js',
            '.github/workflows/deploy-to-vultr.yml'
        ]
        
        missing_files = []
        
        for file_path in critical_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.log_error(f"Missing critical files: {', '.join(missing_files)}")
        else:
            self.log_success("All critical files present")
    
    def check_manifest_drift(self):
        """Check for file manifest drift"""
        print("\n📊 Checking File Manifest Drift...")
        
        manifest_file = 'backend/FILE_MANIFEST_HASHES.txt'
        
        if not os.path.exists(manifest_file):
            self.log_warning("File manifest not found (run tools/generate_manifest.sh)")
            return
        
        # Read manifest
        with open(manifest_file, 'r') as f:
            manifest_lines = [line for line in f.readlines() if line.strip() and not line.startswith('#')]
        
        manifest_count = len(manifest_lines)
        
        # Count actual files
        result = subprocess.run(
            ['bash', '-c', 'cd backend && find . -type f ! -path "*/__pycache__/*" ! -name "*.pyc" ! -path "*/.git/*" ! -path "*/instance/*" ! -path "*/verzek_*.db*" ! -path "*/logs/*" | wc -l'],
            capture_output=True,
            text=True
        )
        
        actual_count = int(result.stdout.strip())
        
        if manifest_count == actual_count:
            self.log_success(f"File manifest is up to date ({manifest_count} files)")
        else:
            self.log_warning(f"File manifest may be outdated: {manifest_count} tracked vs {actual_count} actual")
            if self.auto_fix:
                self.log_info("Regenerating manifest...")
                os.system('bash tools/generate_manifest.sh')
    
    def check_version_sync(self):
        """Check if backend and mobile versions are in sync"""
        print("\n🔄 Checking Version Sync...")
        
        try:
            result = subprocess.run(
                ['python3', 'tools/sync_versions.py'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if 'in sync' in result.stdout.lower():
                self.log_success("Backend and mobile versions are in sync")
            else:
                self.log_warning("Backend and mobile versions are OUT OF SYNC")
                self.log_info("Run: python3 tools/sync_versions.py --bump patch")
        except Exception as e:
            self.log_warning(f"Could not check version sync: {str(e)}")
    
    def check_api_url_consistency(self):
        """Check that all API URLs point to production"""
        print("\n🌐 Checking API URL Consistency...")
        
        # Check mobile app config
        api_config_file = 'mobile_app/VerzekApp/src/config/api.js'
        
        if os.path.exists(api_config_file):
            with open(api_config_file, 'r') as f:
                content = f.read()
                
                if 'localhost' in content or '10.0.2.2' in content or '127.0.0.1' in content:
                    self.log_error("Development URLs found in mobile app config!")
                else:
                    if 'https://api.verzekinnovative.com' in content:
                        self.log_success("Mobile app uses production API URL")
                    else:
                        self.log_warning("Mobile app API URL may be incorrect")
        else:
            self.log_warning(f"API config file not found: {api_config_file}")
    
    def check_git_status(self):
        """Check Git status for uncommitted changes"""
        print("\n🔍 Checking Git Status...")
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            
            uncommitted = result.stdout.strip()
            
            if uncommitted:
                lines = uncommitted.split('\n')
                self.log_warning(f"You have {len(lines)} uncommitted changes")
                self.log_info("Make sure to commit all changes before pushing")
            else:
                self.log_success("No uncommitted changes")
        except Exception as e:
            self.log_warning(f"Could not check git status: {str(e)}")
    
    def run_all_checks(self):
        """Run all protection checks"""
        print(f"\n{BLUE}{'='*60}")
        print("🛡️  VerzekAutoTrader - Pre-Push Protection")
        print(f"{'='*60}{NC}\n")
        
        self.check_required_env_vars()
        self.check_fernet_key()
        self.check_critical_files()
        self.check_manifest_drift()
        self.check_version_sync()
        self.check_api_url_consistency()
        self.check_git_status()
        
        # Summary
        print(f"\n{BLUE}{'='*60}")
        print("📊 Summary")
        print(f"{'='*60}{NC}\n")
        
        print(f"{GREEN}✅ Checks Passed: {self.checks_passed}{NC}")
        print(f"{RED}❌ Checks Failed: {self.checks_failed}{NC}")
        print(f"{YELLOW}⚠️  Warnings: {len(self.warnings)}{NC}")
        
        if self.errors:
            print(f"\n{RED}Errors that must be fixed:{NC}")
            for error in self.errors:
                print(f"  - {error}")
            print(f"\n{RED}❌ Pre-push validation FAILED{NC}")
            print("Fix the errors above before pushing to GitHub.\n")
            return False
        elif self.warnings:
            print(f"\n{YELLOW}⚠️  Warnings detected (review recommended):{NC}")
            for warning in self.warnings:
                print(f"  - {warning}")
            print(f"\n{GREEN}✅ Pre-push validation PASSED (with warnings){NC}")
            print("You may proceed with pushing to GitHub.\n")
            return True
        else:
            print(f"\n{GREEN}✅ All checks passed! Safe to push to GitHub.{NC}\n")
            return True

def main():
    """Main function"""
    auto_fix = '--fix' in sys.argv
    
    guard = PrePushGuard(auto_fix=auto_fix)
    success = guard.run_all_checks()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
