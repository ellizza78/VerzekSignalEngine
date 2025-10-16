"""
Security Audit Logging System
Comprehensive logging of all security-relevant events
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class AuditEventType(Enum):
    """Types of audit events"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    MFA_ENROLLED = "mfa_enrolled"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFIED = "mfa_verified"
    MFA_FAILED = "mfa_failed"
    
    API_KEY_ADDED = "api_key_added"
    API_KEY_REMOVED = "api_key_removed"
    API_KEY_USED = "api_key_used"
    
    PAYMENT_CREATED = "payment_created"
    PAYMENT_VERIFIED = "payment_verified"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_REJECTED = "payment_rejected"
    
    PAYOUT_REQUESTED = "payout_requested"
    PAYOUT_APPROVED = "payout_approved"
    
    TRADE_EXECUTED = "trade_executed"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    
    KILL_SWITCH_ACTIVATED = "kill_switch_activated"
    TRADING_PAUSED = "trading_paused"
    TRADING_RESUMED = "trading_resumed"
    
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    ADMIN_ACTION = "admin_action"


class AuditLogger:
    """
    Centralized audit logging for security events
    """
    
    def __init__(self):
        self.audit_file = "database/security_audit.jsonl"  # JSONL format
        self.alerts_file = "database/security_alerts.json"
        
        os.makedirs(os.path.dirname(self.audit_file), exist_ok=True)
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict] = None,
        severity: str = "info"
    ):
        """
        Log a security audit event
        
        Args:
            event_type: Type of event from AuditEventType enum
            user_id: User ID (if applicable)
            ip_address: IP address of request
            details: Additional event details
            severity: info, warning, critical
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {},
            'severity': severity
        }
        
        # Append to JSONL file (one JSON per line)
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
        
        # If critical, also add to alerts
        if severity == 'critical':
            self._create_alert(audit_entry)
    
    def _create_alert(self, audit_entry: Dict):
        """Create security alert for critical events"""
        alerts = []
        
        if os.path.exists(self.alerts_file):
            with open(self.alerts_file, 'r') as f:
                alerts = json.load(f)
        
        alert = {
            **audit_entry,
            'alert_id': f"ALERT_{int(datetime.now().timestamp())}",
            'resolved': False
        }
        
        alerts.append(alert)
        
        # Keep only last 100 alerts
        alerts = alerts[-100:]
        
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get recent activity for a user"""
        events = []
        
        if not os.path.exists(self.audit_file):
            return events
        
        with open(self.audit_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get('user_id') == user_id:
                        events.append(entry)
                        if len(events) >= limit:
                            break
                except json.JSONDecodeError:
                    continue
        
        return list(reversed(events[-limit:]))
    
    def get_events_by_type(
        self,
        event_type: AuditEventType,
        start_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get events of a specific type"""
        events = []
        
        if not os.path.exists(self.audit_file):
            return events
        
        with open(self.audit_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    if entry.get('event_type') != event_type.value:
                        continue
                    
                    if start_date and entry.get('timestamp', '') < start_date:
                        continue
                    
                    events.append(entry)
                    
                    if len(events) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        return list(reversed(events[-limit:]))
    
    def get_suspicious_activity(self, limit: int = 20) -> List[Dict]:
        """Get recent suspicious activity"""
        suspicious_types = [
            AuditEventType.LOGIN_FAILED,
            AuditEventType.MFA_FAILED,
            AuditEventType.RATE_LIMIT_EXCEEDED,
            AuditEventType.UNAUTHORIZED_ACCESS,
            AuditEventType.SUSPICIOUS_ACTIVITY
        ]
        
        events = []
        
        if not os.path.exists(self.audit_file):
            return events
        
        with open(self.audit_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    if any(entry.get('event_type') == t.value for t in suspicious_types):
                        events.append(entry)
                        
                        if len(events) >= limit:
                            break
                            
                except json.JSONDecodeError:
                    continue
        
        return list(reversed(events[-limit:]))
    
    def get_alerts(self, resolved: Optional[bool] = None) -> List[Dict]:
        """Get security alerts"""
        if not os.path.exists(self.alerts_file):
            return []
        
        with open(self.alerts_file, 'r') as f:
            alerts = json.load(f)
        
        if resolved is not None:
            alerts = [a for a in alerts if a.get('resolved') == resolved]
        
        return alerts
    
    def resolve_alert(self, alert_id: str):
        """Mark alert as resolved"""
        if not os.path.exists(self.alerts_file):
            return
        
        with open(self.alerts_file, 'r') as f:
            alerts = json.load(f)
        
        for alert in alerts:
            if alert.get('alert_id') == alert_id:
                alert['resolved'] = True
                alert['resolved_at'] = datetime.now().isoformat()
        
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)


# Global audit logger instance
audit_logger = AuditLogger()
