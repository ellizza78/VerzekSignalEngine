#!/usr/bin/env python3
"""
Server Environment Validation
Validates production server configuration and environment
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List

class EnvironmentValidator:
    """Validate server environment and configuration"""
    
    def __init__(self):
        self.results = []
        
    def log_result(self, category: str, test: str, passed: bool, message: str, data: dict = None):
        """Log validation result"""
        result = {
            "category": category,
            "test": test,
            "status": "PASS" if passed else "FAIL",
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.results.append(result)
        
        icon = "✅" if passed else "❌"
        print(f"{icon} [{category}] {test}: {message}")
        
        return passed
    
    def validate_required_env_vars(self):
        """Validate required environment variables"""
        print("\n[Environment Variables]")
        
        required_vars = [
            "DATABASE_URL",
            "JWT_SECRET",
            "ENCRYPTION_MASTER_KEY",
            "RESEND_API_KEY",
            "EMAIL_FROM",
            "ADMIN_EMAIL",
            "API_BASE_URL",
            "DOMAIN"
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            exists = value is not None and len(value) > 0
            
            # Show length/fingerprint for sensitive vars
            if exists:
                if "SECRET" in var or "KEY" in var or "PASSWORD" in var:
                    display = f"Set (length: {len(value)})"
                else:
                    display = f"Set: {value}"
            else:
                display = "MISSING"
            
            self.log_result(
                "Environment",
                var,
                exists,
                display,
                {"exists": exists, "length": len(value) if value else 0}
            )
    
    def validate_optional_env_vars(self):
        """Validate optional environment variables"""
        print("\n[Optional Environment Variables]")
        
        optional_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_TRIAL_CHAT_ID",
            "TELEGRAM_VIP_CHAT_ID",
            "ADMIN_CHAT_ID",
            "PYROGRAM_API_ID",
            "PYROGRAM_API_HASH"
        ]
        
        for var in optional_vars:
            value = os.getenv(var)
            exists = value is not None and len(value) > 0
            
            self.log_result(
                "Optional",
                var,
                True,  # Optional vars don't fail
                "Set" if exists else "Not set",
                {"exists": exists}
            )
    
    def validate_database_connection(self):
        """Validate database connection"""
        print("\n[Database Connection]")
        
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from db import engine
            from sqlalchemy import text
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
            
            self.log_result(
                "Database",
                "Connection Test",
                True,
                "Successfully connected to database",
                {"connected": True}
            )
            
            # Check database name
            db_url = os.getenv("DATABASE_URL", "")
            if "postgresql" in db_url:
                db_name = db_url.split("/")[-1].split("?")[0]
                self.log_result(
                    "Database",
                    "Database Name",
                    True,
                    f"Using database: {db_name}",
                    {"database": db_name}
                )
            
        except Exception as e:
            self.log_result(
                "Database",
                "Connection Test",
                False,
                f"Connection failed: {str(e)}",
                {"error": str(e)}
            )
    
    def validate_api_health(self):
        """Validate production API health"""
        print("\n[Production API Health]")
        
        api_url = os.getenv("API_BASE_URL", "https://api.verzekinnovative.com")
        
        try:
            import requests
            
            # Test /api/ping
            response = requests.get(f"{api_url}/api/ping", timeout=10)
            ping_ok = response.status_code == 200
            
            self.log_result(
                "API",
                "/api/ping",
                ping_ok,
                f"Status: {response.status_code}",
                {"status_code": response.status_code, "response": response.json()}
            )
            
            # Test /api/health
            response = requests.get(f"{api_url}/api/health", timeout=10)
            health_ok = response.status_code == 200 and response.json().get("ok") is True
            
            self.log_result(
                "API",
                "/api/health",
                health_ok,
                f"Status: {response.status_code}, OK: {response.json().get('ok')}",
                {"status_code": response.status_code, "response": response.json()}
            )
            
        except Exception as e:
            self.log_result(
                "API",
                "Health Check",
                False,
                f"API unreachable: {str(e)}",
                {"error": str(e)}
            )
    
    def validate_logging_system(self):
        """Validate logging configuration"""
        print("\n[Logging System]")
        
        # Check if logs directory exists (for local development)
        log_dir = "backend/logs"
        if os.path.exists(log_dir):
            self.log_result(
                "Logging",
                "Log Directory",
                True,
                f"Directory exists: {log_dir}",
                {"path": log_dir}
            )
        else:
            self.log_result(
                "Logging",
                "Log Directory",
                True,  # Not critical for validation
                f"Production logs at /root/api_server/logs/ (not local)",
                {"production_path": "/root/api_server/logs/"}
            )
    
    def validate_file_permissions(self):
        """Validate critical file permissions"""
        print("\n[File Permissions]")
        
        critical_files = [
            "backend/api_server.py",
            "backend/db.py",
            "backend/models.py"
        ]
        
        for filepath in critical_files:
            if os.path.exists(filepath):
                is_readable = os.access(filepath, os.R_OK)
                self.log_result(
                    "Permissions",
                    filepath,
                    is_readable,
                    "Readable" if is_readable else "NOT readable",
                    {"readable": is_readable}
                )
    
    def run_all_validations(self):
        """Run all environment validations"""
        print(f"\n{'='*70}")
        print("Server Environment Validation")
        print(f"Started: {datetime.utcnow().isoformat()}Z")
        print(f"{'='*70}\n")
        
        # Run validations
        self.validate_required_env_vars()
        self.validate_optional_env_vars()
        self.validate_database_connection()
        self.validate_api_health()
        self.validate_logging_system()
        self.validate_file_permissions()
        
        # Summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = total - passed
        
        print(f"\n{'='*70}")
        print("VALIDATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Checks: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print(f"{'='*70}\n")
        
        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "success_rate": round(passed/total*100, 2)
            },
            "checks": self.results,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def main():
    """Main execution"""
    validator = EnvironmentValidator()
    results = validator.run_all_validations()
    
    # Save results
    output_file = "environment_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Full results saved to: {output_file}\n")
    
    # Exit with error if critical failures
    critical_failures = [
        r for r in results["checks"]
        if r["status"] == "FAIL" and r["category"] in ["Environment", "Database", "API"]
    ]
    
    if critical_failures:
        print(f"⚠️  {len(critical_failures)} critical failures detected")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
