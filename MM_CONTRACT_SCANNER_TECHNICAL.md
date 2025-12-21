# MM Contract Scanner - Technical Implementation

## Functions Added to app.py

### 1. `calculate_black_scholes_greeks(S, K, T, r, sigma, option_type='call')`

**Purpose**: Calculate all five Greeks using the Black-Scholes model

**Parameters**:
- `S` (float): Current stock price
- `K` (float): Strike price
- `T` (float): Time to expiration in years
- `r` (float): Risk-free rate (0.045 = 4.5%)
- `sigma` (float): Volatility as decimal (0.20 = 20%)
- `option_type` (str): 'call' or 'put'

**Returns**: Dictionary with:
```python
{
    'delta': float,    # -1 to +1
    'gamma': float,    # Always positive
    'theta': float,    # Per day (annualized ÷ 365)
    'vega': float,     # Per 1% IV change
    'rho': float       # Per 1% rate change
}
```

**Formula Used**:
```
d1 = [ln(S/K) + (r + 0.5σ²)T] / [σ√T]
d2 = d1 - σ√T

For CALL:
  Δ = N(d1)
  Θ = [-S·φ(d1)·σ/(2√T) - r·K·e^(-rT)·N(d2)] / 365
  ρ = K·T·e^(-rT)·N(d2) / 100

For PUT:
  Δ = N(d1) - 1
  Θ = [-S·φ(d1)·σ/(2√T) + r·K·e^(-rT)·N(-d2)] / 365
  ρ = -K·T·e^(-rT)·N(-d2) / 100

Common to both:
  Γ = φ(d1) / [S·σ·√T]
  ν = S·φ(d1)·√T / 100

Where:
  N() = cumulative standard normal distribution
  φ() = standard normal probability density function
```

---

### 2. `calculate_prob_itm(S, K, T, r, sigma, option_type='call')`

**Purpose**: Calculate probability an option finishes In-The-Money

**Parameters**: Same as `calculate_black_scholes_greeks`

**Returns**: Float between 0 and 1

**Formula**:
```
d2 = [ln(S/K) + (r - 0.5σ²)T] / [σ√T]

For CALL: P(ITM) = N(d2)
For PUT:  P(ITM) = N(-d2)

Where N() is cumulative normal distribution
```

**Interpretation**:
- 0.50 = 50% chance of finishing ITM
- 0.75 = 75% chance of finishing ITM
- Lower for OTM (out-of-money)
- Higher for ITM (in-the-money)

---

### 3. `mm_contract_scanner(ticker, current_price, target_price, expiration_dates_dict, option_chains_dict, risk_free_rate=0.045)`

**Purpose**: Analyze all available option contracts and rank them by MM Score

**Parameters**:
- `ticker` (str): Stock symbol (e.g., "SPY")
- `current_price` (float): Current stock price
- `target_price` (float): Target price (establishes direction: >current = bullish, <current = bearish)
- `expiration_dates_dict` (dict): Dict of expiration dates (keys only needed)
- `option_chains_dict` (dict): Dict mapping expiration → list of option contracts
- `risk_free_rate` (float): Annual risk-free rate (default 0.045 = 4.5%)

**Returns**: Pandas DataFrame with columns:
```
ticker, exp_date, dte, exp_type, strike, option_type, bid, ask, mid, spread, 
spread_pct, iv, volume, oi, delta, gamma, theta, vega, rho, prob_itm, 
distance_pct, direction, mm_score, prob_profit
```

**Processing Steps**:
1. Determines direction: BULLISH if target > current, BEARISH otherwise
2. For each expiration:
   - Calculates days to expiration (DTE)
   - Classifies expiration type (⚡ WEEKLY ≤7 DTE, 📅 MONTHLY ≤30 DTE, 📊 LONG-DATED)
   - For each option contract:
     - Calculates Greeks using Black-Scholes
     - Calculates probability of ITM
     - Calculates Probability of Profit based on direction
     - Evaluates liquidity (bid-ask spread)
     - Scores strike alignment with target
3. Calculates MM Score = weighted combination of all factors
4. Returns sorted DataFrame (highest MM Score first)

**MM Score Formula**:
```python
MM Score = (
    Gamma_Score × 0.20 +
    Theta_Score × 0.20 +
    Vega_Score × 0.10 +
    (Probability_of_Profit × 100) × 0.30 +
    (Liquidity_Score × 100) × 0.10 +
    (Alignment_Score × 100) × 0.10
)

Where:
  Gamma_Score = Gamma × 100
  Theta_Score = max(0, Theta × 365)
  Vega_Score = Vega / 100
  Liquidity_Score = 1 / (1 + spread_pct)
  Alignment_Score = 1.0 if strike aligns with direction, 0.5 otherwise
  Probability_of_Profit adjusted by direction (PUT for bearish, CALL for bullish)
```

---

### 4. `display_mm_contract_winner(df_contracts, ticker, current_price, target_price)`

**Purpose**: Display the winning contracts (weekly and monthly) with detailed analysis

**Parameters**:
- `df_contracts` (DataFrame): Results from `mm_contract_scanner`
- `ticker` (str): Stock symbol
- `current_price` (float): Current price
- `target_price` (float): Target price

**Displays**:
1. Summary metrics (Current Price, Direction, Expected Move %)
2. Weekly Winner (best contract ≤7 DTE)
3. Monthly Winner (best contract ≤30 DTE)
4. Detailed Greeks breakdown
5. Expandable Greeks explanation

---

## Integration into Streamlit Tab

The MM Contract Scanner is integrated into **Tab 8: Metrics Dashboard**

### UI Layout:
```
📊 MM Contract Scanner - Greeks & Optimal Selection
├── Input Section
│   ├── Stock Ticker [SPY]
│   ├── Current Price [$450.00]
│   └── Target Price [$448.00]
├── [🔍 Scan Optimal Contracts] Button
│
├── Results Section (if scan successful)
│   ├── 🏆 MM Winning Contracts
│   │   ├── ⚡ Weekly Winner
│   │   ├── 📅 Monthly Winner
│   │   └── 📚 Understanding the Greeks (expandable)
│   │
│   ├── 📋 All Contracts Ranked by MM Score
│   │   ├── Filters
│   │   │   ├── Expiration Type multiselect
│   │   │   ├── Option Type multiselect
│   │   │   └── Minimum MM Score slider
│   │   ├── Results Table (sortable)
│   │   └── 📥 Download Full Results (CSV)
│
└── [Status Messages / Errors]
```

---

## Data Flow Diagram

```
User Input (Ticker, Prices)
         ↓
[Scan Optimal Contracts Button]
         ↓
get_expiration_dates(ticker)
         ↓
get_option_chain(ticker, exp_date) ← for each expiration
         ↓
mm_contract_scanner()
  ├─ calculate_black_scholes_greeks() ← for each option
  ├─ calculate_prob_itm() ← for each option
  └─ Calculate MM Score ← weighted formula
         ↓
DataFrame (all contracts ranked)
         ↓
display_mm_contract_winner() ← show best contracts
         ↓
Filter & Display Table
         ↓
Download CSV (optional)
```

---

## Key Assumptions & Limitations

### Assumptions:
✓ European-style options (no early exercise modeled)
✓ Black-Scholes model is accurate (breaks down in extremes)
✓ Implied Volatility surface is smooth
✓ No dividends (for stocks with dividends, IV already priced in)
✓ Continuous trading (no gaps)
✓ Transaction costs are negligible

### Limitations:
✗ Does NOT account for American option early assignment
✗ Greeks change dynamically (snapshot only)
✗ Bid-ask spread is variable (mid-price assumption)
✗ Stochastic volatility effects ignored
✗ Jump risk (earnings, gap moves) not modeled
✗ Pin risk near expiration not considered

---

## Code Locations in app.py

| Function | Lines | Purpose |
|----------|-------|---------|
| `calculate_black_scholes_greeks` | 3483-3523 | Greeks calculation |
| `calculate_prob_itm` | 3526-3553 | Probability calculation |
| `mm_contract_scanner` | 3556-3735 | Main analysis engine |
| `display_mm_contract_winner` | 3738-3855 | Results visualization |
| UI Section (Tab 8) | 7535-7655 | Streamlit interface |

---

## Testing the Implementation

### Test Case 1: SPY Weekly Put
```python
result = mm_contract_scanner(
    ticker='SPY',
    current_price=450.00,
    target_price=448.00,  # Bearish
    expiration_dates_dict={'2024-12-27': None},
    option_chains_dict={...},  # PUT 448 strike
)
# Expected: High MM Score for bearish-aligned PUT
```

### Test Case 2: QQQ Monthly Call
```python
result = mm_contract_scanner(
    ticker='QQQ',
    current_price=400.00,
    target_price=410.00,  # Bullish
    expiration_dates_dict={'2025-01-17': None},
    option_chains_dict={...},  # CALL 410 strike
)
# Expected: High MM Score for bullish-aligned CALL
```

---

## Performance Considerations

- **Latency**: Greeks calculation is O(1) per option, overall O(n) for n options
- **Memory**: DataFrame stores ~20 columns per option contract
- **API Calls**: 1 call per expiration to fetch option chain
- **Typical Analysis**: 100-500 contracts analyzed in <2 seconds

---

## Future Enhancements

1. **IV Surface Modeling**: Account for skew/smile
2. **Greeks Sensitivities**: Second-order Greeks (Volga, Vanna, Charm)
3. **Implied Probability Distribution**: Show full probability landscape
4. **Hedging Recommendations**: Auto-generate optimal hedge ratios
5. **Backtesting Integration**: Historical analysis of scanner performance
6. **Real-time Updates**: Auto-refresh every 30 seconds
7. **Mobile Optimization**: Response design for tablets

---

**Developed by Ozy | © 2025**
