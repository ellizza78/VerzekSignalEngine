# 🚀 One-Line Fix for Vultr Deployment

The signal_engine files exist in GitHub but aren't showing up on Vultr after git pull.

## Run This Single Command on Vultr:

```bash
cd /root/workspace && git reset --hard origin/main && git clean -fdx && ls -la signal_engine/ && cd signal_engine && chmod +x deploy.sh && sudo ./deploy.sh
```

This will:
1. Force reset to match GitHub exactly
2. Clean any untracked files
3. List signal_engine contents (verify files exist)
4. Change to signal_engine directory
5. Run deployment

---

## Expected Output:

After `ls -la signal_engine/` you should see:
```
drwxr-xr-x bots/
drwxr-xr-x common/
drwxr-xr-x config/
-rwxr-xr-x deploy.sh
drwxr-xr-x engine/
-rw-r--r-- main.py
-rw-r--r-- requirements.txt
drwxr-xr-x services/
drwxr-xr-x systemd/
```

Then deployment will start automatically!

---

## If Files Still Don't Appear:

The repository might not have been pushed correctly. Run on **Replit**:

```bash
git add signal_engine/
git commit -m "Ensure signal_engine tracked"
git push origin main
```

Then retry the Vultr command above.
