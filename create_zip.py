import zipfile
import os
from pathlib import Path

exclude_patterns = {
    '__pycache__', '.pyc', '.git', '.upm', 'node_modules',
    '.cache', '.session', '.session-journal', '.config',
    '.pythonlibs', '.replit_pid', 'VerzekAutoTrader.zip'
}

def should_exclude(path):
    parts = Path(path).parts
    return any(pattern in parts or path.endswith(pattern) for pattern in exclude_patterns)

print("📦 Creating VerzekAutoTrader.zip...")
with zipfile.ZipFile('VerzekAutoTrader.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    count = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not should_exclude(file_path):
                arcname = file_path[2:] if file_path.startswith('./') else file_path
                try:
                    zipf.write(file_path, arcname)
                    count += 1
                    if count % 100 == 0:
                        print(f"  Added {count} files...")
                except Exception as e:
                    pass

print(f"✅ Created VerzekAutoTrader.zip with {count} files")
size_mb = os.path.getsize('VerzekAutoTrader.zip') / (1024 * 1024)
print(f"📊 Size: {size_mb:.2f} MB")
