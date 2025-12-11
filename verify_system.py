#!/usr/bin/env python3
"""
System Verification Script - Tests complete flow
Verifies: User registration, authentication, session, admin management
"""

import os
import sys
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from user_management import (
    create_user, authenticate_user, create_session, 
    validate_session, deactivate_user, initialize_users_db
)

USERS_DB = "auth_data/users.db"

def test_complete_flow():
    """Test complete user flow"""
    print("\n" + "=" * 70)
    print("  SYSTEM VERIFICATION TEST - COMPLETE FLOW")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests_passed = 0
    tests_total = 0
    
    # TEST 1: Database exists
    print("TEST 1: Database Integrity")
    print("-" * 70)
    tests_total += 1
    if os.path.exists(USERS_DB):
        print("✅ Database exists")
        tests_passed += 1
    else:
        print("❌ Database missing - reinitializing...")
        initialize_users_db()
        if os.path.exists(USERS_DB):
            print("✅ Database initialized successfully")
            tests_passed += 1
        else:
            print("❌ Failed to initialize database")
    
    # TEST 2: Create test user
    print("\nTEST 2: User Registration")
    print("-" * 70)
    tests_total += 1
    success, msg = create_user("testuser01", "test01@example.com", "password123")
    if success:
        print(f"✅ User created: {msg}")
        tests_passed += 1
    else:
        print(f"❌ Failed to create user: {msg}")
    
    # TEST 3: Authenticate user
    print("\nTEST 3: User Authentication")
    print("-" * 70)
    tests_total += 1
    success, msg = authenticate_user("testuser01", "password123")
    if success:
        print(f"✅ User authenticated successfully")
        tests_passed += 1
    else:
        print(f"❌ Authentication failed: {msg}")
    
    # TEST 4: Create session
    print("\nTEST 4: Session Creation")
    print("-" * 70)
    tests_total += 1
    token = create_session("testuser01")
    if token:
        print(f"✅ Session token created: {token[:30]}...")
        tests_passed += 1
    else:
        print(f"❌ Failed to create session token")
    
    # TEST 5: Validate session
    print("\nTEST 5: Session Validation")
    print("-" * 70)
    tests_total += 1
    is_valid, username = validate_session(token)
    if is_valid and username == "testuser01":
        print(f"✅ Session validated for user: {username}")
        tests_passed += 1
    else:
        print(f"❌ Session validation failed: valid={is_valid}, user={username}")
    
    # TEST 6: Verify Premium tier
    print("\nTEST 6: Premium Tier Assignment")
    print("-" * 70)
    tests_total += 1
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("SELECT tier, daily_limit FROM users WHERE username = 'testuser01'")
        result = c.fetchone()
        conn.close()
        
        if result:
            tier, limit = result
            if tier == "Premium" and limit == 999:
                print(f"✅ User has Premium tier with {limit} daily analyses")
                tests_passed += 1
            else:
                print(f"❌ Wrong tier: {tier} with limit {limit}")
        else:
            print("❌ User not found in database")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # TEST 7: User can login with wrong password (should fail)
    print("\nTEST 7: Security - Wrong Password Rejection")
    print("-" * 70)
    tests_total += 1
    success, msg = authenticate_user("testuser01", "wrongpassword")
    if not success:
        print(f"✅ Wrong password rejected correctly")
        tests_passed += 1
    else:
        print(f"❌ Wrong password was accepted (security issue!)")
    
    # TEST 8: Create second user
    print("\nTEST 8: Multiple Users Support")
    print("-" * 70)
    tests_total += 1
    success, msg = create_user("testuser02", "test02@example.com", "password456")
    if success:
        print(f"✅ Second user created successfully")
        tests_passed += 1
    else:
        print(f"❌ Failed to create second user: {msg}")
    
    # TEST 9: Count users
    print("\nTEST 9: User Count Verification")
    print("-" * 70)
    tests_total += 1
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        conn.close()
        
        if count == 2:
            print(f"✅ Correct user count: {count}")
            tests_passed += 1
        else:
            print(f"❌ Wrong user count: {count} (expected 2)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # TEST 10: User blocking (admin function)
    print("\nTEST 10: Admin User Blocking")
    print("-" * 70)
    tests_total += 1
    try:
        deactivate_user("testuser02")
        
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("SELECT active FROM users WHERE username = 'testuser02'")
        result = c.fetchone()
        conn.close()
        
        if result and result[0] == 0:
            print(f"✅ User blocked successfully (active=0)")
            tests_passed += 1
        else:
            print(f"❌ Failed to block user")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # TEST 11: Blocked user cannot login
    print("\nTEST 11: Blocked User Login Prevention")
    print("-" * 70)
    tests_total += 1
    success, msg = authenticate_user("testuser02", "password456")
    if not success and ("blocked" in msg.lower() or "deactivated" in msg.lower()):
        print(f"✅ Blocked user correctly prevented from login")
        tests_passed += 1
    else:
        print(f"❌ Blocked user could login (security issue!)")
    
    # TEST 12: Session file exists
    print("\nTEST 12: Session File Persistence")
    print("-" * 70)
    tests_total += 1
    if os.path.exists("auth_data/active_sessions.json"):
        print(f"✅ Session file exists at auth_data/active_sessions.json")
        tests_passed += 1
    else:
        print(f"❌ Session file not found")
    
    # CLEANUP: Reset for fresh start
    print("\nCLEANUP: Resetting test users")
    print("-" * 70)
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username LIKE 'testuser%'")
        conn.commit()
        conn.close()
        print(f"✅ Test users removed")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    # FINAL REPORT
    print("\n" + "=" * 70)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print("=" * 70)
    
    if tests_passed == tests_total:
        print("✅ ALL TESTS PASSED - SYSTEM IS HEALTHY")
        print("\nSYSTEM STATUS:")
        print("  ✅ User registration works")
        print("  ✅ User authentication works")
        print("  ✅ Session management works")
        print("  ✅ Premium tier auto-assigned")
        print("  ✅ User blocking works")
        print("  ✅ Database persistence works")
        print("  ✅ Security checks working")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed")
        print("Review output above for issues")
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
