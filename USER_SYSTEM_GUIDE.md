# 🎯 Professional User Management System

## Overview

El nuevo sistema de gestión de usuarios es **completamente automatizado** y permite:

✅ **Registro de usuarios** con 3 tiers diferentes  
✅ **Control de licencias** con expiración automática  
✅ **Límite de uso diario** por usuario  
✅ **Panel de administrador** para gestionar usuarios  
✅ **Registro de actividad** completo  

---

## 📋 User Tiers

| Tier | Daily Limit | Validity | Price Model |
|------|------------|----------|------------|
| **Free** | 10 scans/día | 30 días | Gratis |
| **Pro** | 100 scans/día | 365 días | $9.99/mes |
| **Premium** | Unlimited | 365 días | $29.99/mes |

---

## 🔐 Authentication Flow

### 1. **First Time User - Registration**
```
User clicks "Register"
    ↓
Selects tier (Free/Pro/Premium)
    ↓
Fills: Username, Email, Password
    ↓
System creates user in database
    ↓
License is automatically assigned (30 or 365 days)
    ↓
User can login immediately
```

### 2. **Returning User - Login**
```
User enters Username + Password
    ↓
System verifies password
    ↓
System checks if license is valid
    ↓
If valid → User authenticated ✅
If expired → "License expired. Contact support" ❌
If inactive → "Account deactivated" ❌
```

### 3. **Daily Limit Check**
```
Every action (scan, analysis, etc.)
    ↓
System checks: usage_today < daily_limit
    ↓
If yes → Allow action + increment counter
If no → "Daily limit reached. Return tomorrow."
```

---

## 🛠️ Database Schema

### Users Table
```
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE (e.g., "ozy_trader")
email           TEXT UNIQUE (e.g., "ozy@example.com")
password_hash   TEXT (bcrypt hashed)
tier            TEXT ("Free" | "Pro" | "Premium")
created_date    TEXT (ISO format)
expiration_date TEXT (ISO format - auto-calculated)
daily_limit     INTEGER (10/100/unlimited)
usage_today     INTEGER (resets daily)
last_reset      TEXT (date of last reset)
active          BOOLEAN (1=active, 0=deactivated)
ip_address      TEXT (for tracking)
```

### Activity Log Table
```
id              INTEGER PRIMARY KEY
username        TEXT
action          TEXT ("LOGIN", "SCAN", "ANALYSIS", etc.)
timestamp       TEXT (ISO format)
ip_address      TEXT
details         TEXT (optional notes)
```

---

## 🎮 Functions Available

### User Management
```python
from user_management import (
    authenticate_user,      # Returns (success: bool, message: str)
    create_user,           # Returns (success: bool, message: str)
    check_daily_limit,     # Returns (has_limit: bool, usage: int, limit: int)
    increment_usage,       # Increments daily counter
    get_user_info,         # Returns dict with user details
    extend_license,        # Adds days to license
    deactivate_user,       # Deactivates account
    get_all_users,         # Returns DataFrame (admin)
    get_activity_log       # Returns DataFrame (admin)
)
```

### Example Usage in app.py
```python
# Login
success, msg = authenticate_user("username", "password")
if success:
    st.session_state["authenticated"] = True
    st.session_state["username"] = "username"

# Check daily limit before action
has_limit, used, total = check_daily_limit(st.session_state["username"])
if not has_limit:
    st.error(f"Daily limit reached ({used}/{total})")
else:
    # Perform action
    result = perform_scan()
    increment_usage(st.session_state["username"])

# Get user info
user_info = get_user_info("username")
print(f"Tier: {user_info['tier']}, Days left: {user_info['expiration']}")
```

---

## 👨‍💼 Admin Functions

### Create Premium User (Programmatically)
```python
from user_management import create_user

success, msg = create_user(
    username="client_name",
    email="client@example.com",
    password="initial_password",
    tier="Premium"  # 999/day, 365 days
)
```

### Extend Expiring License
```python
from user_management import extend_license

extend_license("username", days=30)  # Add 30 more days
```

### Deactivate Rogue Account
```python
from user_management import deactivate_user

deactivate_user("username")  # Account locked
```

### View All Users
```python
from user_management import get_all_users

users_df = get_all_users()
print(users_df[["username", "tier", "expiration_date", "active"]])
```

### View Activity Log
```python
from user_management import get_activity_log

log_df = get_activity_log()  # Last 100 actions
print(log_df)
```

---

## 🔄 Daily Reset Logic

The system automatically:
1. **Checks if date changed** (`last_reset != today`)
2. **Resets counter** to 0 if new day
3. **Updates last_reset** to today's date
4. **User can start fresh** at 0 usage for new day

---

## 🚀 Integration in app.py

### 1. **Add Import**
```python
from user_management import (
    authenticate_user, check_daily_limit, increment_usage,
    get_user_info, extend_license, get_all_users, get_activity_log
)
```

### 2. **After Authentication (in main app)**
```python
# Check daily limit before performing actions
has_limit, used, total = check_daily_limit(st.session_state["username"])

if not has_limit:
    st.error(f"❌ Daily limit reached ({used}/{total})")
    st.info("Return tomorrow or upgrade to Pro/Premium")
else:
    # Allow user to perform scan/analysis
    result = perform_analysis()
    
    # Increment usage after successful action
    increment_usage(st.session_state["username"])
    st.success(f"✅ Scan complete! ({used+1}/{total} used today)")
```

### 3. **Admin Dashboard (Optional Tab)**
```python
if st.session_state["tier"] == "Admin":  # Only for admins
    with st.sidebar:
        st.header("⚙️ Admin Panel")
        
        tab1, tab2 = st.tabs(["Users", "Activity"])
        
        with tab1:
            users_df = get_all_users()
            st.dataframe(users_df, use_container_width=True)
        
        with tab2:
            activity_df = get_activity_log()
            st.dataframe(activity_df, use_container_width=True)
```

---

## 🔒 Security Features

✅ **Password Hashing** - bcrypt (industry standard)  
✅ **License Expiration** - Automatic enforcement  
✅ **IP Tracking** - Logs every login IP  
✅ **Activity Logging** - Complete audit trail  
✅ **Account Deactivation** - Instant lockout  
✅ **Daily Limits** - Per-user usage control  

---

## 📊 User Status Check

```python
# Quick status check
user_info = get_user_info("username")

if not user_info:
    print("User not found")
else:
    print(f"""
    Username: {user_info['username']}
    Tier: {user_info['tier']}
    Status: {'Active' if user_info['active'] else 'Deactivated'}
    License Expires: {user_info['expiration']}
    Daily Usage: {user_info['usage_today']}/{user_info['daily_limit']}
    """)
```

---

## 💡 Key Advantages

✅ **Automated** - No manual password management  
✅ **Scalable** - Unlimited users, automatic tier enforcement  
✅ **Transparent** - Users see exactly what they get  
✅ **Flexible** - Easy to adjust tiers, limits, durations  
✅ **Secure** - Enterprise-grade authentication  
✅ **Auditable** - Complete activity logs for compliance  

---

## 🎯 Future Enhancements

- [ ] Payment integration (Stripe/PayPal)
- [ ] Automated email notifications (license expiring)
- [ ] API keys for programmatic access
- [ ] Usage analytics dashboard
- [ ] Custom tier creation
- [ ] Team/organization support

---

**Created:** December 4, 2025  
**System:** Pro Scanner v2.0  
**Status:** Production Ready ✅
