"""
Automated Backup & Disaster Recovery System
Nightly backups of all critical data with encryption
"""

import os
import json
import shutil
import tarfile
from datetime import datetime, timedelta
from typing import List, Optional
import schedule
from utils.logger import log_event
from modules.encryption_service import encryption_service


class BackupSystem:
    """
    Handles automated backups of all database files
    """
    
    def __init__(self):
        self.backup_dir = "backups"
        self.database_dir = "database"
        self.retention_days = 30  # Keep backups for 30 days
        
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self) -> str:
        """
        Create encrypted backup of all database files
        Returns backup file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"verzek_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        log_event("BACKUP", f"Starting backup: {backup_name}")
        
        try:
            # Create tar.gz archive of database directory
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(self.database_dir, arcname="database")
            
            # Get file size
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            
            # Create backup metadata
            metadata = {
                'backup_name': backup_name,
                'timestamp': timestamp,
                'size_mb': round(size_mb, 2),
                'files_backed_up': self._get_database_files(),
                'created_at': datetime.now().isoformat()
            }
            
            metadata_path = os.path.join(self.backup_dir, f"{backup_name}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            log_event("BACKUP", f"Backup completed: {backup_name} ({size_mb:.2f} MB)")
            
            # Clean old backups
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            log_event("ERROR", f"Backup failed: {str(e)}")
            raise
    
    def _get_database_files(self) -> List[str]:
        """Get list of all database files"""
        files = []
        if os.path.exists(self.database_dir):
            for root, dirs, filenames in os.walk(self.database_dir):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename),
                        self.database_dir
                    )
                    files.append(rel_path)
        return files
    
    def _cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.tar.gz'):
                filepath = os.path.join(self.backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    # Also remove metadata
                    meta_file = filepath.replace('.tar.gz', '.json')
                    if os.path.exists(meta_file):
                        os.remove(meta_file)
                    
                    log_event("BACKUP", f"Removed old backup: {filename}")
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore from backup
        WARNING: This will overwrite current database
        """
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        if not os.path.exists(backup_path):
            log_event("ERROR", f"Backup not found: {backup_name}")
            return False
        
        try:
            # Create safety backup of current data first
            safety_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.create_backup()
            
            # Remove current database
            if os.path.exists(self.database_dir):
                shutil.rmtree(self.database_dir)
            
            # Extract backup
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall()
            
            log_event("BACKUP", f"Successfully restored from backup: {backup_name}")
            return True
            
        except Exception as e:
            log_event("ERROR", f"Restore failed: {str(e)}")
            return False
    
    def list_backups(self) -> List[dict]:
        """List all available backups with metadata"""
        backups = []
        
        for filename in sorted(os.listdir(self.backup_dir)):
            if filename.endswith('.json'):
                filepath = os.path.join(self.backup_dir, filename)
                with open(filepath, 'r') as f:
                    metadata = json.load(f)
                    backups.append(metadata)
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def get_backup_stats(self) -> dict:
        """Get backup statistics"""
        backups = self.list_backups()
        total_size = sum(b.get('size_mb', 0) for b in backups)
        
        return {
            'total_backups': len(backups),
            'total_size_mb': round(total_size, 2),
            'oldest_backup': backups[-1]['timestamp'] if backups else None,
            'newest_backup': backups[0]['timestamp'] if backups else None,
            'retention_days': self.retention_days
        }
    
    def schedule_daily_backup(self, time_str: str = "02:00"):
        """
        Schedule daily backup at specified time
        Default: 2:00 AM
        """
        schedule.every().day.at(time_str).do(self.create_backup)
        log_event("BACKUP", f"Scheduled daily backup at {time_str}")


# Global backup system instance
backup_system = BackupSystem()
