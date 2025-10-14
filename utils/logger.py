import datetime
import json
import os

LOG_FILE = "database/logs.txt"

def log_event(event_type, message):
    """Save a log message with timestamp and event type"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{event_type}] {message}\n"

    # Print to console
    print(log_entry.strip())

    # Save to file
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def log_json(data, filename="database/debug.json"):
    """Save a dictionary or list as JSON for debugging"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

