import json
import os
from utils.logger import log_event

USER_DB = "database/users.json"

# --- Ensure database file exists ---
os.makedirs(os.path.dirname(USER_DB), exist_ok=True)
if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({"admins": [], "users": []}, f, indent=2)


def load_users():
    """Load all users from the database."""
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except Exception as e:
        log_event("ERROR", f"Failed to load users: {e}")
        return {"admins": [], "users": []}


def save_users(data):
    """Save updated user data."""
    try:
        with open(USER_DB, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_event("ERROR", f"Failed to save users: {e}")


def add_user(user_id, role="user"):
    """Add a user or admin."""
    data = load_users()
    if role == "admin":
        data["users"] = [u for u in data["users"] if u != user_id]  # remove if exists
        if user_id not in data["admins"]:
            data["admins"].append(user_id)
            save_users(data)
            log_event("INFO", f"🧑‍💼 Admin added: {user_id}")
    else:
        data["admins"] = [a for a in data["admins"] if a != user_id]  # remove if exists
        if user_id not in data["users"]:
            data["users"].append(user_id)
            save_users(data)
            log_event("INFO", f"👤 User added: {user_id}")


def remove_user(user_id):
    """Remove a user or admin."""
    data = load_users()
    removed = False

    for key in ["admins", "users"]:
        if user_id in data[key]:
            data[key].remove(user_id)
            removed = True

    if removed:
        save_users(data)
        log_event("INFO", f"🚫 User removed: {user_id}")
    else:
        log_event("INFO", f"⚠️ User {user_id} not found.")


def is_admin(user_id):
    """Check if a user is admin."""
    data = load_users()
    return user_id in data["admins"]


def list_users():
    """Return all users."""
    return load_users().get("users", [])


def list_admins():
    """Return all admins."""
    return load_users().get("admins", [])
