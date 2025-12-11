#!/usr/bin/env python3
"""
USER AUDIT & RESET SCRIPT - Pro Scanner
Audits users, resets database, explains CEO/Master Admin access
"""

import os
import sys
import sqlite3
from datetime import datetime

USERS_DB = "auth_data/users.db"

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def audit_users():
    """Audit current users in database"""
    print_header("🔍 USER AUDIT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not os.path.exists(USERS_DB):
        print("❌ Database not found!")
        return False
    
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        # Count users
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        print(f"📊 Total Users: {count}\n")
        
        if count > 0:
            print("📋 USER LIST:")
            print("-" * 70)
            c.execute("""
                SELECT id, username, email, tier, active, created_date 
                FROM users 
                ORDER BY created_date DESC
            """)
            users = c.fetchall()
            
            for idx, (uid, username, email, tier, active, created) in enumerate(users, 1):
                status = "🟢 ACTIVE" if active else "🔴 BLOCKED"
                print(f"{idx}. {username:20} | {tier:10} | {status}")
                print(f"   Email: {email}")
                print(f"   ID: {uid} | Created: {created}\n")
            
            # Stats by tier
            print("\n📈 USERS BY TIER:")
            print("-" * 70)
            c.execute("SELECT tier, COUNT(*) FROM users GROUP BY tier ORDER BY tier")
            for tier, tier_count in c.fetchall():
                print(f"  {tier:12}: {tier_count} user(s)")
        
        conn.close()
        print("\n✅ AUDIT COMPLETE")
        return True
        
    except Exception as e:
        print(f"❌ Error during audit: {e}")
        return False

def reset_users():
    """Reset all users - DELETE ALL DATA"""
    print_header("⚠️  RESET ALL USERS")
    print("This will DELETE ALL registered users from the database!\n")
    
    confirm = input("⚠️  Type 'DELETE ALL USERS' to confirm: ").strip()
    
    if confirm != "DELETE ALL USERS":
        print("❌ Reset cancelled - no changes made\n")
        return False
    
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        # Get count before delete
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        
        # Delete all users
        c.execute("DELETE FROM users")
        conn.commit()
        conn.close()
        
        print(f"\n✅ DELETED {count} user(s)")
        print("✅ Database reset complete\n")
        return True
        
    except Exception as e:
        print(f"❌ Error during reset: {e}\n")
        return False

def explain_ceo_access():
    """Explain CEO/Master Admin access"""
    print_header("👑 CEO/MASTER ADMIN ACCESS")
    print("""
HOW YOU (CEO) WILL ACCESS THE SYSTEM:

1. NORMAL USERS:
   - See LOGIN and REGISTER buttons only
   - Users register themselves → get Premium access instantly
   - Can use all 7 trading tabs
   - NO admin panel visible

2. YOU (CEO/MASTER ADMIN):
   - You have DIRECT DATABASE ACCESS (local)
   - You manage users through:
     a) Direct SQLite database (users.db)
     b) Python scripts (audit_users.py, user_management.py)
   - NO ADMIN LOGIN button in the app (hidden for security)

3. TO MANAGE USERS:
   - Run: python audit_users.py audit
     → See all registered users
     → Shows user details and tier

   - Run: python audit_users.py reset
     → Delete ALL users from database
     → Confirm with 'DELETE ALL USERS'

   - Edit directly in users.db:
     → View users with SQLite browser
     → Block users (set active=0)
     → Change tiers
     → Delete specific users

4. SECURITY:
   ✅ Master password (zxc11ASD) CANNOT be used as bypass
   ✅ No admin button visible in UI (prevents confusion)
   ✅ Only you have database access
   ✅ Users cannot see other users
   ✅ All actions are logged

5. MASTER ADMIN CREDENTIALS:
   - Email: ozytargetcom@gmail.com
   - Password: zxc11ASD
   - Access: Direct database + Python scripts only

QUICK COMMANDS:
   python audit_users.py audit    → Check users
   python audit_users.py reset    → Delete all users
   python audit_users.py explain  → Show this info

SUMMARY:
✅ Users only see the trading app
✅ You manage everything from command line
✅ Clean, simple, secure!
    """)

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  PRO SCANNER - USER MANAGEMENT TOOL")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python audit_users.py audit    → Audit current users")
        print("  python audit_users.py reset    → Reset all users (DELETE ALL)")
        print("  python audit_users.py explain  → Explain CEO access\n")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "audit":
        audit_users()
    elif command == "reset":
        reset_users()
    elif command == "explain":
        explain_ceo_access()
    else:
        print(f"\n❌ Unknown command: {command}")
        print("Valid commands: audit, reset, explain\n")
