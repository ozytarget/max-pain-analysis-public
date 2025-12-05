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

# Logger setup
logger = logging.getLogger(__name__)

# Database schema version for tracking migrations
DB_SCHEMA_VERSION = 2  # Increment when schema changes
SCHEMA_VERSION_FILE = "auth_data/schema_version.txt"

USER_TIERS = {
    "Pending": {"daily_limit": 0, "days_valid": 999999, "color": "#FFA500"},  # Orange - awaiting admin
    "Free": {"daily_limit": 10, "days_valid": 30, "color": "#808080"},
    "Pro": {"daily_limit": 100, "days_valid": 365, "color": "#39FF14"},
    "Premium": {"daily_limit": 999, "days_valid": 365, "color": "#FFD700"},
    "SchemaUpdate": {"daily_limit": 0, "days_valid": 0, "color": "#FF0000"}  # Blocked - must re-register
}

def initialize_users_db():
    """Initialize professional user management database with schema versioning"""
    import os
    os.makedirs("auth_data", exist_ok=True)
    
    # Get stored schema version
    stored_version = get_schema_version()
    current_version = DB_SCHEMA_VERSION
    
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    
    # Check if users table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = c.fetchone() is not None
    
    schema_changed = False
    
    if table_exists:
        # Check if new columns exist
        c.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in c.fetchall()]
        
        # If missing new columns, schema has changed
        if 'ip1' not in columns:
            logger.warning("🔴 SCHEMA CHANGED - Detected missing columns (ip1, ip2)")
            schema_changed = True
            
            try:
                # BACKUP old users before migration
                logger.info("📦 Creating backup of existing users...")
                c.execute("SELECT * FROM users")
                old_users = c.fetchall()
                
                # If there are old users, block them and preserve data
                if old_users:
                    logger.warning(f"⚠️ Found {len(old_users)} existing users - marking as BLOCKED for re-registration")
                    
                    # Add new columns
                    c.execute("ALTER TABLE users ADD COLUMN ip1 TEXT DEFAULT ''")
                    c.execute("ALTER TABLE users ADD COLUMN ip2 TEXT DEFAULT ''")
                    
                    # Block all existing users by setting tier to SchemaUpdate
                    c.execute("UPDATE users SET tier = 'SchemaUpdate', active = 0")
                    
                    # Log the blocking action
                    for user_row in old_users:
                        username = user_row[1]  # username is second column
                        c.execute("""INSERT INTO activity_log (username, action, timestamp, details) 
                                   VALUES (?, ?, ?, ?)""",
                                (username, "BLOCKED_SCHEMA_UPDATE", 
                                 datetime.now(MARKET_TIMEZONE).isoformat(),
                                 "Account blocked due to database schema update - must re-register"))
                    
                    conn.commit()
                    logger.info(f"✅ Blocked {len(old_users)} users - they must re-register")
                else:
                    # No old users, just add columns
                    c.execute("ALTER TABLE users ADD COLUMN ip1 TEXT DEFAULT ''")
                    c.execute("ALTER TABLE users ADD COLUMN ip2 TEXT DEFAULT ''")
                    conn.commit()
                    logger.info("✅ Schema migration completed (no users to block)")
                    
            except sqlite3.OperationalError as e:
                logger.warning(f"⚠️ Column already exists: {e}")
    else:
        # Create new table with all columns
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
            ip_address TEXT DEFAULT '',
            ip1 TEXT DEFAULT '',
            ip2 TEXT DEFAULT ''
        )''')
        logger.info("✅ Created new users table with full schema")
    
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
    
    # Update schema version
    if schema_changed:
        save_schema_version(current_version)
        logger.warning(f"🔴 Schema version updated to {current_version} - users have been blocked")
    elif stored_version != current_version:
        save_schema_version(current_version)
        logger.info(f"✅ Schema version updated to {current_version}")

def get_schema_version():
    """Get stored database schema version"""
    try:
        if os.path.exists(SCHEMA_VERSION_FILE):
            with open(SCHEMA_VERSION_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return 1

def save_schema_version(version):
    """Save database schema version"""
    os.makedirs("auth_data", exist_ok=True)
    with open(SCHEMA_VERSION_FILE, 'w') as f:
        f.write(str(version))

def get_local_ip():
    """Get user IP address"""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "Unknown"

def create_user(username: str, email: str, password: str, tier: str = "Pending") -> tuple:
    """Create new user - automatically set to Pending tier (admin will assign plan)"""
    # Force tier to "Pending" - admin assigns tier later
    tier = "Pending"
    
    if tier not in USER_TIERS:
        return False, "Invalid tier"
    
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_date = datetime.now(MARKET_TIMEZONE).isoformat()
        expiration_date = (datetime.now(MARKET_TIMEZONE) + timedelta(days=USER_TIERS[tier]["days_valid"])).isoformat()
        daily_limit = USER_TIERS[tier]["daily_limit"]
        
        c.execute('''INSERT INTO users (username, email, password_hash, tier, created_date, expiration_date, daily_limit, ip1, ip2)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (username, email, password_hash, tier, created_date, expiration_date, daily_limit, "", ""))
        
        conn.commit()
        conn.close()
        
        return True, f"User {username} created. Pending admin tier assignment."
    
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    except Exception as e:
        return False, str(e)

def authenticate_user(username: str, password: str) -> tuple:
    """Authenticate user and check license validity - Max 2 IPs per user"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        c.execute("SELECT password_hash, expiration_date, active, tier, ip1, ip2 FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        
        if not result:
            return False, "User not found"
        
        password_hash, expiration_date, active, tier, ip1, ip2 = result
        
        # 🔴 CHECK FOR SCHEMA UPDATE BLOCK
        if tier == "SchemaUpdate":
            return False, "🔴 ACCOUNT BLOCKED - Database was updated. You must RE-REGISTER to continue. Your account will be restored with your original tier."
        
        if not active:
            return False, "Account is deactivated"
        
        # PENDING users allowed but with Premium access temporarily
        if tier != "Pending":
            exp_date = datetime.fromisoformat(expiration_date)
            if datetime.now(MARKET_TIMEZONE) > exp_date:
                return False, f"License expired on {exp_date.strftime('%Y-%m-%d')}. Contact support to renew."
        
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return False, "Incorrect password"
        
        # VALIDATE IP - Maximum 2 IPs allowed
        current_ip = get_local_ip()
        
        # If both IP slots are filled and current IP doesn't match either, DENY
        if ip1 and ip2 and current_ip != ip1 and current_ip != ip2:
            return False, f"❌ Access denied: This password is already in use from 2 other IPs. Maximum 2 IPs allowed per user."
        
        # If IP1 is empty, register it
        if not ip1:
            c.execute("UPDATE users SET ip1 = ? WHERE username = ?", (current_ip, username))
        # If IP2 is empty and current IP doesn't match IP1, register it
        elif not ip2 and current_ip != ip1:
            c.execute("UPDATE users SET ip2 = ? WHERE username = ?", (current_ip, username))
        
        # Update last IP used
        c.execute("UPDATE users SET ip_address = ? WHERE username = ?", (current_ip, username))
        c.execute("INSERT INTO activity_log (username, action, timestamp, ip_address) VALUES (?, ?, ?, ?)",
                  (username, "LOGIN", datetime.now(MARKET_TIMEZONE).isoformat(), current_ip))
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
        
        c.execute("SELECT usage_today, daily_limit, last_reset, tier FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        
        if not result:
            return False, 0, 0
        
        usage_today, daily_limit, last_reset, tier = result
        
        # PENDING users get PREMIUM limit (999) temporarily
        if tier == "Pending":
            daily_limit = 999
        
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

def set_unlimited_access(username: str, days: int = 365) -> bool:
    """Asignar acceso ILIMITADO a usuario específico"""
    try:
        conn = sqlite3.connect(USERS_DB)
        c = conn.cursor()
        
        # Crear tier "Unlimited" con límite muy alto (999999)
        # Extender expiration_date
        new_expiration = (datetime.now(MARKET_TIMEZONE) + timedelta(days=days)).date().isoformat()
        
        c.execute("UPDATE users SET tier = ?, daily_limit = ?, expiration_date = ? WHERE username = ?", 
                  ("Unlimited", 999999, new_expiration, username))
        
        log_admin_action(username, f"Unlimited access assigned for {days} days")
        
        conn.commit()
        conn.close()
        return True
    except:
        return False

def is_legacy_password_blocked(password: str) -> bool:
    """
    BLOQUEA COMPLETAMENTE CONTRASEÑAS ANTIGUAS
    Retorna True si la contraseña es una contraseña antigua y debe ser bloqueada
    """
    # Lista de contraseñas antiguas que NO deben funcionar más
    LEGACY_BLOCKED_PASSWORDS = [
        "fabi125", "twmmpro", "sandrira1", "mark123", "nonu12", "mary123",
        "alexis1", "sofia2023", "diego123", "carlos456", "laura789",
        "juan_pro", "maria_scan", "antonio22", "rosa2024", "pablo1"
    ]
    
    return password in LEGACY_BLOCKED_PASSWORDS

# Initialize on import
initialize_users_db()
