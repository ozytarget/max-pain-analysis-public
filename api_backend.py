"""
FastAPI Backend para Max Pain Analysis App
Centraliza todas las llamadas a APIs de terceros (Polygon, Tradier, FMP)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Max Pain Analysis API",
    description="Centralized API for financial data aggregation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Configuration
retry_strategy = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)

# Create sessions with retry strategy
polygon_session = requests.Session()
polygon_session.mount("https://", adapter)

tradier_session = requests.Session()
tradier_session.mount("https://", adapter)

fmp_session = requests.Session()
fmp_session.mount("https://", adapter)

# API Keys
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "")
TRADIER_API_KEY = os.getenv("TRADIER_API_KEY", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")

# API URLs
POLYGON_BASE_URL = "https://api.polygon.io"
TRADIER_BASE_URL = "https://api.tradier.com/v1"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Headers
TRADIER_HEADERS = {"Authorization": f"Bearer {TRADIER_API_KEY}", "Accept": "application/json"}
FMP_HEADERS = {"Accept": "application/json"}

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "apis": {
            "polygon": "configured" if POLYGON_API_KEY else "not_configured",
            "tradier": "configured" if TRADIER_API_KEY else "not_configured",
            "fmp": "configured" if FMP_API_KEY else "not_configured"
        }
    }

# ============================================================================
# CURRENT PRICE ENDPOINTS
# ============================================================================

@app.get("/api/price/{ticker}")
async def get_current_price(ticker: str) -> Dict:
    """
    Get current price for a ticker
    Tries: Polygon → Tradier → FMP
    """
    ticker = ticker.upper()
    
    # Try Polygon first
    if POLYGON_API_KEY:
        try:
            url = f"{POLYGON_BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
            params = {"apiKey": POLYGON_API_KEY}
            response = polygon_session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data and data.get("status") == "OK" and "results" in data:
                results = data["results"]
                price = results.get("prevDay", {}).get("c") or results.get("lastQuote", {}).get("p")
                if price and price > 0:
                    logger.info(f"Fetched {ticker} price from Polygon: ${price:.2f}")
                    return {
                        "ticker": ticker,
                        "price": float(price),
                        "source": "polygon",
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            logger.warning(f"Polygon fetch failed for {ticker}: {str(e)}")
    
    # Try Tradier
    try:
        url = f"{TRADIER_BASE_URL}/markets/quotes"
        params = {"symbols": ticker}
        response = tradier_session.get(url, params=params, headers=TRADIER_HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and "quotes" in data and "quote" in data["quotes"]:
            quote = data["quotes"]["quote"]
            if isinstance(quote, list):
                quote = quote[0]
            price = float(quote.get("last", 0.0))
            if price > 0:
                logger.info(f"Fetched {ticker} price from Tradier: ${price:.2f}")
                return {
                    "ticker": ticker,
                    "price": price,
                    "source": "tradier",
                    "timestamp": datetime.now().isoformat()
                }
    except Exception as e:
        logger.warning(f"Tradier fetch failed for {ticker}: {str(e)}")
    
    # Try FMP
    try:
        url = f"{FMP_BASE_URL}/quote/{ticker}"
        params = {"apikey": FMP_API_KEY}
        response = fmp_session.get(url, params=params, headers=FMP_HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            price = float(data[0].get("price", 0.0))
            if price > 0:
                logger.info(f"Fetched {ticker} price from FMP: ${price:.2f}")
                return {
                    "ticker": ticker,
                    "price": price,
                    "source": "fmp",
                    "timestamp": datetime.now().isoformat()
                }
    except Exception as e:
        logger.error(f"FMP fetch failed for {ticker}: {str(e)}")
    
    logger.error(f"Unable to fetch price for {ticker} from any API")
    raise HTTPException(status_code=404, detail=f"Could not fetch price for {ticker}")

@app.get("/api/prices")
async def get_current_prices(tickers: str = Query(..., description="Comma-separated list of tickers")) -> Dict:
    """
    Get current prices for multiple tickers
    Input: tickers=SPY,QQQ,AAPL
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    prices = {}
    
    # Try Polygon batch first
    if POLYGON_API_KEY:
        try:
            url = f"{POLYGON_BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers"
            params = {"apiKey": POLYGON_API_KEY, "limit": 120}
            response = polygon_session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data and data.get("status") == "OK" and "results" in data:
                for result in data["results"]:
                    ticker = result.get("ticker", "")
                    if ticker in ticker_list:
                        price = result.get("lastQuote", {}).get("p") or result.get("prevDay", {}).get("c")
                        if price and price > 0:
                            prices[ticker] = {"price": float(price), "source": "polygon"}
                logger.info(f"Fetched {len(prices)} prices from Polygon batch")
        except Exception as e:
            logger.warning(f"Polygon batch fetch failed: {str(e)}")
    
    # Fill missing with Tradier
    missing = [t for t in ticker_list if t not in prices]
    if missing:
        try:
            url = f"{TRADIER_BASE_URL}/markets/quotes"
            params = {"symbols": ",".join(missing)}
            response = tradier_session.get(url, params=params, headers=TRADIER_HEADERS, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data and "quotes" in data and "quote" in data["quotes"]:
                quotes = data["quotes"]["quote"]
                if isinstance(quotes, dict):
                    quotes = [quotes]
                for quote in quotes:
                    ticker = quote.get("symbol", "")
                    price = float(quote.get("last", 0.0))
                    if price > 0:
                        prices[ticker] = {"price": price, "source": "tradier"}
                logger.info(f"Fetched {len([t for t in missing if t in prices])} prices from Tradier")
        except Exception as e:
            logger.warning(f"Tradier batch fetch failed: {str(e)}")
    
    # Fill remaining with FMP
    missing = [t for t in ticker_list if t not in prices]
    if missing:
        try:
            url = f"{FMP_BASE_URL}/quote/{','.join(missing)}"
            params = {"apikey": FMP_API_KEY}
            response = fmp_session.get(url, params=params, headers=FMP_HEADERS, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list):
                for item in data:
                    ticker = item.get("symbol", "")
                    price = float(item.get("price", 0.0))
                    if price > 0:
                        prices[ticker] = {"price": price, "source": "fmp"}
                logger.info(f"Fetched {len([t for t in missing if t in prices])} prices from FMP")
        except Exception as e:
            logger.error(f"FMP batch fetch failed: {str(e)}")
    
    failed = [t for t in ticker_list if t not in prices]
    if failed:
        logger.warning(f"Failed to fetch prices for: {failed}")
    
    return {
        "tickers_requested": ticker_list,
        "prices": prices,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# HISTORICAL DATA ENDPOINTS
# ============================================================================

@app.get("/api/historical/{ticker}")
async def get_historical_prices(
    ticker: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    period: str = Query("daily", description="daily or weekly")
) -> Dict:
    """
    Get historical prices for a ticker
    Tries: Polygon → FMP → Tradier
    """
    ticker = ticker.upper()
    
    # Try Polygon aggregates first
    if POLYGON_API_KEY:
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days * 1.5)
            url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
            params = {"apiKey": POLYGON_API_KEY, "sort": "asc", "limit": 120}
            response = polygon_session.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data and data.get("status") == "OK" and "results" in data:
                results = data["results"][-days:]
                prices = [float(day["c"]) for day in results]
                volumes = [int(day["v"]) for day in results]
                if prices and volumes:
                    logger.info(f"Fetched {len(prices)} historical prices for {ticker} from Polygon")
                    return {
                        "ticker": ticker,
                        "prices": prices,
                        "volumes": volumes,
                        "source": "polygon",
                        "count": len(prices),
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            logger.warning(f"Polygon historical fetch failed for {ticker}: {str(e)}")
    
    # Try FMP
    try:
        url = f"{FMP_BASE_URL}/historical-price-full/{ticker}"
        params = {"apikey": FMP_API_KEY, "timeseries": days}
        response = fmp_session.get(url, params=params, headers=FMP_HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and "historical" in data:
            historical = data["historical"][:days]
            prices = [float(day["close"]) for day in historical]
            volumes = [int(day["volume"]) for day in historical]
            if prices and volumes:
                logger.info(f"Fetched {len(prices)} historical prices for {ticker} from FMP")
                return {
                    "ticker": ticker,
                    "prices": prices,
                    "volumes": volumes,
                    "source": "fmp",
                    "count": len(prices),
                    "timestamp": datetime.now().isoformat()
                }
    except Exception as e:
        logger.warning(f"FMP historical fetch failed for {ticker}: {str(e)}")
    
    # Try Tradier
    try:
        url = f"{TRADIER_BASE_URL}/markets/history"
        params = {
            "symbol": ticker,
            "interval": period,
            "start": (datetime.now().date() - timedelta(days=days)).strftime("%Y-%m-%d")
        }
        response = tradier_session.get(url, params=params, headers=TRADIER_HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and "history" in data and "day" in data["history"]:
            history = data["history"]["day"]
            prices = [float(day["close"]) for day in history]
            volumes = [int(day["volume"]) for day in history]
            logger.info(f"Fetched {len(prices)} historical prices for {ticker} from Tradier")
            return {
                "ticker": ticker,
                "prices": prices,
                "volumes": volumes,
                "source": "tradier",
                "count": len(prices),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Tradier historical fetch failed for {ticker}: {str(e)}")
    
    logger.error(f"Unable to fetch historical data for {ticker}")
    raise HTTPException(status_code=404, detail=f"Could not fetch historical data for {ticker}")

# ============================================================================
# OPTIONS ENDPOINTS
# ============================================================================

@app.get("/api/options/{ticker}/{expiration}")
async def get_options_chain(ticker: str, expiration: str) -> Dict:
    """
    Get options chain for a ticker at specific expiration
    Expiration format: YYYY-MM-DD
    """
    ticker = ticker.upper()
    
    try:
        url = f"{TRADIER_BASE_URL}/markets/options/chains"
        params = {"symbol": ticker, "expiration": expiration, "greeks": True}
        response = tradier_session.get(url, params=params, headers=TRADIER_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and "options" in data:
            logger.info(f"Fetched options chain for {ticker} {expiration} from Tradier")
            return {
                "ticker": ticker,
                "expiration": expiration,
                "options": data["options"],
                "source": "tradier",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to fetch options for {ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Could not fetch options for {ticker}")

@app.get("/api/expirations/{ticker}")
async def get_option_expirations(ticker: str) -> Dict:
    """Get available option expiration dates for a ticker"""
    ticker = ticker.upper()
    
    try:
        url = f"{TRADIER_BASE_URL}/markets/options/expirations"
        params = {"symbol": ticker}
        response = tradier_session.get(url, params=params, headers=TRADIER_HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data and "expirations" in data and "date" in data["expirations"]:
            expirations = data["expirations"]["date"]
            current_date = datetime.now().date()
            valid_dates = [
                date for date in expirations 
                if datetime.strptime(date, "%Y-%m-%d").date() >= current_date
            ]
            logger.info(f"Fetched {len(valid_dates)} expiration dates for {ticker}")
            return {
                "ticker": ticker,
                "expirations": valid_dates,
                "source": "tradier",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to fetch expirations for {ticker}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Could not fetch expirations for {ticker}")

# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@app.get("/api/metrics/{ticker}")
async def get_financial_metrics(ticker: str) -> Dict:
    """Get financial metrics for a ticker (using FMP)"""
    ticker = ticker.upper()
    
    try:
        # Fetch from Polygon first for price/market cap
        current_price = 0.0
        market_cap = 0.0
        
        if POLYGON_API_KEY:
            try:
                url = f"{POLYGON_BASE_URL}/v1/snapshot/locale/us/markets/stocks/tickers/{ticker}"
                params = {"apiKey": POLYGON_API_KEY}
                response = polygon_session.get(url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                if data and data.get("status") == "OK" and "results" in data:
                    results = data["results"]
                    current_price = results.get("lastQuote", {}).get("p", 0) or results.get("prevDay", {}).get("c", 0)
                    market_cap = results.get("marketCap", 0)
            except Exception as e:
                logger.warning(f"Polygon metrics fetch failed: {str(e)}")
        
        # Get FMP fundamentals
        income_stmt = requests.get(f"{FMP_BASE_URL}/income-statement/{ticker}?apikey={FMP_API_KEY}").json()
        balance_sheet = requests.get(f"{FMP_BASE_URL}/balance-sheet-statement/{ticker}?apikey={FMP_API_KEY}").json()
        cash_flow = requests.get(f"{FMP_BASE_URL}/cash-flow-statement/{ticker}?apikey={FMP_API_KEY}").json()
        key_metrics = requests.get(f"{FMP_BASE_URL}/key-metrics/{ticker}?apikey={FMP_API_KEY}").json()
        
        if not (income_stmt and balance_sheet and cash_flow and key_metrics):
            raise HTTPException(status_code=404, detail=f"Incomplete metrics for {ticker}")
        
        latest_income = income_stmt[0] if income_stmt else {}
        latest_balance = balance_sheet[0] if balance_sheet else {}
        latest_cash_flow = cash_flow[0] if cash_flow else {}
        latest_metrics = key_metrics[0] if key_metrics else {}
        
        metrics = {
            "ticker": ticker,
            "current_price": current_price or latest_metrics.get("marketCap", 0),
            "market_cap": market_cap or latest_metrics.get("marketCap", 0),
            "revenue": latest_income.get("revenue", 0),
            "net_income": latest_income.get("netIncome", 0),
            "ebitda": latest_income.get("ebitda", 0),
            "roa": latest_metrics.get("roa", 0),
            "roe": latest_metrics.get("roe", 0),
            "pe_ratio": latest_metrics.get("peRatio", 0),
            "debt_to_equity": latest_metrics.get("debtToEquity", 0),
            "current_ratio": latest_metrics.get("currentRatio", 0),
            "source": "polygon+fmp",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Fetched metrics for {ticker}")
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to fetch metrics for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching metrics: {str(e)}")

# ============================================================================
# VOLATILITY ENDPOINT
# ============================================================================

@app.get("/api/volatility/{ticker}")
async def get_volatility(
    ticker: str,
    days: int = Query(30, ge=1, le=365)
) -> Dict:
    """
    Calculate volatility (standard deviation of returns) for a ticker
    """
    ticker = ticker.upper()
    
    try:
        # Get historical prices
        historical = await get_historical_prices(ticker, days=days)
        prices = historical.get("prices", [])
        
        if len(prices) < 2:
            raise HTTPException(status_code=400, detail=f"Not enough price data for {ticker}")
        
        # Calculate returns
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        # Calculate volatility (standard deviation of returns)
        import statistics
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0.0
        
        # Annualized volatility
        annualized_vol = volatility * (252 ** 0.5)  # 252 trading days
        
        logger.info(f"Calculated volatility for {ticker}: {volatility:.4f}")
        
        return {
            "ticker": ticker,
            "daily_volatility": float(volatility),
            "annualized_volatility": float(annualized_vol),
            "period_days": days,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate volatility for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating volatility: {str(e)}")

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
