# 🎯 MM CONTRACT SCANNER - Greeks-Based Option Analysis

## Overview
The **MM Contract Scanner** is a sophisticated options analysis tool that uses Black-Scholes Greeks calculations to identify the optimal option contracts for your trading strategy. Think of it as a Market Maker's intelligent option selector.

## What It Does

### Core Functionality
1. **Fetches real-time option chains** for multiple expiration dates (weekly, monthly, long-dated)
2. **Calculates Black-Scholes Greeks** for each option:
   - **Delta (Δ)**: Price sensitivity - how much the option moves with $1 stock move
   - **Gamma (Γ)**: Delta acceleration - how fast Delta changes with price moves
   - **Theta (Θ)**: Daily time decay - value lost per day (positive for sellers)
   - **Vega (ν)**: Volatility sensitivity - change for 1% IV change
   - **Rho (ρ)**: Interest rate sensitivity
3. **Calculates Probability of ITM (In-The-Money)** using cumulative normal distribution
4. **Ranks contracts** using MM Score (weighted Greeks + Probability + Liquidity)
5. **Identifies winners** for weekly and monthly expirations

## Usage

### Location in App
**Tab 8: Metrics Dashboard → MM Contract Scanner - Greeks & Optimal Selection**

### Step-by-Step Guide

#### 1. **Set Your Parameters**
```
Stock Ticker:    SPY
Current Price:   $450.00
Target Price:    $448.00  (Bearish bias - target is lower)
```

#### 2. **Click "Scan Optimal Contracts"**
The scanner will:
- Fetch expiration dates
- Download option chains
- Calculate Greeks for each strike
- Rank them by MM Score

#### 3. **Review the Winners**
The scanner displays:
- **⚡ Weekly Winner**: Best risk/reward for 1-2 week trades
- **📅 Monthly Winner**: Best risk/reward for 3-4 week trades

Example output:
```
⚡ Weekly Winner
PUT | Strike: $448.00
Price Range: $2.10 - $2.25
Greeks: Δ: 0.450 | Γ: 0.045
Probability: ITM 45% | Profit 68%
⭐ MM Score: 78.5/100
Theta: $0.032 daily | Vega: $1.25 per 1% IV
DTE: 7 days | IV: 18.5%
```

#### 4. **Filter Results**
Use the detailed table to filter by:
- **Expiration Type**: Weekly, Monthly, Long-dated
- **Option Type**: CALL or PUT
- **MM Score**: Minimum quality threshold

### Example Scenario
```
Asset: SPY @ $160
Target: $158 (Bearish)
Expected Move: -1.25%

Scanner Result:
- Weekly PUT $158 Strike
  - Γ (Gamma): 0.045 (good acceleration)
  - Θ (Theta): $0.035/day (decay in your favor)
  - IV: 19% (normal)
  - P(Profit): 68% probability of profit
  - MM Score: 78/100 ← WINNER

vs. Monthly PUT $158 Strike
  - Γ (Gamma): 0.018 (lower acceleration)
  - Θ (Theta): $0.012/day (slower decay)
  - IV: 19%
  - P(Profit): 64% probability
  - MM Score: 65/100
```

## MM Scoring Explained

The **MM Score** (0-100) is a weighted combination of:

| Component | Weight | Meaning |
|-----------|--------|---------|
| Gamma (Γ) | 20% | Hedging ability - how much delta changes |
| Theta (Θ) | 20% | Time decay advantage (positive for sellers) |
| Vega (ν) | 10% | IV crush sensitivity |
| Probability of Profit | 30% | Directional alignment with target |
| Liquidity | 10% | Tight bid-ask spread |
| Strike Alignment | 10% | How well strike matches your target |

### High MM Score Means:
✓ Good Gamma for rebalancing  
✓ Strong Theta decay in your favor  
✓ Low volatility sensitivity risk  
✓ High probability of your target  
✓ Tight spreads (easy to enter/exit)  
✓ Perfect strike for your thesis  

## Greeks Interpretation

### Delta (Δ)
- **Call**: 0.00 to 1.00 (positive)
  - Δ 0.50 = ~50% chance ITM, moves $0.50 per $1 stock move
- **Put**: -1.00 to 0.00 (negative)
  - Δ -0.50 = ~50% chance ITM, gains $0.50 per $1 stock drop

### Gamma (Γ)
- **Highest at ATM (At-The-Money)** strikes
- **Increases as expiration approaches** (peaks last 2 weeks)
- **Buy Gamma** if you expect moves but unsure direction
- **Sell Gamma** if you expect calm (collect theta)

### Theta (Θ)
- **Always positive for sellers** (time decay works for you)
- **Always negative for buyers** (time decay works against you)
- **Increases dramatically last 2 weeks**
- **Best for weekly spreads** (high theta decay)

### Vega (ν)
- **Same for calls and puts** (up = benefits from IV rise)
- **Highest OTM** (Out-The-Money)
- **Buy Vega** if IV is low (expect expansion)
- **Sell Vega** if IV is high (expect compression)

## Real-World Examples

### Example 1: Bullish Trade
```
Current Price: $450
Target: $455 (+1.1% upside)
Direction: BULLISH

Best Contract Found:
- CALL $452 Strike
- Delta: 0.45 (moderate directional exposure)
- Gamma: 0.038 (good for catching move)
- Theta: -$0.025/day (acceptable for upside play)
- MM Score: 72/100

Why? 
- Strike near target ($452 vs $455 target)
- Good gamma for acceleration if stock jumps
- Tight spread suggests liquid contract
- High prob of profit
```

### Example 2: Bearish Trade
```
Current Price: $160
Target: $158 (-1.25% downside)
Direction: BEARISH

Best Contract Found:
- PUT $158 Strike (Weekly)
- Delta: -0.48 (strong directional match)
- Gamma: 0.045 (excellent for reversal hedging)
- Theta: $0.032/day (decay in your favor)
- MM Score: 78/100

Why?
- Strike equals your target exactly
- High gamma for managing reversals
- Positive theta is your friend as buyer
- Weekly = faster decay for profits
- Very liquid (tight spread)
```

## Advanced Tips

### 1. **Gamma Scalping Opportunities**
- Look for **high Gamma** contracts
- Perfect for volatile days where you catch swings
- Rebalance when Delta moves +/-0.15

### 2. **Theta Decay Strategies**
- **Buy weekly** when probability high (collect decay fast)
- **Sell monthly** to harvest slow decay over time
- **Sell on Fridays** last hour (theta acceleration)

### 3. **IV Crush Prevention**
- Check **Vega** before buying
- High IV + High Vega = risky (IV crush will hurt)
- Low IV + High Vega = opportunity (IV expansion benefit)

### 4. **Volatility Regime**
- When IV **Percentile < 20%** → Buy volatility (long vega)
- When IV **Percentile > 80%** → Sell volatility (short vega)

### 5. **Time Decay Management**
- **Days 35-21**: Slow theta (not worth the capital)
- **Days 20-8**: Medium theta (balanced)
- **Days 7-1**: Extreme theta (high risk, high reward)

## Download & Export

All results can be downloaded as CSV:
- **Full Option Data**: Strike prices, Greeks, IV, Volume, OI
- **Analysis Ready**: Use in spreadsheets, backtesting platforms
- **Filename**: `mm_contracts_SPY_20251220_143022.csv`

## Limitations & Disclaimers

⚠️ **Warnings**
- Greeks assume Black-Scholes model (not perfect in extremes)
- Real fills may differ from bid-ask mid-prices
- Stochastic volatility can make Greeks "wrong"
- Early assignment risk for American options not modeled
- Transaction costs not included in P&L calculations

## FAQ

### Q: What's the difference between weekly and monthly?
**A:** 
- **Weekly**: Gamma higher, Theta higher, Less stable
- **Monthly**: Gamma lower, Theta lower, More stable

### Q: Which MM Score threshold should I use?
**A:** 
- **>75**: Excellent contracts (rare)
- **60-75**: Good contracts (reasonable risk/reward)
- **<60**: Marginal (only use if thesis very high conviction)

### Q: Why is Probability of Profit different from Delta?
**A:** Delta is instantaneous sensitivity; Prob Profit includes time & volatility effects.

### Q: Can I use this for earnings trades?
**A:** Yes! Scanner picks high-Gamma contracts perfect for IV crush. But watch for pin risk.

### Q: What's the best contract for income?
**A:** **Sell monthly calls/puts** with MM Score >65 → High theta, Low gamma risk.

## Support
For questions or bugs, check the SECURITY.md and SYSTEM_STATUS.md files in the project.

---
**Developed by Ozy | © 2025**  
*MM Contract Scanner v1.0 - Black-Scholes Greeks Analysis Engine*
