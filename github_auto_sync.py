"""
Verzek AutoTrader → GitHub Auto-Sync (Changed files only, every 3 hours)
-----------------------------------------------------------------------
- Compares local file content to GitHub; uploads only if different.
- Skips venv/.git/__pycache__/node_modules and files > 2MB.
- Uses GitHub Contents API with SHA to update safely.
- Runs forever; interval configurable via SYNC_INTERVAL_HOURS env (default 3).
- To run once instead of looping, set SYNC_ONCE=1 in env.
"""

import os
import base64
import time
import requests
from datetime import datetime

# ==== REQUIRED: set in Replit Secrets (Tools → Secrets) ====
# GITHUB_TOKEN: your personal access token with "repo" scope
# ===========================================================

# ==== CONFIG: update repo/branch if needed ====
REPO = "ellizza78/VerzekAutoTrader"
BRANCH = "main"
EXCLUDE_DIRS = {"venv", ".git", "__pycache__", "node_modules", ".mypy_cache"}
MAX_FILE_BYTES = 2_000_000  # skip files > 2MB
SYNC_INTERVAL_HOURS = float(os.getenv("SYNC_INTERVAL_HOURS", "3"))  # default 3h
SYNC_ONCE = os.getenv("SYNC_ONCE", "0") == "1"
COMMIT_MESSAGE_PREFIX = "Auto-Sync from Replit"
# ==============================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise SystemExit("❌ Missing GITHUB_TOKEN in Secrets. Add it under Tools → Secrets.")

API_URL = f"https://api.github.com/repos/{REPO}/contents"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}


def normalize_path(p: str) -> str:
    return p.replace("\\", "/")


def should_skip_path(root: str) -> bool:
    parts = set(root.split(os.sep))
    return bool(parts & EXCLUDE_DIRS)


def get_remote_file(github_path: str):
    """Fetch file metadata/content from GitHub. Returns (status_code, json or None)."""
    url = f"{API_URL}/{github_path}?ref={BRANCH}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return 200, r.json()
        elif r.status_code == 404:
            return 404, None
        elif r.status_code == 403:
            # Likely rate limit; print headers for debug
            reset = r.headers.get("X-RateLimit-Reset")
            print(f"⚠️  Rate limited. Reset at epoch {reset}. Status: 403 for {github_path}")
            return 403, None
        else:
            print(f"⚠️  Unexpected GET {r.status_code} for {github_path}: {r.text[:200]}")
            return r.status_code, None
    except requests.RequestException as e:
        print(f"⚠️  Network error getting {github_path}: {e}")
        return 0, None


def files_equal_local_remote(local_bytes: bytes, remote_json: dict) -> bool:
    """
    Compare local bytes to remote 'content' if present.
    GitHub returns base64 with newlines; handle that. If content is missing/truncated, return False.
    """
    if not remote_json:
        return False
    content = remote_json.get("content")
    encoding = remote_json.get("encoding")
    if not content or encoding != "base64":
        # Content may be truncated or not returned (e.g., large file) → force update
        return False
    try:
        remote_b64 = content.replace("\n", "").strip()
        remote_bytes = base64.b64decode(remote_b64)
        return remote_bytes == local_bytes
    except Exception:
        return False


def upload_file(file_path: str):
    """Create or update a single file on GitHub if changed."""
    github_path = normalize_path(file_path)

    # Read local content
    try:
        with open(file_path, "rb") as f:
            local_bytes = f.read()
    except Exception as e:
        print(f"⚠️  Could not read {file_path}: {e}")
        return

    # Check remote
    status, remote = get_remote_file(github_path)
    sha = remote.get("sha") if (status == 200 and isinstance(remote, dict)) else None

    # Skip if identical
    if status == 200 and files_equal_local_remote(local_bytes, remote):
        print(f"⏭️  Unchanged, skipped: {github_path}")
        return

    # Prepare payload
    b64 = base64.b64encode(local_bytes).decode("utf-8")
    message = f"{COMMIT_MESSAGE_PREFIX} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    payload = {"message": message, "content": b64, "branch": BRANCH}
    if sha:
        payload["sha"] = sha

    # PUT to create/update
    put_url = f"{API_URL}/{github_path}"
    try:
        r = requests.put(put_url, json=payload, headers=HEADERS, timeout=60)
        if r.status_code in (200, 201):
            action = "Updated" if sha else "Created"
            print(f"✅ {action}: {github_path}")
        elif r.status_code == 409:
            print(f"⚠️  Conflict updating {github_path}. Try again later.")
        elif r.status_code == 422:
            print(f"⚠️  Unprocessable (maybe path issue) {github_path}: {r.text[:200]}")
        else:
            print(f"⚠️  Error {r.status_code} for {github_path}: {r.text[:200]}")
    except requests.RequestException as e:
        print(f"⚠️  Network error PUT {github_path}: {e}")


def run_sync_once():
    print("🚀 Starting Replit → GitHub sync (changed files only)...")
    changed = 0
    skipped = 0
    for root, _, files in os.walk("."):
        if should_skip_path(root):
            continue
        for filename in files:
            path = os.path.join(root, filename)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    print(f"⏭️  Skipped >2MB: {normalize_path(path)}")
                    skipped += 1
                    continue
            except OSError:
                continue
            upload_file(path)
    print("✅ Sync pass completed.")


def main():
    if SYNC_ONCE:
        run_sync_once()
        return

    while True:
        run_sync_once()
        sleep_secs = int(SYNC_INTERVAL_HOURS * 3600)
        print(f"⏳ Waiting {SYNC_INTERVAL_HOURS} hour(s) before next sync...")
        time.sleep(sleep_secs)


if __name__ == "__main__":
    main()