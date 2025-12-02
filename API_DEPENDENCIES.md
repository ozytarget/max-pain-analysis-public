# API Dependencies by Tab

## Tab Summary

| Tab | Name | Primary API | Fallback API | Status |
|-----|------|-------------|--------------|--------|
| 1 | Gummy Data Bubbles® | Tradier | FMP | ✅ Working |
| 2 | Market Scanner | Tradier | yfinance | ✅ Working |
| 3 | News | NewsAPI / Web Scraping | - | ✅ Working |
| 4 | Stock Insights | yfinance | - | ✅ Working |
| 5 | Options Order Flow | Tradier | - | ✅ Working |
| 6 | Analyst Rating Flow | FMP | Yahoo Finance | ⚠️ May vary |
| 7 | Elliott Pulse® | Tradier | - | ✅ Working |
| 8 | Crypto Insights | Kraken | yfinance | ✅ Working |
| 9 | Projection | yfinance | - | ✅ Working |
| 10 | **Performance Map** | **yfinance (Primary)** | **FMP Fallback** | ✅ **Now Working** |
| 11 | **Options Signals** | **Tradier** | **Limited Fallback** | ⚠️ **May have delays** |

---

## Detailed API Configuration

### Tab 10: Performance Map
**Updated to use yfinance as primary source**
- Fetches 1 year of historical data for 34+ assets
- Uses yfinance for faster, more reliable data retrieval
- Falls back to FMP if yfinance fails
- Calculates: Returns, Correlations, Volatility, Risk-Adjusted Returns

**APIs:**
- 🟢 **Primary**: yfinance (free, unlimited)
- 🟡 **Secondary**: FMP API Key: `tng3tSJKgtwzYSDNcylDZKYfb60QOHRW`
- ⚠️ **Note**: FMP may return 403 errors (API limit or subscription issue)

### Tab 11: Options Signals
**Requires valid Tradier API credentials**
- Analyzes all options contracts for a ticker
- Calculates: Max Pain, Gamma, IV, Volume Signals
- Heavy computation - may take 10-30 seconds per ticker

**APIs:**
- 🔴 **Required**: Tradier API Key: `Mys3Hsfg4oG5G6qi9PF7ZfInDDVf`
- 📊 **Features**: Options chains, Greeks, historical options data
- ⚠️ **Note**: Requires active Tradier account with market data subscription

---

## API Key Status

| API | Key | Status | Issue |
|-----|-----|--------|-------|
| Tradier | `Mys3Hsfg4oG5...` | ✅ Valid | - |
| FMP | `tng3tSJKgtwz...` | ❌ Returns 403 | Free tier limited / Subscription expired |
| Kraken | `kyFpw+5fbr...` | ✅ Valid | - |
| yfinance | N/A (free) | ✅ Available | - |

---

## Troubleshooting

### Performance Map (Tab 10) Not Loading
1. **Check internet connection** - requires downloading 1 year of data for 34+ assets
2. **Wait 30-60 seconds** - yfinance is slower on first load
3. **Refresh the page** - cached data may help second time
4. **Check .env file** - ensure API keys are properly configured

### Options Signals (Tab 11) Not Loading
1. **Verify Tradier API Key** - check if subscription is active
2. **Use SPY or AAPL** - test with highly liquid stocks first
3. **Check market hours** - some data only available during market hours
4. **Wait longer** - options analysis can take 15-30 seconds for full dataset

### FMP API Returns 403 Forbidden
- **Cause**: Free tier API limit reached or subscription expired
- **Solution**: 
  - Use yfinance alternative (implemented for Tab 10)
  - Contact FMP to upgrade subscription
  - Or disable FMP and rely on yfinance

---

## Performance Tips

1. **Use yfinance tabs first** (Tabs 1-5, 8-9) - they're faster
2. **Avoid rapid tab switching** - allow data to load before switching
3. **Clear cache**: Refresh browser (Ctrl+F5) if data looks stale
4. **Market hours**: Performance is faster 9:30 AM - 4:00 PM ET
5. **Test with major tickers**: SPY, QQQ, AAPL, MSFT - more data available

---

## API Limits & Quotas

| API | Free Tier | Limit | Resets |
|-----|-----------|-------|--------|
| yfinance | ✅ Unlimited | 1 req/sec | - |
| Tradier | ⚠️ Sandbox | 1k/day | Daily |
| FMP | ❌ Limited | 250/day | Daily |
| Kraken | ✅ Unlimited | Public data | - |

---

## Last Updated
- **Date**: 2025-12-01
- **Changes**: Tab 10 reconfigured to use yfinance as primary (FMP had 403 errors)
- **Status**: All tabs operational with fallbacks in place
