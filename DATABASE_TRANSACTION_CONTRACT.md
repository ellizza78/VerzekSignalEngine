# Database Transaction Contract
**VerzekAutoTrader - Developer Guide**

## Overview
This document defines the transaction contract for all database operations in VerzekAutoTrader. **All contributors must follow this contract** to maintain data integrity and prevent race conditions.

---

## 🔒 Core Principles

### 1. Always Use the Transaction Context Manager
```python
from modules.database import Database

db = Database()

# ✅ CORRECT: Use transaction context manager
with db.transaction() as conn:
    conn.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    # Transaction automatically commits on success, rolls back on error

# ❌ WRONG: Direct connection usage
conn = db._get_connection()
conn.execute("UPDATE users SET balance = ?", (new_balance,))  # NO RETRY, NO SAFETY
conn.commit()
```

### 2. BEGIN IMMEDIATE is Default
All transactions use `BEGIN IMMEDIATE` by default to serialize writers and prevent lock conflicts:

```python
# Default: BEGIN IMMEDIATE (recommended for all writes)
with db.transaction() as conn:
    conn.execute("INSERT INTO positions ...")

# Only for read-only operations
with db.transaction(immediate=False) as conn:
    result = conn.execute("SELECT * FROM users")
```

### 3. Automatic Retry Logic
The transaction manager automatically retries on database lock errors:
- **Max retries:** 5 attempts
- **Delay strategy:** Exponential backoff (100ms → 200ms → 400ms → 800ms → 1600ms → 3200ms)
- **Total wait time:** Up to ~6.3 seconds
- **Busy timeout:** 30 seconds (SQLite driver level)

---

## 📋 Transaction Guarantees

### What the Transaction Manager Provides:
✅ **Automatic BEGIN IMMEDIATE** - Prevents concurrent write conflicts  
✅ **Exponential backoff retry** - Handles lock contention gracefully  
✅ **Automatic rollback on error** - No partial writes  
✅ **OperationalError handling** - Catches and retries database locks  
✅ **Per-thread connections** - Thread-safe by design  
✅ **WAL mode enabled** - Better concurrent performance  

### What You Must Do:
⚠️ **Always wrap writes in transactions** - Never execute raw SQL  
⚠️ **Handle IntegrityError** - Catch unique constraint violations  
⚠️ **Catch OperationalError** - Handle retry exhaustion gracefully  
⚠️ **Log failures** - Always log when operations fail  
⚠️ **Return boolean status** - Indicate success/failure to caller  

---

## 🛠️ Implementation Examples

### Example 1: Creating a User
```python
def create_user(self, user_id: str, username: str, email: str, password_hash: str) -> bool:
    """Create a new user with retry logic"""
    try:
        # Transaction manager handles BEGIN IMMEDIATE + retry
        with self.transaction(immediate=True) as conn:
            conn.execute("""
                INSERT INTO users (user_id, username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, email, password_hash, int(time.time())))
            return True
    except sqlite3.IntegrityError:
        # Unique constraint violation (email/username exists)
        return False
    except sqlite3.OperationalError as e:
        # Retry exhausted or other database error
        print(f"Database error creating user: {e}")
        return False
```

### Example 2: Updating a Position
```python
def update_position(self, position_id: str, **updates) -> bool:
    """Update position fields with retry logic"""
    if not updates:
        return False
    
    try:
        # Serialize JSON fields
        if 'data' in updates:
            updates['data'] = json.dumps(updates['data'])
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [position_id]
        
        with self.transaction(immediate=True) as conn:
            conn.execute(f"UPDATE positions SET {set_clause} WHERE position_id = ?", values)
            return True
    except sqlite3.OperationalError as e:
        print(f"Database error updating position: {e}")
        return False
```

### Example 3: Complex Multi-Step Transaction
```python
def close_position_and_update_stats(self, position_id: str, pnl: float) -> bool:
    """Close position and update user stats atomically"""
    try:
        with self.transaction(immediate=True) as conn:
            # Step 1: Close position
            conn.execute("""
                UPDATE positions 
                SET status = 'CLOSED', closed_at = ?, pnl = ?
                WHERE position_id = ?
            """, (int(time.time()), pnl, position_id))
            
            # Step 2: Get user_id
            row = conn.execute(
                "SELECT user_id FROM positions WHERE position_id = ?", 
                (position_id,)
            ).fetchone()
            
            if not row:
                raise ValueError(f"Position {position_id} not found")
            
            user_id = row[0]
            
            # Step 3: Update user stats
            conn.execute("""
                UPDATE users 
                SET total_pnl = total_pnl + ?,
                    total_trades = total_trades + 1,
                    active_positions = active_positions - 1
                WHERE user_id = ?
            """, (pnl, user_id))
            
            # All steps commit together or rollback together
            return True
            
    except sqlite3.OperationalError as e:
        print(f"Database error closing position: {e}")
        return False
    except Exception as e:
        print(f"Error closing position: {e}")
        return False
```

---

## ⚠️ Common Pitfalls

### ❌ DON'T: Execute without transaction
```python
# DANGEROUS: No retry, no rollback, no safety
conn = db._get_connection()
conn.execute("UPDATE users SET balance = balance - 100")
conn.commit()
```

### ❌ DON'T: Ignore errors
```python
# DANGEROUS: Silent failures lose data
with db.transaction() as conn:
    conn.execute("INSERT INTO positions ...")
# What if IntegrityError? User never knows!
```

### ❌ DON'T: Use bare BEGIN
```python
# DANGEROUS: Won't serialize writers
conn.execute("BEGIN")  # Should be BEGIN IMMEDIATE
conn.execute("UPDATE positions ...")
conn.commit()
```

### ✅ DO: Use transaction manager
```python
# SAFE: Automatic retry, rollback, and error handling
try:
    with db.transaction() as conn:
        conn.execute("UPDATE users SET balance = balance - 100 WHERE user_id = ?", (user_id,))
        conn.execute("INSERT INTO transactions ...")
        return True
except sqlite3.OperationalError as e:
    logger.error(f"Database error: {e}")
    return False
```

---

## 🧪 Testing Your Database Code

### 1. Test Concurrent Writes
```python
import threading

def test_concurrent_writes():
    threads = []
    for i in range(10):
        t = threading.Thread(target=create_test_user, args=(f"user_{i}",))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # Verify all users created without errors
```

### 2. Test Retry Logic
```python
# Simulate lock contention
def test_retry():
    # Hold a lock in one thread
    with db.transaction() as conn:
        time.sleep(5)  # Hold lock
        
        # Try to write from another thread (should retry and succeed)
```

### 3. Test Rollback
```python
def test_rollback():
    try:
        with db.transaction() as conn:
            conn.execute("INSERT INTO users ...")
            raise Exception("Simulated error")
    except:
        pass
    
    # Verify user was NOT created (rolled back)
```

---

## 📊 Performance Considerations

### Connection Pooling
- Each thread gets its own connection (thread-local storage)
- Connections are reused within the same thread
- No connection pool needed (SQLite is local)

### WAL Mode Benefits
- Readers don't block writers
- Writers don't block readers
- Only writers block other writers (via BEGIN IMMEDIATE)

### When to Use `immediate=False`
```python
# Read-only queries (no writes)
with db.transaction(immediate=False) as conn:
    users = conn.execute("SELECT * FROM users").fetchall()
```

---

## 🚨 Emergency Procedures

### If Database is Locked
1. Check for long-running transactions
2. Verify no infinite loops holding locks
3. Restart affected services
4. Database will auto-recover (rollback uncommitted)

### If Retry Exhausted
```python
# After 5 retries (6.3 seconds), OperationalError is raised
# This indicates severe contention or deadlock
except sqlite3.OperationalError as e:
    logger.critical(f"Database retry exhausted: {e}")
    # Alert admin, investigate contention
```

### Database Corruption (Unlikely)
```bash
# Verify integrity
sqlite3 database/verzek.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp backups/latest_backup.db database/verzek.db
```

---

## ✅ Checklist for New Database Code

Before committing database code, verify:

- [ ] All writes wrapped in `with db.transaction():`
- [ ] `OperationalError` caught and logged
- [ ] `IntegrityError` handled appropriately
- [ ] Function returns boolean success status
- [ ] Error messages logged with context
- [ ] No direct `conn.execute()` + `conn.commit()`
- [ ] JSON fields serialized before storing
- [ ] Thread-safe (no shared state)

---

**Remember:** The database is the source of truth for user funds and positions. **Always follow this contract to prevent data loss.**

**Questions?** Review `modules/database.py` for reference implementations.
