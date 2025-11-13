#!/usr/bin/env python3
"""
VerzekAutoTrader - Version Sync Utility
Synchronizes backend API version and mobile app version
Usage: python tools/sync_versions.py [--bump minor|patch|major]
"""

import os
import re
import sys
import json
import subprocess
from datetime import datetime

# File paths
BACKEND_VERSION_FILE = "backend/api_version.txt"
MOBILE_VERSION_FILE = "mobile_app/VerzekApp/app_version.txt"
MOBILE_APP_JSON = "mobile_app/VerzekApp/app.json"

def get_git_commit_hash():
    """Get short git commit hash"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"

def parse_version(version_str):
    """Parse semantic version string"""
    match = re.match(r'v?(\d+)\.(\d+)\.?(\d+)?', version_str.strip())
    if match:
        major, minor, patch = match.groups()
        return int(major), int(minor), int(patch or 0)
    return None

def format_version(major, minor, patch, include_v=True):
    """Format version as string"""
    prefix = "v" if include_v else ""
    return f"{prefix}{major}.{minor}.{patch}"

def bump_version(current_version, bump_type='patch'):
    """Bump version based on type"""
    parsed = parse_version(current_version)
    if not parsed:
        print(f"❌ Invalid version format: {current_version}")
        sys.exit(1)
    
    major, minor, patch = parsed
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        print(f"❌ Invalid bump type: {bump_type}")
        sys.exit(1)
    
    return major, minor, patch

def read_backend_version():
    """Read backend API version"""
    if not os.path.exists(BACKEND_VERSION_FILE):
        return None
    
    with open(BACKEND_VERSION_FILE, 'r') as f:
        content = f.read()
        # Extract version from content
        match = re.search(r'Version:\s*v?(\d+\.\d+\.?\d*)', content)
        if match:
            return match.group(1)
        # Try first line if format not found
        first_line = content.split('\n')[0].strip()
        return first_line.replace('Version:', '').strip()

def read_mobile_version():
    """Read mobile app version"""
    if not os.path.exists(MOBILE_APP_JSON):
        return None
    
    with open(MOBILE_APP_JSON, 'r') as f:
        data = json.load(f)
        return data.get('expo', {}).get('version', None)

def write_backend_version(version):
    """Write backend API version"""
    commit = get_git_commit_hash()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    content = f"""Version: v{version}
Build: {commit}
Updated: {timestamp}
"""
    
    with open(BACKEND_VERSION_FILE, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {BACKEND_VERSION_FILE}: v{version}")

def write_mobile_version(version):
    """Write mobile app version to both files"""
    # Update app.json
    with open(MOBILE_APP_JSON, 'r') as f:
        data = json.load(f)
    
    data['expo']['version'] = version
    data['expo']['runtimeVersion'] = version
    
    # Optionally bump Android versionCode
    if 'android' in data['expo']:
        current_code = data['expo']['android'].get('versionCode', 1)
        data['expo']['android']['versionCode'] = current_code + 1
    
    with open(MOBILE_APP_JSON, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Updated {MOBILE_APP_JSON}: {version}")
    
    # Update app_version.txt
    commit = get_git_commit_hash()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    content = f"""App Version: {version}
Build: {commit}
Updated: {timestamp}
Platform: React Native (Expo)
"""
    
    with open(MOBILE_VERSION_FILE, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {MOBILE_VERSION_FILE}: {version}")

def check_sync():
    """Check if versions are in sync"""
    backend_ver = read_backend_version()
    mobile_ver = read_mobile_version()
    
    print("🔍 Current Versions:")
    print(f"  Backend: v{backend_ver or 'NOT FOUND'}")
    print(f"  Mobile:  {mobile_ver or 'NOT FOUND'}")
    
    if backend_ver and mobile_ver:
        # Normalize for comparison
        backend_normalized = backend_ver.replace('v', '')
        mobile_normalized = mobile_ver.replace('v', '')
        
        if backend_normalized == mobile_normalized:
            print("✅ Versions are in sync!")
            return True
        else:
            print("⚠️  Versions are OUT OF SYNC")
            return False
    else:
        print("❌ Unable to read versions")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print(__doc__)
        print("\nExamples:")
        print("  python tools/sync_versions.py              # Check sync status")
        print("  python tools/sync_versions.py --bump patch # Bump patch version")
        print("  python tools/sync_versions.py --bump minor # Bump minor version")
        print("  python tools/sync_versions.py --bump major # Bump major version")
        sys.exit(0)
    
    # Check if bump requested
    bump_type = None
    if len(sys.argv) > 2 and sys.argv[1] == '--bump':
        bump_type = sys.argv[2]
        if bump_type not in ['patch', 'minor', 'major']:
            print("❌ Invalid bump type. Use: patch, minor, or major")
            sys.exit(1)
    
    if bump_type:
        # Bump version
        print(f"🚀 Bumping {bump_type} version...")
        
        # Read current backend version
        current = read_backend_version()
        if not current:
            print("❌ Cannot read current backend version")
            sys.exit(1)
        
        # Bump it
        major, minor, patch = bump_version(current, bump_type)
        new_version = f"{major}.{minor}.{patch}"
        
        print(f"📦 New version: v{new_version}")
        
        # Write to both
        write_backend_version(new_version)
        write_mobile_version(new_version)
        
        print("\n✅ Version bump complete!")
        print(f"\n💡 Next steps:")
        print(f"  1. Review changes: git diff")
        print(f"  2. Commit: git add . && git commit -m 'Bump version to v{new_version}'")
        print(f"  3. Push: git push origin main")
    else:
        # Just check sync
        check_sync()

if __name__ == '__main__':
    main()
