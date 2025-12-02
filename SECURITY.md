# 🔐 SECURITY GUIDELINES

## API Keys and Credentials Management

### ✅ WHAT TO DO

1. **Store all API keys in `.env` file** (never in code)
   ```
   .env (local - NOT committed to git)
   ```

2. **Use `python-dotenv`** to load environment variables:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   
   API_KEY = os.getenv("FMP_API_KEY", "")
   ```

3. **Add sensitive files to `.gitignore`**:
   - `.env` (all environment files)
   - `auth_data/` (database with sensitive info)
   - `credentials/`
   - `secrets/`

4. **Rotate API keys regularly** if compromised
   - Update in `.env`
   - No code changes needed

### ❌ WHAT NOT TO DO

- ❌ Hardcode API keys in `app.py`
- ❌ Commit `.env` to GitHub
- ❌ Share passwords or API keys in chat
- ❌ Push `auth_data/` database to public repos
- ❌ Log sensitive information

## File Structure (Secure)

```
max-pain-analysis-public/
├── app.py                    # ✅ NO hardcoded secrets
├── .env                      # 🔐 PRIVATE - loads secrets
├── .gitignore               # ✅ Blocks .env, auth_data/
├── requirements.txt         # ✅ Includes python-dotenv
├── auth_data/              # 🔐 PRIVATE - user database
│   └── passwords.db
└── README.md
```

## Environment Variables (.env)

**Format:**
```dotenv
# API Keys - Keep this file PRIVATE
KRAKEN_API_KEY=your_key_here
KRAKEN_PRIVATE_KEY=your_secret_here
FMP_API_KEY=your_fmp_key
TRADIER_API_KEY=your_tradier_key
FINVIZ_API_TOKEN=your_finviz_token
```

**How to load in code:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FMP_API_KEY", "")  # Default empty string if not found
```

## Git Security Checklist

- [x] `.env` in `.gitignore`
- [x] `auth_data/` in `.gitignore`
- [x] No hardcoded API keys in `app.py`
- [x] `python-dotenv` in `requirements.txt`
- [x] `.gitignore` comprehensive

## How to Share the Project Safely

1. **Share the code repo** (without `.env`):
   ```bash
   git clone https://github.com/user/max-pain-analysis-public
   ```

2. **Create template file** `.env.example`:
   ```dotenv
   KRAKEN_API_KEY=your_key_here
   KRAKEN_PRIVATE_KEY=your_secret_here
   FMP_API_KEY=your_fmp_key
   TRADIER_API_KEY=your_tradier_key
   FINVIZ_API_TOKEN=your_finviz_token
   ```

3. **Users create their own `.env`** with their keys

## Deployment Security

### Local Deployment (Current)
- ✅ `.env` stored locally only
- ✅ No exposure to GitHub
- ✅ Database in `auth_data/` local

### Cloud Deployment (Future)
- Use environment variable management:
  - Heroku: Config Vars
  - AWS: Systems Manager Parameter Store
  - Docker: Secret mounting
  - Kubernetes: Secrets

## Incident Response

If API key is exposed:

1. **Immediately revoke the key** in the API provider's dashboard
2. **Update `.env`** with new key
3. **No code changes needed** (loads from `.env`)
4. **Commit the new code** (which references `.env`, not hardcoded values)

---

**Last Updated:** December 1, 2025
**Status:** ✅ SECURE
