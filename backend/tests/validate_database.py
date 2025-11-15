#!/usr/bin/env python3
"""
Database Schema & Integrity Validation
Validates all tables, constraints, relationships, and data integrity
NO MODIFICATIONS - Read-only validation
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from db import engine, SessionLocal
from models import (
    User, UserSettings, VerificationToken, Signal, Position,
    PositionTarget, ExchangeAccount, Payment, TradeLog
)
from datetime import datetime
import json

class DatabaseValidator:
    """Validate database schema and integrity"""
    
    def __init__(self):
        self.inspector = inspect(engine)
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
    
    def validate_table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        tables = self.inspector.get_table_names()
        exists = table_name in tables
        
        return self.log_result(
            "Schema",
            f"Table: {table_name}",
            exists,
            f"Table {'exists' if exists else 'MISSING'}",
            {"table": table_name, "exists": exists}
        )
    
    def validate_table_columns(self, table_name: str, expected_columns: list) -> bool:
        """Validate table has expected columns"""
        try:
            columns = self.inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            missing = [col for col in expected_columns if col not in column_names]
            extra = [col for col in column_names if col not in expected_columns]
            
            passed = len(missing) == 0
            
            message = f"Columns: {len(column_names)} found"
            if missing:
                message += f", MISSING: {', '.join(missing)}"
            
            return self.log_result(
                "Schema",
                f"Columns: {table_name}",
                passed,
                message,
                {"columns": column_names, "missing": missing, "extra": extra}
            )
        except Exception as e:
            return self.log_result(
                "Schema",
                f"Columns: {table_name}",
                False,
                f"Error: {str(e)}"
            )
    
    def validate_primary_keys(self, table_name: str) -> bool:
        """Validate table has primary key"""
        try:
            pk = self.inspector.get_pk_constraint(table_name)
            has_pk = len(pk.get('constrained_columns', [])) > 0
            
            return self.log_result(
                "Constraints",
                f"Primary Key: {table_name}",
                has_pk,
                f"PK: {', '.join(pk.get('constrained_columns', []))}",
                {"pk_columns": pk.get('constrained_columns', [])}
            )
        except Exception as e:
            return self.log_result(
                "Constraints",
                f"Primary Key: {table_name}",
                False,
                f"Error: {str(e)}"
            )
    
    def validate_foreign_keys(self, table_name: str, expected_fks: dict) -> bool:
        """Validate foreign key relationships"""
        try:
            fks = self.inspector.get_foreign_keys(table_name)
            
            fk_info = {}
            for fk in fks:
                local_col = fk['constrained_columns'][0]
                ref_table = fk['referred_table']
                fk_info[local_col] = ref_table
            
            all_valid = True
            for local_col, expected_table in expected_fks.items():
                if fk_info.get(local_col) != expected_table:
                    all_valid = False
            
            return self.log_result(
                "Constraints",
                f"Foreign Keys: {table_name}",
                all_valid,
                f"FK count: {len(fks)}",
                {"foreign_keys": fk_info, "expected": expected_fks}
            )
        except Exception as e:
            return self.log_result(
                "Constraints",
                f"Foreign Keys: {table_name}",
                False,
                f"Error: {str(e)}"
            )
    
    def validate_row_counts(self):
        """Validate tables have reasonable data"""
        db: Session = SessionLocal()
        try:
            counts = {
                "users": db.query(User).count(),
                "user_settings": db.query(UserSettings).count(),
                "verification_tokens": db.query(VerificationToken).count(),
                "signals": db.query(Signal).count(),
                "positions": db.query(Position).count(),
                "position_targets": db.query(PositionTarget).count(),
                "exchange_accounts": db.query(ExchangeAccount).count(),
                "payments": db.query(Payment).count(),
                "trade_logs": db.query(TradeLog).count()
            }
            
            for table, count in counts.items():
                self.log_result(
                    "Data",
                    f"Row Count: {table}",
                    True,
                    f"{count} rows",
                    {"count": count}
                )
            
            return counts
        except Exception as e:
            self.log_result(
                "Data",
                "Row Counts",
                False,
                f"Error: {str(e)}"
            )
            return {}
        finally:
            db.close()
    
    def validate_orphan_data(self):
        """Check for orphaned records (FK integrity)"""
        db: Session = SessionLocal()
        try:
            # Check for user_settings without users
            orphan_settings = db.execute(text("""
                SELECT COUNT(*) FROM user_settings 
                WHERE user_id NOT IN (SELECT id FROM users)
            """)).scalar()
            
            self.log_result(
                "Integrity",
                "Orphan user_settings",
                orphan_settings == 0,
                f"{orphan_settings} orphan records",
                {"orphan_count": orphan_settings}
            )
            
            # Check for exchange_accounts without users
            orphan_exchanges = db.execute(text("""
                SELECT COUNT(*) FROM exchange_accounts 
                WHERE user_id NOT IN (SELECT id FROM users)
            """)).scalar()
            
            self.log_result(
                "Integrity",
                "Orphan exchange_accounts",
                orphan_exchanges == 0,
                f"{orphan_exchanges} orphan records",
                {"orphan_count": orphan_exchanges}
            )
            
            # Check for positions without users
            orphan_positions = db.execute(text("""
                SELECT COUNT(*) FROM positions 
                WHERE user_id NOT IN (SELECT id FROM users)
            """)).scalar()
            
            self.log_result(
                "Integrity",
                "Orphan positions",
                orphan_positions == 0,
                f"{orphan_positions} orphan records",
                {"orphan_count": orphan_positions}
            )
            
            # Check for position_targets without positions
            orphan_targets = db.execute(text("""
                SELECT COUNT(*) FROM position_targets 
                WHERE position_id NOT IN (SELECT id FROM positions)
            """)).scalar()
            
            self.log_result(
                "Integrity",
                "Orphan position_targets",
                orphan_targets == 0,
                f"{orphan_targets} orphan records",
                {"orphan_count": orphan_targets}
            )
            
        except Exception as e:
            self.log_result(
                "Integrity",
                "Orphan Data Check",
                False,
                f"Error: {str(e)}"
            )
        finally:
            db.close()
    
    def validate_connection_pool(self):
        """Test database connection pool"""
        try:
            # Test multiple connections
            sessions = []
            for i in range(5):
                db = SessionLocal()
                result = db.execute(text("SELECT 1")).scalar()
                sessions.append(db)
            
            # Close all
            for db in sessions:
                db.close()
            
            self.log_result(
                "Connection",
                "Connection Pool",
                True,
                "Successfully created 5 concurrent connections",
                {"test_connections": 5}
            )
        except Exception as e:
            self.log_result(
                "Connection",
                "Connection Pool",
                False,
                f"Error: {str(e)}"
            )
    
    def validate_database_environment(self):
        """Validate database environment variables"""
        db_url = os.getenv("DATABASE_URL", "")
        
        has_db_url = len(db_url) > 0
        is_postgres = "postgresql" in db_url.lower()
        
        self.log_result(
            "Environment",
            "DATABASE_URL",
            has_db_url,
            f"Database URL {'set' if has_db_url else 'MISSING'}",
            {"has_url": has_db_url, "is_postgres": is_postgres}
        )
        
        if is_postgres:
            # Extract database name
            try:
                db_name = db_url.split("/")[-1].split("?")[0]
                self.log_result(
                    "Environment",
                    "Database Name",
                    True,
                    f"Using database: {db_name}",
                    {"database": db_name}
                )
            except:
                pass
    
    def run_all_validations(self):
        """Run all database validations"""
        print(f"\n{'='*70}")
        print("Database Schema & Integrity Validation")
        print(f"Started: {datetime.utcnow().isoformat()}Z")
        print(f"{'='*70}\n")
        
        # Environment
        print("\n[Environment Variables]")
        self.validate_database_environment()
        
        # Connection
        print("\n[Connection Pool]")
        self.validate_connection_pool()
        
        # Schema validation
        print("\n[Table Existence]")
        tables = [
            "users",
            "user_settings",
            "verification_tokens",
            "signals",
            "positions",
            "position_targets",
            "exchange_accounts",
            "payments",
            "trade_logs"
        ]
        
        for table in tables:
            self.validate_table_exists(table)
        
        # Primary keys
        print("\n[Primary Keys]")
        for table in tables:
            self.validate_primary_keys(table)
        
        # Foreign keys
        print("\n[Foreign Key Relationships]")
        self.validate_foreign_keys("user_settings", {"user_id": "users"})
        self.validate_foreign_keys("exchange_accounts", {"user_id": "users"})
        self.validate_foreign_keys("positions", {"user_id": "users", "signal_id": "signals"})
        self.validate_foreign_keys("position_targets", {"position_id": "positions"})
        self.validate_foreign_keys("payments", {"user_id": "users"})
        self.validate_foreign_keys("verification_tokens", {"user_id": "users"})
        
        # Row counts
        print("\n[Row Counts]")
        counts = self.validate_row_counts()
        
        # Orphan data
        print("\n[Data Integrity - Orphan Records]")
        self.validate_orphan_data()
        
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
            "row_counts": counts,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def main():
    """Main execution"""
    validator = DatabaseValidator()
    results = validator.run_all_validations()
    
    # Save results
    output_file = "database_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Full results saved to: {output_file}\n")
    
    # Exit with error if failures
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
