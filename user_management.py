"""
Professional User Management System for Pro Scanner
- User registration & authentication
- Tier-based access (Free, Pro, Premium)
- Daily usage limits
- License expiration tracking
- Admin dashboard
"""

import sqlite3
import bcrypt
import pandas as pd
from datetime import datetime, timedelta
import pytz
import socket
import logging
import os

MARKET_TIMEZONE = pytz.timezone("America/New_York")
USERS_DB = "auth_data/users.db"
ADMIN_EMAIL = "ozytargetcom@gmail.com"
ADMIN_PASSWORD_HASH = None  # Set during init

USER_TIERS = {
    "Free": {"daily_limit": 10, "days_valid": 30, "color": "#808080"},
    "Pro": {"daily_limit": 100, "days_valid": 365, "color": "#39FF14"},
    "Premium": {"daily_limit": 999, "days_valid": 365, "color": "#FFD700"}
}

def initialize_users_db():
    """Initialize professional user management database"""
    import os
    os.makedirs("auth_data", exist_ok=True)
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
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
        ip_address TEXT DEFAULT ''
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY,
        username TEXT,
        action TEXT,
        timestamp TEXT,
        ip_address TEXT,
        details TEXT
    )''')
    
    conn.commit()
    conn.close()

def get_local_ip():
    """Get user IP address"""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "Unknown"

def create_user(username: str, email: str, password: str, tier: str = "Free") -> tuple:
    """Create new user with automatic license"""
    if tier not in USER_TIERS:
        return False, "Invalid tier"
    
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_date = datetime.now(MARKET_TIMEZONE).isoformat()
        expiration_date = (datetime.now(MARKET_TIMEZONE) + timedelta(days=USER_TIERS[tier]["days_valid"])).isoformat()
        daily_limit = USER_TIERS[tier]["daily_limit"]
        
        c.execute('''INSERT INTO users (username, email, password_hash, tier, created_date, expiration_date, daily_limit)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (username, email, password_hash, tier, created_date, expiration_date, daily_limit))
        
        conn.commit()
        conn.close()
        
        return True, f"User {username} created with {tier} tier (valid {USER_TIERS[tier]['days_valid']} days)"
    
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    except Exception as e:
        return False, str(e)

def authenticate_user(username: str, password: str) -> tuple:
    """Authenticate user and check license validity"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        c.execute("SELECT password_hash, expiration_date, active, tier FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        
        if not result:
            return False, "User not found"
        
        password_hash, expiration_date, active, tier = result
        
        if not active:
            return False, "Account is deactivated"
        
        exp_date = datetime.fromisoformat(expiration_date)
        if datetime.now(MARKET_TIMEZONE) > exp_date:
            return False, f"License expired on {exp_date.strftime('%Y-%m-%d')}. Contact support to renew."
        
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return False, "Incorrect password"
        
        ip_address = get_local_ip()
        c.execute("UPDATE users SET ip_address = ? WHERE username = ?", (ip_address, username))
        c.execute("INSERT INTO activity_log (username, action, timestamp, ip_address) VALUES (?, ?, ?, ?)",
                  (username, "LOGIN", datetime.now(MARKET_TIMEZONE).isoformat(), ip_address))
        conn.commit()
        conn.close()
        
        return True, f"Welcome {username}!"
    
    except Exception as e:
        return False, str(e)

def check_daily_limit(username: str) -> tuple:
    """Check if user has scans remaining today"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        c.execute("SELECT usage_today, daily_limit, last_reset FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        
        if not result:
            return False, 0, 0
        
        usage_today, daily_limit, last_reset = result
        today = datetime.now(MARKET_TIMEZONE).date().isoformat()
        
        if last_reset != today:
            c.execute("UPDATE users SET usage_today = 0, last_reset = ? WHERE username = ?", (today, username))
            conn.commit()
            usage_today = 0
        
        conn.close()
        remaining = daily_limit - usage_today
        return remaining > 0, usage_today, daily_limit
    
    except:
        return False, 0, 0

def increment_usage(username: str):
    """Increment user's daily usage count"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("UPDATE users SET usage_today = usage_today + 1 WHERE username = ?", (username,))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def get_all_users() -> pd.DataFrame:
    """Get all users for admin panel"""
    try:
        conn = sqlite3.connect(USERS_DB)
        df = pd.read_sql_query("SELECT id, username, email, tier, created_date, expiration_date, active, usage_today, daily_limit FROM users", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def get_activity_log() -> pd.DataFrame:
    """Get activity log for admin"""
    try:
        conn = sqlite3.connect(USERS_DB)
        df = pd.read_sql_query("SELECT username, action, timestamp, ip_address FROM activity_log ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def deactivate_user(username: str):
    """Deactivate user account"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("UPDATE users SET active = 0 WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def extend_license(username: str, days: int):
    """Extend user license"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("SELECT expiration_date FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if result:
            current_exp = datetime.fromisoformat(result[0])
            new_exp = current_exp + timedelta(days=days)
            c.execute("UPDATE users SET expiration_date = ? WHERE username = ?", (new_exp.isoformat(), username))
            conn.commit()
            conn.close()
            return True
    except:
        pass
    return False

def get_user_info(username: str) -> dict:
    """Get detailed user information"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("""SELECT username, email, tier, expiration_date, daily_limit, usage_today, active 
                     FROM users WHERE username = ?""", (username,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                "username": result[0],
                "email": result[1],
                "tier": result[2],
                "expiration": result[3],
                "daily_limit": result[4],
                "usage_today": result[5],
                "active": result[6]
            }
    except:
        pass
    return None

def authenticate_admin(email: str, password: str) -> tuple:
    """Authenticate admin user"""
    if email == ADMIN_EMAIL:
        # Create admin account if doesn't exist
        try:
            conn = sqlite3.connect(USERS_DB)
            c = conn.cursor()
            c.execute("SELECT password_hash FROM users WHERE email = ?", (ADMIN_EMAIL,))
            result = c.fetchone()
            
            if not result:
                # Create admin account
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                admin_tier = "Admin"
                created_date = datetime.now(MARKET_TIMEZONE).isoformat()
                expiration_date = (datetime.now(MARKET_TIMEZONE) + timedelta(days=3650)).isoformat()
                
                c.execute('''INSERT OR IGNORE INTO users (username, email, password_hash, tier, created_date, expiration_date, daily_limit, active)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          ("admin", ADMIN_EMAIL, password_hash, admin_tier, created_date, expiration_date, 99999, 1))
                conn.commit()
                result = (password_hash,)
            
            if result:
                password_hash = result[0]
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    ip_address = get_local_ip()
                    c.execute("UPDATE users SET ip_address = ? WHERE email = ?", (ip_address, ADMIN_EMAIL))
                    c.execute("INSERT INTO activity_log (username, action, timestamp, ip_address) VALUES (?, ?, ?, ?)",
                              ("admin", "ADMIN_LOGIN", datetime.now(MARKET_TIMEZONE).isoformat(), ip_address))
                    conn.commit()
                    conn.close()
                    return True, "Admin authenticated"
                else:
                    conn.close()
                    return False, "Invalid admin password"
        except Exception as e:
            return False, str(e)
    
    return False, "Invalid admin email"

def get_user_stats() -> dict:
    """Get overall user statistics"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users WHERE active = 1")
        total_active = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE tier = 'Free'")
        free_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE tier = 'Pro'")
        pro_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE tier = 'Premium'")
        premium_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM activity_log")
        total_logins = c.fetchone()[0]
        
        conn.close()
        
        return {
            "total_active": total_active,
            "free_users": free_users,
            "pro_users": pro_users,
            "premium_users": premium_users,
            "total_logins": total_logins
        }
    except:
        return {
            "total_active": 0,
            "free_users": 0,
            "pro_users": 0,
            "premium_users": 0,
            "total_logins": 0
        }

def change_user_tier(username: str, new_tier: str) -> bool:
    """Change user tier"""
    if new_tier not in USER_TIERS and new_tier != "Admin":
        return False
    
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        daily_limit = USER_TIERS[new_tier]["daily_limit"] if new_tier in USER_TIERS else 99999
        
        c.execute("UPDATE users SET tier = ?, daily_limit = ? WHERE username = ?", 
                  (new_tier, daily_limit, username))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def reset_user_daily_limit(username: str) -> bool:
    """Manually reset user's daily limit"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        c.execute("UPDATE users SET usage_today = 0, last_reset = ? WHERE username = ?", 
                  (datetime.now(MARKET_TIMEZONE).date().isoformat(), username))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# Initialize on import
initialize_users_db()
