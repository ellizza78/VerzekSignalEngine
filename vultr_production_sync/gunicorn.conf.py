"""
Gunicorn Configuration for Verzek AutoTrader API
Production deployment settings for Vultr VPS
"""
import multiprocessing
import os

# Server Socket
bind = "127.0.0.1:8050"
backlog = 2048

# Worker Processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/verzek_api_access.log"
errorlog = "/var/log/verzek_api_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = "verzek_api"

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (handled by Nginx reverse proxy)
keyfile = None
certfile = None

# Preload application for faster worker spawn
preload_app = True

# Graceful timeout for worker restart
graceful_timeout = 30

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Gunicorn master process starting")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("🔄 Reloading workers")

def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Verzek API Server ready - Workers: {workers}, Bind: {bind}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("👋 Gunicorn shutting down")
