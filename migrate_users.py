#!/usr/bin/env python3
"""
Migration script to recover user data after schema changes.
This script recreates users that were lost during database schema updates.
"""

import sqlite3
import bcrypt
from datetime import datetime, timedelta
import pytz

MARKET_TIMEZONE = pytz.timezone("America/New_York")
USERS_DB = "auth_data/users.db"

# Users to restore - Add your 8 users here with their original data
USERS_TO_RESTORE = [
    # Format: (username, email, password_hash, tier, created_date, days_valid)
    # You need to provide the actual user data
    # Example:
    # ("user1", "user1@email.com", hashed_password, "Pro", "2025-11-01", 365),
]

def migrate_users():
    """Migrate and restore users to database"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        # Create backup of current table
        c.execute("ALTER TABLE users RENAME TO users_backup")
        
        # Create new table with all columns
        c.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            tier TEXT DEFAULT 'Free',
            created_date TEXT,
            expiration_date TEXT,
            daily_limit INTEGER DEFAULT 10,
            usage_today INTEGER DEFAULT 0,
            last_reset TEXT,
            active BOOLEAN DEFAULT 1,
            ip_address TEXT DEFAULT '',
            ip1 TEXT DEFAULT '',
            ip2 TEXT DEFAULT ''
        )''')
        
        # Restore users from backup
        c.execute('''INSERT INTO users 
            (username, email, password_hash, tier, created_date, expiration_date, daily_limit, active)
            SELECT username, email, password_hash, tier, created_date, expiration_date, daily_limit, active
            FROM users_backup''')
        
        conn.commit()
        
        # Verify migration
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        print(f"✅ Migration successful! Restored {count} users")
        
        # Show restored users
        c.execute("SELECT username, email, tier FROM users")
        print("\n📋 Restored users:")
        for row in c.fetchall():
            print(f"  - {row[0]} ({row[1]}) - Tier: {row[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def add_missing_users(users_list):
    """Add users that need to be manually recreated"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        for username, email, password, tier, days_valid in users_list:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Calculate dates
            created_date = datetime.now(MARKET_TIMEZONE).isoformat()
            expiration_date = (datetime.now(MARKET_TIMEZONE) + timedelta(days=days_valid)).isoformat()
            
            # Get daily limit for tier
            tier_limits = {
                "Free": 10,
                "Pro": 100,
                "Premium": 999,
                "Pending": 0
            }
            daily_limit = tier_limits.get(tier, 10)
            
            try:
                c.execute('''INSERT INTO users 
                    (username, email, password_hash, tier, created_date, expiration_date, daily_limit, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (username, email, password_hash, tier, created_date, expiration_date, daily_limit, 1))
                print(f"✅ Added user: {username}")
            except sqlite3.IntegrityError:
                print(f"⚠️ User already exists: {username}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding users: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting user migration...\n")
    
    # Step 1: Attempt to migrate from backup
    if migrate_users():
        print("\n✅ Automatic migration completed!")
    else:
        print("\n⚠️ Auto migration not available. Need manual user recovery.")
        print("\nTo restore users manually:")
        print("1. Provide the list of users with their details")
        print("2. Call add_missing_users() with user data")
        print("3. Each user: (username, email, password, tier, days_valid)")
    
    print("\nExample to add users:")
    print("""
users_to_add = [
    ("username1", "user1@email.com", "password123", "Pro", 365),
    ("username2", "user2@email.com", "password456", "Premium", 365),
]
add_missing_users(users_to_add)
    """)
