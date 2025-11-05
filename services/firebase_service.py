"""
Firebase Admin SDK Service
--------------------------
Handles Firebase Realtime Database connections for push notifications,
real-time updates, and logging.
"""

import os
import firebase_admin
from firebase_admin import credentials, db
from utils.logger import log_event

class FirebaseService:
    """Firebase Realtime Database service"""
    
    def __init__(self):
        self.initialized = False
        self.database_url = "https://verzekautotrader-default-rtdb.firebaseio.com/"
        
    def initialize(self, service_account_path="/root/firebase_key.json"):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                # Check if service account file exists
                if not os.path.exists(service_account_path):
                    log_event("WARNING", f"Firebase service account not found at {service_account_path}")
                    return False
                
                # Initialize Firebase
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    "databaseURL": self.database_url
                })
                
                self.initialized = True
                log_event("INFO", f"✅ Firebase initialized successfully: {self.database_url}")
                return True
            else:
                self.initialized = True
                log_event("INFO", "Firebase already initialized")
                return True
                
        except Exception as e:
            log_event("ERROR", f"Firebase initialization failed: {e}")
            return False
    
    def push_log(self, log_type, message, user_id=None):
        """Push a log entry to Firebase"""
        if not self.initialized:
            return False
            
        try:
            import time
            ref = db.reference(f"/logs/{log_type}")
            ref.push({
                "message": message,
                "user_id": user_id,
                "timestamp": int(time.time() * 1000)  # Unix timestamp in milliseconds
            })
            return True
        except Exception as e:
            log_event("ERROR", f"Failed to push Firebase log: {e}")
            return False
    
    def push_notification(self, user_id, notification_data):
        """Push a notification to a specific user"""
        if not self.initialized:
            return False
            
        try:
            ref = db.reference(f"/notifications/{user_id}")
            ref.push(notification_data)
            return True
        except Exception as e:
            log_event("ERROR", f"Failed to push notification: {e}")
            return False
    
    def update_user_status(self, user_id, status_data):
        """Update user status in realtime"""
        if not self.initialized:
            return False
            
        try:
            ref = db.reference(f"/users/{user_id}/status")
            ref.update(status_data)
            return True
        except Exception as e:
            log_event("ERROR", f"Failed to update user status: {e}")
            return False
    
    def get_reference(self, path):
        """Get a Firebase database reference"""
        if not self.initialized:
            return None
        return db.reference(path)

# Global instance
firebase_service = FirebaseService()
