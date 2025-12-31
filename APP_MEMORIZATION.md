# 📊 PRO SCANNER - Complete Application Memorization

**Last Updated:** December 31, 2025  
**Status:** 🟢 PRODUCTION READY  
**Version:** 8150 lines (app.py core)

---

## 🎯 Application Overview

**Pro Scanner** is a professional-grade **institutional options trading analysis platform** built with **Streamlit**. It combines:
- Real-time market data aggregation (Tradier, FMP, Finviz Elite APIs)
- Advanced quantitative analysis (Black-Scholes, Greeks, Gamma exposure)
- Market Maker (MM) intelligence system
- Institutional-level contract selection
- Multi-user authentication & session management

**Primary Users:**
- Day traders analyzing options
- Market makers understanding gamma/delta exposure
- Institutional investors doing macro analysis
- Options scalpers finding gamma opportunities

---

## 🏗️ Architecture Overview

### Tech Stack
```
Frontend:    Streamlit 1.40.2
Backend:     Python 3.11+
Database:    SQLite (auth_data/users.db, options_tracker.db)
APIs:        
  - Tradier (real-time options chains)
  - FMP (Financial Modeling Prep - quotes, fundamentals)
  - Finviz Elite (screener, options export)
External:    yfinance (fallback), BeautifulSoup (news scraping)
```

### Key Components

#### 1. **Main Application (app.py)** - 8150 lines
Core features:
- **Authentication System**: Legacy password-based + new SQLite user management
- **7+ Trading Analysis Tabs** (from Tab 1-11)
- **Session Management**: Auto-authenticate CEO (ozytarget)
- **Real-time Price Feeds**: Dual-source (Tradier→FMP fallback)
- **Cache Management**: TTL-based caching (30s for prices, 5min for stats)
- **Database Operations**: Locked database access, retry logic for stability

#### 2. **User Management (user_management.py)** - 575 lines
Database schema:
```sql
TABLE users:
  - id (PRIMARY KEY)
  - username (UNIQUE)
  - email
  - password_hash (bcrypt)
  - tier (Free/Pro/Premium/Pending)
  - daily_limit (queries)
  - license_expiration
  - created_at, last_login
  - ip1, ip2 (for legacy password tracking)
```

Tier system:
- **Free**: 10 queries/day, 30-day license
- **Pro**: 100 queries/day, 365-day license  
- **Premium**: 999 queries/day, 365-day license
- **Pending**: 0 queries (awaiting admin approval)

#### 3. **MM System Modules** (mm_*.py)

**mm_scanner_ui.py** - User interface for Tab 8 (Institutional MM Analysis)
**mm_data_ingestion.py** - Snapshots & contract storage
**mm_orchestrator.py** - Pipeline coordinator: Data → Quant → AI → Output
**mm_quant_engine.py** - Core quantitative calculations
  - Gamma Exposure (GEX) with liquidity weighting
  - Options walls detection
  - Pinning score calculation
  - Regime detection (CHOP/TREND/SQUEEZE)
**mm_ai_layer.py** - Natural language briefing generation
**mm_memory.py** - Historical context & learning system

#### 4. **Analysis Modules**

Key functions by purpose:

**Price/Volatility:**
- `get_current_price()` - Real-time spot price (10s cache)
- `get_implied_volatility()` - Nearest expiration IV
- `get_historical_prices_combined()` - 30-day history (FMP→yfinance)

**Options Data:**
- `get_options_data()` - Tradier options chains (10s cache)
- `get_finviz_options_data()` - Finviz Elite export
- `get_options_data_hybrid()` - Intelligent fallback system

**Analysis Engines:**
- `calculate_max_pain()` - Strike where max total losses (OI-weighted)
- `calculate_black_scholes_greeks()` - Delta, Gamma, Theta, Vega + second-order (Vanna, Volga, Charm)
- `mm_contract_scanner()` - Institutional-grade contract ranking
- `gamma_exposure_chart()` - Visual GEX analysis
- `plot_skew_analysis_with_totals()` - IV skew with bubbles

**Market Data:**
- `get_financial_metrics()` - P/E, P/B, dividend yield
- `get_macro_data()` - FED rates, GDP, CPI, unemployment
- `fetch_fmp_*()` - 20+ FMP data endpoints (company profile, ratios, DCF, etc.)
- `fetch_market_movers()` - Gainers/Losers/Actives

**News & Sentiment:**
- `fetch_google_news()`, `fetch_bing_news()`, `fetch_instagram_posts()`
- `calculate_retail_sentiment()` - Bullish/Bearish/Neutral from titles
- `calculate_volatility_sentiment()` - Market stability assessment

---

## 📋 Core Features & Workflows

### Feature 1: Real-Time Options Analysis
**Workflow:**
1. User selects ticker (e.g., SPY) + expiration date
2. System fetches current price (Tradier API)
3. Retrieves full options chain with Greeks
4. Calculates Max Pain strike
5. Displays gamma exposure, IV skew, probability metrics
6. Generates ML-based contract suggestions

**Key Metrics:**
- Open Interest (OI) clustering
- Gamma-weighted exposure
- Probability of ITM/Profit
- Risk-Reward ratio
- Expected value

### Feature 2: Market Maker Intelligence
**Three-Level Analysis:**

**Level 1: Gamma Scalping** (Tab 8)
- Identifies optimal contracts for scalping
- Scores based on Gamma value + Theta decay
- Highlights "sweet spot" strikes with high Gamma/OI

**Level 2: Institutional MM Scoring**
```
MM Score = 
  35% × Gamma Score (price move profit potential)
  + 30% × Theta Score (daily revenue, time decay)
  + 20% × IV Edge Score (vol surface opportunity)
  + 10% × OI Score (liquidity concentration)
  + 5% × Spread Score (execution cost)
```

**Level 3: Pinning Score**
- Analyzes walls (concentrated OI at round numbers)
- Predicts likely support/resistance levels
- Calculates probability of expiration pinning

### Feature 3: Multi-Expiration Analysis
**Automatic Classification:**
- **⚡ Weekly** (≤7 DTE): 1.2x weight boost (high theta)
- **📅 Monthly** (8-30 DTE): Standard 1.0x weight
- **📊 60-DTE** (31-60 DTE): 0.8x weight  
- **📈 Long-Dated** (>60 DTE): 0.6x weight

Each expiration shows:
- Top contracts by MM score
- Greeks evolution with DTE
- Theta decay acceleration factor
- IV term structure analysis

### Feature 4: Sentiment Analysis
**Three Sources:**
1. **News Sentiment** (Google/Bing scraping)
   - Positive keywords: "up, bullish, gain, rise, surge"
   - Negative keywords: "down, bearish, loss, drop, fall"
   - Score: 0.0 (Very Bearish) → 1.0 (Very Bullish)

2. **Volatility Sentiment**
   - High Vol keywords: "crash, surge, volatile, shock"
   - Low Vol keywords: "steady, calm, stable, flat"
   - Output: Stability level

3. **Web Sentiment** (via fetch_web_sentiment)
   - Aggregated from latest news articles
   - Used for directional bias signals

### Feature 5: Contract Assignment Tracking (Tab 11)
**Database Schema:**
```sql
TABLE assigned_contracts:
  - ticker, strike, option_type, expiration_date
  - assigned_price (cost basis)
  - current_price (auto-updated every 15s)
  - profit_loss_percent (live P&L)
  - assigned_at, last_updated
  - closed (boolean)
```

**Auto-Update Mechanism:**
- Every 15 seconds: `update_contract_prices()`
- Fetches fresh options data for each position
- Calculates live Greeks (Gamma, Theta)
- Updates database with retry logic (5 retries, 2s delay)

---

## 🔑 Key Functions & Their Purpose

### Critical Data Fetching
| Function | Source | TTL | Purpose |
|----------|--------|-----|---------|
| `get_current_price()` | Tradier/FMP | 10s | Spot price for Greeks calculation |
| `get_options_data()` | Tradier API | 10s | Option chains with Greeks |
| `get_historical_prices_combined()` | FMP/yfinance | 30s | Historical data for indicators |
| `get_expiration_dates()` | Tradier | 1 day | Available expirations |
| `get_implied_volatility()` | Tradier | 1 day | Nearest exp IV |

### Advanced Analysis
| Function | Inputs | Outputs | Use Case |
|----------|--------|---------|----------|
| `calculate_black_scholes_greeks()` | S,K,T,r,σ,type | Delta,Gamma,Theta,Vega,Vanna,Volga | Greeks for MM analysis |
| `mm_contract_scanner()` | ticker, price, target | DataFrame ranked contracts | Find best MM opportunities |
| `calculate_max_pain()` | options_data | strike price | Predict support/resistance |
| `gamma_exposure_chart()` | processed_data | Plotly figure | Visualize GEX by strike |
| `calculate_prob_itm()` | S,K,T,r,σ,type | 0-1 probability | Probability metrics |

### Market Intelligence
| Function | Returns | Update Freq |
|----------|---------|------------|
| `fetch_fmp_market_movers()` | gainers/losers/actives | 1 hour |
| `fetch_fmp_sector_performance()` | sector % change | 1 hour |
| `get_macro_factors()` | FED rate, GDP, CPI | 1 day |
| `fetch_senate_trades()`, `fetch_house_trades()` | insider trading | 1 day |
| `fetch_fmp_company_profile()` | market cap, beta, sector | 1 hour |

---

## 🔐 Authentication & Security

### Session Management
1. **Legacy System** (deprecated):
   - Passwords stored hashed in `auth_data/passwords.db`
   - IP-tracked (max 2 IPs per password)
   - Usage counter to prevent sharing

2. **New System** (active):
   - SQLite `auth_data/users.db` with bcrypt hashing
   - Username/email authentication
   - Tier-based daily usage limits
   - Session tokens for persistence
   - License expiration dates

### Auto-Authentication
Current implementation: **CEO/Admin (ozytarget) auto-authenticated** without password
- `st.session_state["authenticated"] = True`
- User sees only trading app, NO login screen
- Normal users register via "📝 Register" tab

### Rate Limiting
- Daily limits enforced per tier
- `check_daily_limit()` validates before analysis
- `increment_usage()` tracks queries
- Can be reset by admin: `reset_user_daily_limit()`

---

## 💾 Database Structure

### 1. Users Database (`auth_data/users.db`)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT,
    password_hash TEXT,
    tier TEXT,  -- Free/Pro/Premium/Pending
    daily_limit INTEGER,
    usage_today INTEGER,
    license_expiration DATE,
    ip1 TEXT,
    ip2 TEXT,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```

### 2. Contract Tracking (`options_tracker.db`)
```sql
CREATE TABLE assigned_contracts (
    id INTEGER PRIMARY KEY,
    ticker TEXT,
    strike REAL,
    option_type TEXT,  -- CALL/PUT
    expiration_date TEXT,
    assigned_price REAL,
    current_price REAL,
    assigned_at TIMESTAMP,
    profit_loss_percent REAL,
    last_updated TIMESTAMP,
    closed BOOLEAN
);
```

### 3. MM System (`mm_system.db`) - Phase 1
```sql
TABLE snapshots:     Timestamp, price, IV, put-call ratio
TABLE contracts:     Strike, type, Greeks, OI, volume by snapshot
TABLE computed_levels: Walls, pinning score, regime, gamma flip zones
TABLE news:          Sentiment analysis by ticker
```

---

## 🎨 UI/UX Structure

### Navigation (Streamlit Sidebar - Collapsed)
Main app auto-authenticates, shows **7-11 Analysis Tabs**:

1. **Tab 1: Max Pain** 
   - Histogram of losses by strike
   - Support/Resistance levels
   - Current price indicator

2. **Tab 2: Gamma Exposure (GEX)**
   - Call/Put gamma by strike
   - Net gamma exposure
   - Whale accumulation zones

3. **Tab 3: IV Skew Analysis**
   - IV surface visualization
   - Skew direction (call/put preference)
   - Bubble size = OI

4. **Tab 4: Elliott Pulse**
   - Gamma net exposure
   - Predicted next move direction
   - Highest gamma concentration

5. **Tab 5: Order Flow**
   - Buy/Sell call/put distribution
   - Market maker delta hedging pressure
   - Directional bias

6. **Tab 6: Rating Flow**
   - Max pain target price
   - MM profitability potential
   - Strike quality scoring

7. **Tab 7: Liquidity Pulse**
   - Buy/Sell volume over time
   - Projected price target
   - Support/Resistance zones

8. **Tab 8: Market Maker Scanner** (MM SYSTEM)
   - Institutional contract ranking
   - Black-Scholes Greeks
   - Probability metrics
   - MM score breakdown

9. **Tab 9-11: (Extended Features)**
   - Macro economic analysis
   - Sector performance
   - Senate/House trading activity

---

## 🚀 Critical Operations & Flows

### Operation 1: Daily Price Update
```
Every 15 seconds (app running):
├─ get_current_price(ticker)           [Tradier/FMP]
├─ get_options_data(ticker, exp_date)  [Tradier API]
├─ FOR each assigned_contract:
│  └─ Update current_price, P&L%, Greeks
├─ CACHE hit/miss tracking
└─ Log to analytics
```

**Cache Strategy:**
- TTL_REAL_TIME = 10s (options price)
- TTL_AGGRESSIVE = 60s (screener data)
- TTL_STATS = 300s (5 min for ratios)
- CACHE_HIT tracking in `cache_stats` dict

### Operation 2: Options Chain Analysis
```
User selects ticker + expiration:
├─ Fetch from Tradier API
├─ Parse JSON, validate bid/ask > 0
├─ Calculate Greeks (if not provided)
│  └─ estimate_greeks() using Black-Scholes
├─ Filter by volume/OI thresholds
├─ Build strike surface
│  └─ Detect walls (peaks in OI)
│  └─ Calculate gamma exposure
├─ Generate contract suggestions
│  └─ Score by gamma, theta, IV edge
└─ Visualize (Plotly charts)
```

### Operation 3: Contract Assignment
```
User clicks "Assign Contract":
├─ Input: ticker, strike, type, exp_date, price
├─ LOCK database
├─ Check if already assigned
├─ INSERT into assigned_contracts
├─ Set initial Greeks
├─ UNLOCK & COMMIT
└─ Display confirmation
```

### Operation 4: Auto-Update Loop
```
Every 15 seconds:
├─ Get all active (non-closed) contracts
├─ FOR each contract:
│  ├─ Fetch current options price
│  ├─ Calculate new Greeks
│  ├─ Calculate P&L%
│  ├─ Update record
│  └─ Store in session state (for display)
├─ Handle DB locks (5 retries, 2s backoff)
├─ Log any errors
└─ Update timestamp
```

---

## 📊 Key Algorithms

### Algorithm 1: Max Pain Calculation
```python
For each strike price S:
  call_loss(S) = Σ OI_call(K) × max(0, K - S)
  put_loss(S)  = Σ OI_put(K) × max(0, S - K)
  total_loss(S) = call_loss(S) + put_loss(S)

Max Pain = argmin(total_loss)  # Strike with minimum losses
```

### Algorithm 2: Gamma Exposure Index
```python
GEX = Σ [
  (gamma_call × OI_call - gamma_put × OI_put) 
  × liquidity_factor × IV_factor × moneyness_factor
] by strike

Direction = sign(GEX)  # Positive = bullish gamma, negative = bearish
```

### Algorithm 3: Black-Scholes Greeks
```
d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
d2 = d1 - σ√T

Delta_call = N(d1)
Gamma = φ(d1) / (S × σ × √T)         # Same for calls & puts
Theta = [-S×φ(d1)×σ/(2√T) - r×K×e^(-rT)×N(d2)] / 365
Vega = S × φ(d1) × √T / 100
Vanna = -φ(d1) × d2 / σ               # First second-order
Volga = S × φ(d1) × √T × (d1×d2 - 1) / σ²
```

### Algorithm 4: MM Contract Scoring
```
MM_Score = 
  35% × Gamma_Score +           # Price movement profit
  30% × Theta_Score +           # Daily time decay
  20% × IV_Edge_Score +         # Vol surface opportunity  
  10% × OI_Score +              # Liquidity concentration
  5% × Spread_Score             # Execution cost

Gamma_Score = min(100, gamma / max_gamma_in_exp × 100)

Theta_Score = min(100, |theta_daily| × 5000)
            × (1.5 if DTE ≤ 7 else 1.3 if DTE ≤ 14 else 1.1 if DTE ≤ 30)

IV_Edge_Score = base(IV level) + vanna_contribution + volga_contribution
```

---

## 🔄 API Integration Strategy

### Tradier (Primary for Options)
**Endpoints Used:**
- `/markets/quotes` - Real-time prices
- `/markets/options/chains` - Full options chains  
- `/markets/options/expirations` - Available expirations
- `/markets/history` - Historical OHLCV data

**Rate Limiting:** 120/minute, 480/hour
**Fallback:** FMP for alternative pricing
**Retry Strategy:** 5 attempts with exponential backoff (1s, 2s, 4s, 8s, 16s)

### FMP (Primary for Fundamentals)
**Endpoints Used:**
- `/quote/{symbol}` - Stock quotes
- `/stock-screener` - Bulk filtering
- `/ratios/{symbol}` - Financial ratios
- `/enterprise-values/{symbol}` - EV metrics
- `/economic?name={indicator}` - Macro data
- 20+ other data endpoints (profile, financials, DCF, etc.)

**Rate Limiting:** Based on API tier (development: 250/day)
**Caching:** 1 day for most, 1 hour for moving metrics

### Finviz Elite (Screener)
**Endpoints Used:**
- `/export.ashx` - Screener export (stocks + filters)
- `/export/options` - Options chain export

**Authentication:** Token-based (FINVIZ_API_TOKEN from .env)
**Format:** CSV response (parsed with pandas.read_csv)

### yfinance (Fallback)
**Use Case:** When FMP fails
**Data:** Historical prices, market data
**No Rate Limit:** But respect good-faith usage

---

## 🎯 Performance Optimizations

### Caching Strategy
```python
@st.cache_data(ttl=10)      # 10 seconds - real-time data
def get_current_price(ticker): ...

@st.cache_data(ttl=30)      # 30 seconds - options data
def get_options_data(ticker, expiration): ...

@st.cache_data(ttl=300)     # 5 minutes - fundamental data
def get_financial_metrics(symbol): ...

@st.cache_data(ttl=86400)   # 1 day - company info
def get_top_traded_stocks(): ...
```

### Parallel Processing
```python
with ThreadPoolExecutor(max_workers=num_workers) as executor:
    futures = {
        executor.submit(get_historical_prices_combined, ticker): ticker 
        for ticker in tickers
    }
    for future in futures:
        ticker = futures[future]
        prices, volumes = future.result()
        # Process...
```

### Database Optimization
```python
with db_lock:
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
    # ... operations ...
    conn.commit()
```

**Retry Logic:** 5 retries, 2-second delays for locked databases

---

## 📈 Metrics & Monitoring

### Session Tracking
- Active sessions: `st.session_state["session_token"]`
- User info: `st.session_state["current_user"]`
- Daily usage: `usage_today` from DB

### Cache Performance
```python
cache_stats = {
    "hits": 0,
    "misses": 0,
    "bandwidth_saved_mb": 0
}
```

### Logging
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# All API calls, calculations, errors logged with timestamps
```

---

## 🛡️ Error Handling Patterns

### API Failures
```python
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()
except RequestException as e:
    logger.warning(f"Primary source failed: {e}")
    # Fallback to secondary source
    data = get_fmp_fallback(...)
```

### JSON Parsing
```python
if not data or not isinstance(data, dict):
    logger.error(f"Invalid response: {response.text}")
    return None
```

### Database Locking
```python
for attempt in range(DB_RETRIES):
    try:
        # Database operation
        break
    except sqlite3.OperationalError as e:
        if "locked" in str(e) and attempt < DB_RETRIES - 1:
            sleep(DB_RETRY_DELAY)
        else:
            raise
```

---

## 🚨 Known Issues & Status

### Current Status: ✅ PRODUCTION READY
- All 12 system tests passing (from SYSTEM_STATUS.md)
- Database persistence working
- Real-time pricing stable
- User management operational

### Minor Known Quirks
1. **Finviz API sometimes returns empty** → Falls back to Tradier
2. **yfinance can be slow** → Limited to fallback only
3. **News scraping fragile** → HTML structure changes affect parsing
4. **Database locks on high concurrency** → Mitigated with WAL + retries

### Recent Fixes
- Added PRAGMA journal_mode=WAL for concurrent access
- Robust JSON validation in `get_options_data()`
- Vanna/Volga calculation for institutional-grade Greeks
- Second-order Greeks (Charm, Vanna, Volga) for MM analysis

---

## 🎓 How to Extend

### Adding New Analysis Tab
1. Create `def tab_x_content():` function
2. Add to sidebar tabs list
3. Structure: Input widgets → Data fetch → Calculate → Visualize
4. Use existing fetching functions (they handle fallbacks)
5. Cache any expensive operations with `@st.cache_data(ttl=...)`

### Adding New API Source
1. Create wrapper function: `def get_xxx_source(params):` 
2. Implement retry logic with exponential backoff
3. Validate response format
4. Add to primary/fallback chain
5. Add caching decorator with appropriate TTL

### Adding New Calculation
1. Put math in new function, keep pure (no side effects)
2. Document inputs/outputs clearly
3. Test with mock data first
4. Add to `analyze_options()` or new analysis function
5. Visualize results with Plotly

---

## 📚 Dependencies Reference

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.40.2 | Web UI framework |
| pandas | 2.2.0 | Data manipulation |
| numpy | 1.26.4 | Numerical computing |
| plotly | 5.24.1 | Interactive charts |
| scipy | 1.14.0 | Statistical functions |
| requests | 2.32.3 | HTTP requests |
| yfinance | 0.2.66 | Finance data fallback |
| bcrypt | 4.2.0 | Password hashing |
| beautifulsoup4 | 4.13.2 | Web scraping |
| python-dotenv | 1.0.1 | Environment variables |
| pytz | 2024.2 | Timezone handling |

---

## 📞 Support & Contacts

**Admin Email:** ozytargetcom@gmail.com  
**For Access:** Text "Pro Scanner Access" to 678-978-9414  
**GitHub:** ozytarget/max-pain-analysis-public

---

**This memorization is complete and comprehensive. The app is production-ready with institutional-grade options analysis capabilities.**
