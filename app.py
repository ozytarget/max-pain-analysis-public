import streamlit as st
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from typing import List, Dict, Optional, Tuple
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import multiprocessing
from scipy import stats
import plotly.express as px
import csv
import bcrypt
import sqlite3
from sklearn.linear_model import LinearRegression
from bs4 import BeautifulSoup
import socket
from scipy.stats import norm
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components
import krakenex
import base64
import threading
import os
import pytz
from time import sleep
from requests.exceptions import RequestException
from contextlib import contextmanager
from threading import Lock
from plotly.subplots import make_subplots
import yfinance as yf

# Configuración global
db_lock = threading.Lock()
AUTO_UPDATE_INTERVAL = 15
DB_TIMEOUT = 20
DB_RETRIES = 5
DB_RETRY_DELAY = 2
MARKET_TIMEZONE = pytz.timezone("America/New_York")

def get_current_date():
    return datetime.now(MARKET_TIMEZONE).date()

def get_current_datetime():
    return datetime.now(MARKET_TIMEZONE)

logging.getLogger("streamlit").setLevel(logging.ERROR)

# API Sessions
session_fmp = requests.Session()
session_tradier = requests.Session()
retry_strategy = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session_fmp.mount("https://", adapter)
session_tradier.mount("https://", adapter)
num_workers = min(100, multiprocessing.cpu_count())

# API Keys
API_KEY = "kyFpw+5fbrFIMDuWJmtkbbbr/CgH/MS63wv7dRz3rndamK/XnjNOVkgP"
PRIVATE_KEY = "7xbaBIp902rSBVdIvtfrUNbRHEHMkfMHPEf4rssz+ZwSwjUZFegjdyyYZzcE5DbBrUbtFdGRRGRjTuTnEblZWA=="
kraken = krakenex.API(key=API_KEY, secret=PRIVATE_KEY)

FMP_API_KEY = "bQ025fPNVrYcBN4KaExd1N3Xczyk44wM"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
TRADIER_API_KEY = "Mys3Hsfg4oG5G6qi9PF7ZfInDDVf"
TRADIER_BASE_URL = "https://api.tradier.com/v1"
HEADERS_FMP = {"Accept": "application/json"}
HEADERS_TRADIER = {"Authorization": f"Bearer {TRADIER_API_KEY}", "Accept": "application/json"}
PASSWORDS_DB = "auth_data/passwords.db"
CACHE_TTL = 300
MAX_RETRIES = 5
INITIAL_DELAY = 1
RISK_FREE_RATE = 0.045

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de página
st.set_page_config(
    page_title="Pro Scanner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Autenticación
def initialize_passwords_db():
    os.makedirs("auth_data", exist_ok=True)
    conn = sqlite3.connect(PASSWORDS_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS passwords 
                 (password TEXT PRIMARY KEY, usage_count INTEGER DEFAULT 0, ip1 TEXT DEFAULT '', ip2 TEXT DEFAULT '')''')
    
    c.execute("SELECT COUNT(*) FROM passwords")
    if c.fetchone()[0] == 0:
        initial_passwords = [
            ("abc234", 0, "", ""), ("def456", 0, "", ""), ("ghi789", 0, "", ""),
            ("jkl010", 0, "", ""), ("mno345", 0, "", ""), ("pqr678", 0, "", ""),
            ("stu901", 0, "", ""), ("vwx234", 0, "", ""), ("yz1234", 0, "", ""),
            ("abcd56", 0, "", ""), ("efgh78", 0, "", ""), ("ijkl90", 0, "", ""),
            ("mnop12", 0, "", ""), ("qrst34", 0, "", ""), ("uvwx56", 0, "", ""),
            ("yzab78", 0, "", ""), ("cdef90", 0, "", ""), ("ghij12", 0, "", ""),
            ("news34", 0, "", ""), ("opqr56", 0, "", ""), ("xyz789", 0, "", ""),
            ("kml456", 0, "", ""), ("nop123", 0, "", ""), ("qwe987", 0, "", ""),
            ("asd654", 0, "", ""), ("zxc321", 0, "", ""), ("bnm098", 0, "", ""),
            ("vfr765", 0, "", ""), ("test234", 0, "", ""), ("hju109", 0, "", "")
        ]
        hashed_passwords = [(bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), count, ip1, ip2) 
                           for pwd, count, ip1, ip2 in initial_passwords]
        c.executemany("INSERT OR IGNORE INTO passwords VALUES (?, ?, ?, ?)", hashed_passwords)
        logger.info("Password database initialized")
    
    conn.commit()
    conn.close()

def load_passwords():
    conn = sqlite3.connect(PASSWORDS_DB)
    c = conn.cursor()
    c.execute("SELECT password, usage_count, ip1, ip2 FROM passwords")
    passwords = {row[0]: {"usage_count": row[1], "ip1": row[2], "ip2": row[3]} for row in c.fetchall()}
    conn.close()
    return passwords

def save_passwords(passwords):
    conn = sqlite3.connect(PASSWORDS_DB)
    c = conn.cursor()
    c.execute("DELETE FROM passwords")
    c.executemany("INSERT INTO passwords VALUES (?, ?, ?, ?)", 
                  [(pwd, data["usage_count"], data["ip1"], data["ip2"]) for pwd, data in passwords.items()])
    conn.commit()
    conn.close()

def get_local_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return None

def authenticate_password(input_password):
    local_ip = get_local_ip()
    if not local_ip:
        st.error("Could not obtain local IP.")
        return False
    passwords = load_passwords()
    for hashed_pwd, data in passwords.items():
        if bcrypt.checkpw(input_password.encode('utf-8'), hashed_pwd.encode('utf-8')):
            if data["usage_count"] < 2:
                if data["ip1"] == "":
                    passwords[hashed_pwd]["ip1"] = local_ip
                elif data["ip2"] == "" and data["ip1"] != local_ip:
                    passwords[hashed_pwd]["ip2"] = local_ip
                passwords[hashed_pwd]["usage_count"] += 1
                save_passwords(passwords)
                return True
            elif data["usage_count"] == 2 and (data["ip1"] == local_ip or data["ip2"] == local_ip):
                return True
            else:
                st.error("❌ This password has already been used by two IPs.")
                return False
    st.error("❌ Incorrect password.")
    return False

initialize_passwords_db()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "intro_shown" not in st.session_state:
    st.session_state["intro_shown"] = False

if not st.session_state["intro_shown"]:
    st.session_state["intro_shown"] = True

if not st.session_state["authenticated"]:
    st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }
    .login-container {
        background: #1E1E1E;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        width: 100%;
        max-width: 400px;
        text-align: center;
        border: 1px solid rgba(0, 255, 255, 0.2);
    }
    .login-title {
        font-size: 28px;
        font-weight: 700;
        color: #00FFFF;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔒 VIP ACCESS</div>', unsafe_allow_html=True)
    password = st.text_input("Enter your password", type="password", key="login_input")
    if st.button("LogIn", key="login_button"):
        if not password:
            st.error("❌ Please enter a password.")
        elif authenticate_password(password):
            st.session_state["authenticated"] = True
            time.sleep(0.5)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Funciones de utilidad
@st.cache_data(ttl=CACHE_TTL)
def fetch_logo_url(symbol: str) -> str:
    url = f"https://logo.clearbit.com/{symbol.lower()}.com"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"data:image/png;base64,{base64.b64encode(response.content).decode('utf-8')}"
    except Exception as e:
        logger.warning(f"Failed to fetch logo for {symbol}: {e}")
    return "https://via.placeholder.com/100"

@st.cache_data(ttl=86400)
def get_top_traded_stocks() -> set:
    url = f"{FMP_BASE_URL}/stock-screener"
    params = {
        "apikey": FMP_API_KEY,
        "marketCapMoreThan": 10_000_000_000,
        "volumeMoreThan": 1_000_000,
        "exchange": "NASDAQ,NYSE",
        "limit": 100
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {stock["symbol"] for stock in data if stock.get("isActivelyTrading", True)}
    except Exception as e:
        logger.error(f"Error fetching top traded stocks: {e}")
        return {"AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "WMT", "SPY"}

@st.cache_data(ttl=86400)
def get_implied_volatility(symbol: str) -> Optional[float]:
    expiration_dates = get_expiration_dates(symbol)
    if not expiration_dates:
        return None
    nearest_exp = expiration_dates[0]
    url = f"{TRADIER_BASE_URL}/markets/options/chains"
    params = {"symbol": symbol, "expiration": nearest_exp, "greeks": "true"}
    try:
        response = requests.get(url, headers=HEADERS_TRADIER, params=params, timeout=5)
        response.raise_for_status()
        data = response.json().get("options", {}).get("option", [])
        ivs = [float(opt.get("implied_volatility", 0)) for opt in data if opt.get("implied_volatility")]
        if ivs:
            return sum(ivs) / len(ivs)
        return None
    except Exception as e:
        logger.error(f"Error fetching IV for {symbol}: {e}")
        return None

def fetch_api_data(url: str, params: Dict, headers: Dict, source: str, max_retries: int = 5) -> Optional[Dict]:
    session = session_fmp if "FMP" in source else session_tradier
    for attempt in range(max_retries):
        try:
            response = session.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if attempt < max_retries - 1:
                sleep(2 ** attempt)
            else:
                logger.error(f"{source} failed after {max_retries} attempts: {str(e)}")
                return None

@st.cache_data(ttl=60)
def get_current_price(ticker: str) -> float:
    url_tradier = f"{TRADIER_BASE_URL}/markets/quotes"
    params_tradier = {"symbols": ticker}
    try:
        response = session_tradier.get(url_tradier, params=params_tradier, headers=HEADERS_TRADIER, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and "quotes" in data and "quote" in data["quotes"]:
            quote = data["quotes"]["quote"]
            if isinstance(quote, list):
                quote = quote[0]
            price = float(quote.get("last", 0.0))
            if price > 0:
                return price
    except Exception as e:
        logger.warning(f"Failed to fetch price for {ticker}: {str(e)}")

    url_fmp = f"{FMP_BASE_URL}/quote/{ticker}"
    params_fmp = {"apikey": FMP_API_KEY}
    try:
        response = session_fmp.get(url_fmp, params=params_fmp, headers=HEADERS_FMP, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            price = float(data[0].get("price", 0.0))
            if price > 0:
                return price
    except Exception as e:
        logger.error(f"Failed to fetch price for {ticker}: {str(e)}")

    return 0.0

@st.cache_data(ttl=86400)
def get_expiration_dates(ticker: str) -> List[str]:
    url = f"{TRADIER_BASE_URL}/markets/options/expirations"
    params = {"symbol": ticker}
    try:
        response = session_tradier.get(url, params=params, headers=HEADERS_TRADIER, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and "expirations" in data and "date" in data["expirations"]:
            expiration_dates = data["expirations"]["date"]
            current_date = datetime.now().date()
            valid_dates = [date for date in expiration_dates if datetime.strptime(date, "%Y-%m-%d").date() >= current_date]
            return valid_dates
        return []
    except Exception as e:
        logger.error(f"Error fetching expiration dates for {ticker}: {str(e)}")
        return []

@st.cache_data(ttl=60)
def get_current_prices(tickers: List[str]) -> Dict[str, float]:
    prices_dict = {ticker: 0.0 for ticker in tickers}
    
    tickers_str = ",".join(tickers)
    url_tradier = f"{TRADIER_BASE_URL}/markets/quotes"
    params_tradier = {"symbols": tickers_str}
    try:
        response = session_tradier.get(url_tradier, params=params_tradier, headers=HEADERS_TRADIER, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and "quotes" in data and "quote" in data["quotes"]:
            quotes = data["quotes"]["quote"]
            if isinstance(quotes, dict):
                quotes = [quotes]
            for quote in quotes:
                ticker = quote.get("symbol", "")
                price = float(quote.get("last", 0.0))
                if ticker in prices_dict and price > 0:
                    prices_dict[ticker] = price
    except Exception as e:
        logger.warning(f"Tradier failed to fetch prices for batch: {str(e)}")

    missing_tickers = [t for t, p in prices_dict.items() if p == 0.0]
    if missing_tickers:
        url_fmp = f"{FMP_BASE_URL}/quote/{','.join(missing_tickers)}"
        params_fmp = {"apikey": FMP_API_KEY}
        try:
            response = session_fmp.get(url_fmp, params=params_fmp, headers=HEADERS_FMP, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list):
                for item in data:
                    ticker = item.get("symbol", "")
                    price = float(item.get("price", 0.0))
                    if ticker in prices_dict and price > 0:
                        prices_dict[ticker] = price
        except Exception as e:
            logger.error(f"FMP failed to fetch prices for batch: {str(e)}")

    return prices_dict

@st.cache_data(ttl=3600)
def get_metaverse_stocks() -> List[str]:
    url = "https://financialmodelingprep.com/api/v3/stock_market/actives"
    params = {"apikey": FMP_API_KEY}
    data = fetch_api_data(url, params, HEADERS_FMP, "Actives")
    if data and isinstance(data, list):
        return [stock["symbol"] for stock in data[:50]]
    return ["NVDA", "TSLA", "AAPL", "AMD", "PLTR", "META", "RBLX", "U", "COIN", "HOOD"]

@st.cache_data(ttl=CACHE_TTL)
def get_options_data(ticker: str, expiration_date: str) -> List[Dict]:
    url = f"{TRADIER_BASE_URL}/markets/options/chains"
    params = {"symbol": ticker, "expiration": expiration_date, "greeks": "true"}
    try:
        time.sleep(0.1)
        response = session_tradier.get(url, params=params, headers=HEADERS_TRADIER, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data is None or not isinstance(data, dict):
            logger.error(f"Invalid JSON response for {ticker}")
            return []
        if 'options' not in data or 'option' not in data['options']:
            logger.warning(f"No valid options data for {ticker} on {expiration_date}")
            return []
        valid_options = []
        for opt in data['options']['option']:
            if (opt.get("bid") is not None and opt.get("ask") is not None and
                isinstance(opt.get("bid"), (int, float)) and isinstance(opt.get("ask"), (int, float)) and
                opt.get("bid") > 0 and opt.get("ask") > 0):
                valid_options.append(opt)
        return valid_options
    except requests.RequestException as e:
        logger.error(f"Network error fetching options for {ticker}: {str(e)}")
        return []
    except ValueError as e:
        logger.error(f"JSON parsing error for {ticker}: {str(e)}")
        return []

@st.cache_data(ttl=CACHE_TTL)
def get_historical_prices_combined(symbol, period="daily", limit=30):
    url_fmp = f"{FMP_BASE_URL}/historical-price-full/{symbol}"
    params_fmp = {"apikey": FMP_API_KEY, "timeseries": limit}
    data_fmp = fetch_api_data(url_fmp, params_fmp, HEADERS_FMP, "FMP")
    if data_fmp and "historical" in data_fmp:
        prices = [float(day["close"]) for day in data_fmp["historical"]]
        volumes = [int(day["volume"]) for day in data_fmp["historical"]]
        if prices and volumes:
            return prices, volumes

    url_tradier = f"{TRADIER_BASE_URL}/markets/history"
    params_tradier = {"symbol": symbol, "interval": period, "start": (datetime.now().date() - timedelta(days=limit)).strftime("%Y-%m-%d")}
    data_tradier = fetch_api_data(url_tradier, params_tradier, HEADERS_TRADIER, "Tradier")
    if data_tradier and "history" in data_tradier and "day" in data_tradier["history"]:
        prices = [float(day["close"]) for day in data_tradier["history"]["day"]]
        volumes = [int(day["volume"]) for day in data_tradier["history"]["day"]]
        return prices, volumes
    
    return [], []

@st.cache_data(ttl=CACHE_TTL)
def get_stock_list_combined():
    combined_tickers = set()

    try:
        response = requests.get(
            f"{FMP_BASE_URL}/stock-screener",
            params={
                "apikey": FMP_API_KEY,
                "marketCapMoreThan": 1_000_000_000,
                "volumeMoreThan": 500_000,
                "priceMoreThan": 5,
                "exchange": "NASDAQ,NYSE"
            }
        )
        response.raise_for_status()
        data = response.json()
        fmp_tickers = [stock["symbol"] for stock in data if stock.get("isActivelyTrading", True)]
        combined_tickers.update(fmp_tickers[:200])
    except Exception as e:
        logger.error(f"FMP stock list failed: {str(e)}")

    try:
        initial_tickers = "SPY,QQQ,DIA,IWM,TSLA,AAPL,MSFT,NVDA,GOOGL,AMZN,META"
        url_tradier = f"{TRADIER_BASE_URL}/markets/quotes"
        params_tradier = {"symbols": initial_tickers}
        data_tradier = fetch_api_data(url_tradier, params_tradier, HEADERS_TRADIER, "Tradier")
        if data_tradier and "quotes" in data_tradier and "quote" in data_tradier["quotes"]:
            quotes = data_tradier["quotes"]["quote"]
            if isinstance(quotes, dict):
                quotes = [quotes]
            tradier_tickers = [
                quote["symbol"] for quote in quotes
                if quote.get("last", 0) > 5 and quote.get("volume", 0) > 500_000
            ]
            combined_tickers.update(tradier_tickers)
    except Exception as e:
        logger.error(f"Tradier stock list failed: {str(e)}")

    final_list = list(combined_tickers)
    return final_list[:200]

def analyze_contracts(ticker, expiration, current_price):
    url = f"{TRADIER_BASE_URL}/markets/options/chains"
    params = {"symbol": ticker, "expiration": expiration, "greeks": True}
    try:
        response = requests.get(url, headers=HEADERS_TRADIER, params=params, timeout=10)
        if response.status_code != 200:
            st.error(f"Error retrieving option contracts: {response.status_code}")
            return pd.DataFrame()
        options = response.json().get("options", {}).get("option", [])
        if not options:
            st.warning("No contracts available.")
            return pd.DataFrame()
        df = pd.DataFrame(options)
        for col in ['strike', 'option_type', 'open_interest', 'volume', 'bid', 'ask', 'last_volume', 'trade_date', 'bid_exchange', 'delta', 'gamma', 'break_even']:
            if col not in df.columns:
                df[col] = 0
        df['open_interest'] = pd.to_numeric(df['open_interest'], errors='coerce').fillna(0).astype(int).clip(lower=0)
        df['trade_date'] = datetime.now().strftime('%Y-%m-%d')
        df['break_even'] = df.apply(lambda row: row['strike'] + row['bid'] if row['option_type'] == 'call' else row['strike'] - row['bid'], axis=1)
        return df
    except requests.exceptions.ReadTimeout:
        st.error(f"Timeout retrieving option contracts for {ticker}")
        return pd.DataFrame()
    except requests.RequestException as e:
        st.error(f"Error retrieving option contracts for {ticker}: {str(e)}")
        return pd.DataFrame()

def style_and_sort_table(df):
    ordered_columns = ['strike', 'option_type', 'open_interest', 'volume', 'trade_date', 'bid', 'ask', 'last_volume', 'bid_exchange', 'delta', 'gamma', 'break_even']
    df = df.sort_values(by=['volume', 'open_interest'], ascending=[False, False]).head(10)
    df = df[ordered_columns]
    def highlight_row(row):
        color = 'background-color: green; color: white;' if row['option_type'] == 'call' else 'background-color: red; color: white;'
        return [color] * len(row)
    return df.style.apply(highlight_row, axis=1).format({
        'strike': '{:.2f}', 'bid': '${:.2f}', 'ask': '${:.2f}', 'last_volume': '{:,}', 'open_interest': '{:,}', 'delta': '{:.2f}', 'gamma': '{:.2f}', 'break_even': '${:.2f}'
    })

def select_best_contracts(df, current_price):
    if df.empty:
        return None, None
    df['strike_diff'] = abs(df['strike'] - current_price)
    closest_contract = df.sort_values(by=['strike_diff', 'volume', 'open_interest'], ascending=[True, False, False]).iloc[0]
    otm_calls = df[(df['option_type'] == 'call') & (df['strike'] > current_price) & (df['ask'] < 5)]
    otm_puts = df[(df['option_type'] == 'put') & (df['strike'] < current_price) & (df['ask'] < 5)]
    if not otm_calls.empty or not otm_puts.empty:
        economic_df = pd.concat([otm_calls, otm_puts])
        economic_contract = economic_df.sort_values(by=['volume', 'open_interest'], ascending=[False, False]).iloc[0]
    else:
        economic_contract = None
    return closest_contract, economic_contract

def calculate_max_pain(options_data: List[Dict]) -> Optional[float]:
    if not options_data:
        logger.warning("No options data provided for Max Pain calculation")
        return None
    strikes = {}
    for opt in options_data:
        try:
            strike = float(opt.get("strike", 0))
            oi = int(opt.get("open_interest", 0) or 0)
            opt_type = opt.get("option_type", "").upper()
            if strike not in strikes:
                strikes[strike] = {"CALL": 0, "PUT": 0}
            strikes[strike][opt_type] += oi
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid option data: {opt} - {str(e)}")
            continue
    strike_prices = sorted(strikes.keys())
    total_losses = {}
    for strike in strike_prices:
        call_loss = sum(strikes[s]["CALL"] * max(0, s - strike) for s in strike_prices)
        put_loss = sum(strikes[s]["PUT"] * max(0, strike - s) for s in strike_prices)
        total_losses[strike] = call_loss + put_loss
    if not total_losses:
        logger.warning("No valid strike prices for Max Pain calculation")
        return None
    max_pain = min(total_losses, key=total_losses.get)
    return max_pain

def calculate_support_resistance_mid(max_pain_table, current_price):
    if max_pain_table.empty or 'strike' not in max_pain_table.columns:
        return current_price, current_price, current_price
    puts = max_pain_table[max_pain_table['strike'] <= current_price]
    calls = max_pain_table[max_pain_table['strike'] > current_price]
    support_level = puts.loc[puts['total_loss'].idxmin()]['strike'] if not puts.empty else current_price
    resistance_level = calls.loc[calls['total_loss'].idxmin()]['strike'] if not calls.empty else current_price
    mid_level = (support_level + resistance_level) / 2
    return support_level, resistance_level, mid_level

def plot_max_pain_histogram_with_levels(max_pain_table, current_price):
    if max_pain_table.empty:
        fig = go.Figure()
        fig.update_layout(title="Max Pain Histogram (No Data)", template="plotly_white")
        return fig
    
    support_level, resistance_level, mid_level = calculate_support_resistance_mid(max_pain_table, current_price)
    max_pain_table['loss_category'] = max_pain_table['total_loss'].apply(
        lambda x: 'High Loss' if x > max_pain_table['total_loss'].quantile(0.75) else ('Low Loss' if x < max_pain_table['total_loss'].quantile(0.25) else 'Neutral')
    )
    color_map = {'High Loss': '#FF5733', 'Low Loss': '#28A745', 'Neutral': 'rgba(128,128,128,0.3)'}
    fig = px.bar(max_pain_table, x='strike', y='total_loss', title="Max Pain Histogram with Levels",
                 labels={'total_loss': 'Total Loss', 'strike': 'Strike Price'}, color='loss_category', color_discrete_map=color_map)
    fig.update_layout(xaxis_title="Strike Price", yaxis_title="Total Loss", template="plotly_white", font=dict(size=14, family="Open Sans"),
                      title=dict(text="📊 Analysis loss Options", font=dict(size=18), x=0.5), hovermode="x",
                      yaxis=dict(showspikes=True, spikemode="across", spikesnap="cursor", spikecolor="#FFFF00", spikethickness=1.5))
    mean_loss = max_pain_table['total_loss'].mean()
    fig.add_hline(y=mean_loss, line_width=1, line_dash="dash", line_color="#00FF00", annotation_text=f"Mean Loss: {mean_loss:.2f}", annotation_position="top right", annotation_font=dict(color="#00FF00", size=12))
    fig.add_vline(x=support_level, line_width=1, line_dash="dot", line_color="#1E90FF", annotation_text=f"Support: {support_level:.2f}", annotation_position="top left", annotation_font=dict(color="#1E90FF", size=10))
    fig.add_vline(x=resistance_level, line_width=1, line_dash="dot", line_color="#FF4500", annotation_text=f"Resistance: {resistance_level:.2f}", annotation_position="top right", annotation_font=dict(color="#FF4500", size=10))
    fig.add_vline(x=mid_level, line_width=1, line_dash="solid", line_color="#FFD700", annotation_text=f"Mid Level: {mid_level:.2f}", annotation_position="top right", annotation_font=dict(color="#FFD700", size=8))
    return fig

def get_option_chains(ticker, expiration):
    url = f"{TRADIER_BASE_URL}/markets/options/chains"
    params = {"symbol": ticker, "expiration": expiration, "greeks": True}
    response = requests.get(url, headers=HEADERS_TRADIER, params=params)
    if response.status_code == 200:
        return response.json().get("options", {}).get("option", [])
    st.error("Error retrieving option chains.")
    return []

def calculate_score(df, current_price, volatility=0.2):
    df['score'] = (df['open_interest'] * df['volume']) / (abs(df['strike'] - current_price) + volatility)
    return df.sort_values(by='score', ascending=False)

def display_cards(df):
    top_5_vol = df.sort_values(by='volume', ascending=False).head(5)
    st.markdown("### Top 5")
    for i, row in top_5_vol.iterrows():
        st.markdown(f"""
        **Strike:** {row['strike']}  
        **Type:** {'Call' if row['option_type'] == 'call' else 'Put'}  
        **Volume:** {row['volume']}  
        **Open Interest:** {row['open_interest']}  
        **Score:** {row['score']:.2f}  
        """)

def plot_histogram(df):
    fig = px.bar(df, x='strike', y='score', color='option_type', title="Score by Strike (Calls and Puts)",
                 labels={'score': 'Relevance Score', 'strike': 'Strike Price'}, text='score',
                 color_discrete_map={'call': '#00FF00', 'put': '#FF00FF'})
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', marker=dict(line=dict(width=0.5, color='black')))
    fig.update_layout(plot_bgcolor='black', font=dict(color='white', size=12), xaxis=dict(showgrid=True, gridcolor='gray'),
                      yaxis=dict(showgrid=True, gridcolor='gray'), xaxis_title="Strike Price", yaxis_title="Relevance Score")
    support_level = df['strike'].iloc[0]
    resistance_level = df['strike'].iloc[-1]
    fig.add_hline(y=support_level, line_width=1, line_dash="dot", line_color="#1E90FF", annotation_text=f"Support: {support_level:.2f}", annotation_position="bottom left", annotation_font=dict(size=10, color="#1E90FF"))
    fig.add_hline(y=resistance_level, line_width=1, line_dash="dot", line_color="#FF4500", annotation_text=f"Resistance: {resistance_level:.2f}", annotation_position="top left", annotation_font=dict(size=10, color="#FF4500"))
    return fig

def detect_touched_strikes(strikes, historical_prices):
    touched_strikes = set()
    cleaned_prices = [float(p) for p in historical_prices if isinstance(p, (int, float, str)) and str(p).replace('.', '', 1).isdigit()]
    if len(cleaned_prices) < 2:
        return touched_strikes
    for strike in strikes:
        for i in range(1, len(cleaned_prices)):
            if (cleaned_prices[i-1] < strike <= cleaned_prices[i]) or (cleaned_prices[i-1] > strike >= cleaned_prices[i]):
                touched_strikes.add(strike)
    return touched_strikes

def calculate_max_pain_optimized(options_data):
    if not options_data:
        return None
    strikes = {}
    for option in options_data:
        strike = float(option["strike"])
        oi = int(option.get("open_interest", 0) or 0)
        volume = int(option.get("volume", 0) or 0)
        option_type = option["option_type"].upper()
        if strike not in strikes:
            strikes[strike] = {"CALL": {"OI": 0, "Volume": 0}, "PUT": {"OI": 0, "Volume": 0}}
        strikes[strike][option_type]["OI"] += oi
        strikes[strike][option_type]["Volume"] += volume
    strike_prices = sorted(strikes.keys())
    total_losses = {}
    for strike in strike_prices:
        loss_call = sum((strikes[s]["CALL"]["OI"] + strikes[s]["CALL"]["Volume"]) * max(0, s - strike) for s in strike_prices)
        loss_put = sum((strikes[s]["PUT"]["OI"] + strikes[s]["PUT"]["Volume"]) * max(0, strike - s) for s in strike_prices)
        total_losses[strike] = loss_call + loss_put
    return min(total_losses, key=total_losses.get) if total_losses else None

def gamma_exposure_chart(processed_data, current_price, touched_strikes):
    strikes = sorted(processed_data.keys())
    gamma_calls = [processed_data[s]["CALL"]["OI"] * processed_data[s]["CALL"]["Gamma"] * current_price for s in strikes]
    gamma_puts = [-processed_data[s]["PUT"]["OI"] * processed_data[s]["PUT"]["Gamma"] * current_price for s in strikes]
    call_colors = ["grey" if s in touched_strikes else "#7DF9FF" for s in strikes]
    put_colors = ["orange" if s in touched_strikes else "red" for s in strikes]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=strikes, y=gamma_calls, name="Gummy CALL", marker=dict(color=call_colors), width=0.4, hovertemplate="Gummy CALL: %{y:.2f}"))
    fig.add_trace(go.Bar(x=strikes, y=gamma_puts, name="Gummy PUT", marker=dict(color=put_colors), width=0.4, hovertemplate="Gummy PUT: %{y:.2f}"))

    y_min = min(gamma_calls + gamma_puts) * 1.1
    y_max = max(gamma_calls + gamma_puts) * 1.1
    fig.add_trace(go.Scatter(x=[current_price, current_price], y=[y_min, y_max], mode="lines", line=dict(width=1, dash="dot", color="#39FF14"),
                            name="Current Price", hovertemplate="", showlegend=False, hoverlabel=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)", font=dict(color="#39FF14", size=12))))

    fig.add_annotation(x=current_price, y=y_max * 0.95, text=f"Price: ${current_price:.2f}", showarrow=False, font=dict(color="#39FF14", size=10),
                      bgcolor="rgba(0,0,0,0.5)", bordercolor="#39FF14", borderwidth=1, borderpad=4)

    fig.update_traces(hoverlabel=dict(bgcolor="rgba(0,0,0,0.1)", bordercolor="rgba(255,255,255,0.3)", font=dict(color="white", size=12)))
    fig.update_layout(title="GUMMY EXPOSURE", xaxis_title="Strike", yaxis_title="Gummy Exposure", template="plotly_dark", hovermode="x",
                     xaxis=dict(tickmode="array", tickvals=strikes, ticktext=[f"{s:.2f}" for s in strikes], rangeslider=dict(visible=False), showgrid=False),
                     yaxis=dict(showgrid=False), bargap=0.2, barmode="relative")
    return fig

def plot_skew_analysis_with_totals(options_data, current_price=None):
    strikes = [float(option["strike"]) for option in options_data]
    iv = [float(option.get("implied_volatility", 0)) * 100 for option in options_data]
    option_type = [option["option_type"].upper() for option in options_data]
    open_interest = [int(option.get("open_interest", 0) or 0) for option in options_data]
    
    total_calls = sum(oi for oi, ot in zip(open_interest, option_type) if ot == "CALL")
    total_puts = sum(oi for oi, ot in zip(open_interest, option_type) if ot == "PUT")
    total_volume_calls = sum(int(option.get("volume", 0)) for option in options_data if option["option_type"].upper() == "CALL")
    total_volume_puts = sum(int(option.get("volume", 0)) for option in options_data if option["option_type"].upper() == "PUT")
    
    adjusted_iv = [iv[i] + (open_interest[i] * 0.01) if option_type[i] == "CALL" else -(iv[i] + (open_interest[i] * 0.01)) for i in range(len(iv))]
    
    skew_df = pd.DataFrame({
        "Strike": strikes,
        "Adjusted IV (%)": adjusted_iv,
        "Option Type": option_type,
        "Open Interest": open_interest
    })
    skew_df["Open Interest"] = skew_df["Open Interest"].fillna(0).astype(int).clip(lower=0)
    
    fig = px.scatter(skew_df, x="Strike", y="Adjusted IV (%)", color="Option Type", size="Open Interest", size_max=30,
                    custom_data=["Strike", "Option Type", "Open Interest", "Adjusted IV (%)"],
                    title=f"IV Analysis<br><span style='font-size:16px;'> CALLS: {total_calls} | PUTS: {total_puts} | VC {total_volume_calls} | VP {total_volume_puts}</span>",
                    labels={"Option Type": "Contract Type"}, color_discrete_map={"CALL": "blue", "PUT": "red"})
    fig.update_traces(hovertemplate="<b>Strike:</b> %{customdata[0]:.2f}<br><b>Type:</b> %{customdata[1]}<br><b>Open Interest:</b> %{customdata[2]:,}<br><b>Adjusted IV:</b> %{customdata[3]:.2f}%")
    fig.update_layout(xaxis_title="Strike Price", yaxis_title="Gummy Bubbles® (%)", legend_title="Option Type", template="plotly_white", title_x=0.5)

    if current_price is not None and options_data:
        strikes_dict = {}
        for option in options_data:
            strike = float(option["strike"])
            oi = int(option.get("open_interest", 0) or 0)
            opt_type = option["option_type"].upper()
            if strike not in strikes_dict:
                strikes_dict[strike] = {"CALL": 0, "PUT": 0}
            strikes_dict[strike][opt_type] += oi
        strike_prices = sorted(strikes_dict.keys())
        total_losses = {}
        for strike in strike_prices:
            loss_call = sum((strikes_dict[s]["CALL"] * max(0, s - strike)) for s in strike_prices)
            loss_put = sum((strikes_dict[s]["PUT"] * max(0, strike - s)) for s in strike_prices)
            total_losses[strike] = loss_call + loss_put
        max_pain = min(total_losses, key=total_losses.get) if total_losses else None

        avg_iv_calls = sum(iv[i] + (open_interest[i] * 0.01) for i, ot in enumerate(option_type) if ot == "CALL") / max(1, sum(1 for ot in option_type if ot == "CALL"))
        avg_iv_puts = sum(-(iv[i] + (open_interest[i] * 0.01)) for i, ot in enumerate(option_type) if ot == "PUT") / max(1, sum(1 for ot in option_type if ot == "PUT"))

        call_open_interest = total_calls
        put_open_interest = total_puts
        scale_factor = 5000
        call_size = max(5, min(30, call_open_interest / scale_factor))
        put_size = max(5, min(30, put_open_interest / scale_factor))

        if current_price is not None and max_pain is not None:
            calls_data = [opt for opt in options_data if opt["option_type"].upper() == "CALL"]
            puts_data = [opt for opt in options_data if opt["option_type"].upper() == "PUT"]
            closest_call = min(calls_data, key=lambda x: abs(float(x["strike"]) - current_price), default=None)
            closest_put = min(puts_data, key=lambda x: abs(float(x["strike"]) - current_price), default=None)

            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            exp_date = datetime.strptime(options_data[0].get("expiration_date") or options_data[0].get("expirationDate"), "%Y-%m-%d")
            days_to_expiration = (exp_date - today).days

            if closest_call:
                call_strike = float(closest_call["strike"])
                call_data = {
                    call_strike: {
                        'bid': float(closest_call.get("bid", 0)),
                        'ask': float(closest_call.get("ask", 0)),
                        'delta': float(closest_call.get("greeks", {}).get("delta", 0.5)),
                        'gamma': float(closest_call.get("greeks", {}).get("gamma", 0.02)),
                        'theta': float(closest_call.get("greeks", {}).get("theta", -0.01)),
                        'iv': float(closest_call.get("implied_volatility", 0.2)),
                        'open_interest': int(closest_call.get("open_interest", 0)),
                        'intrinsic': max(current_price - call_strike, 0)
                    }
                }
                rr_calls, profit_calls, prob_otm_calls, _ = calculate_special_monetization(call_data, current_price, days_to_expiration)
                percent_change_calls = ((current_price - max_pain) / max_pain) * 100 if max_pain != 0 else 0
                call_loss = abs(current_price - max_pain) * total_calls if current_price < max_pain else (current_price - max_pain) * total_calls
                potential_move_calls = abs(current_price - max_pain)
                direction_calls = "Down" if current_price > max_pain else "Up"
            else:
                rr_calls, profit_calls, prob_otm_calls, percent_change_calls, call_loss, potential_move_calls, direction_calls = 0, 0, 0, 0, 0, 0, "N/A"

            if closest_put:
                put_strike = float(closest_put["strike"])
                put_data = {
                    put_strike: {
                        'bid': float(closest_put.get("bid", 0)),
                        'ask': float(closest_put.get("ask", 0)),
                        'delta': float(closest_put.get("greeks", {}).get("delta", -0.5)),
                        'gamma': float(closest_put.get("greeks", {}).get("gamma", 0.02)),
                        'theta': float(closest_put.get("greeks", {}).get("theta", -0.01)),
                        'iv': float(closest_put.get("implied_volatility", 0.2)),
                        'open_interest': int(closest_put.get("open_interest", 0)),
                        'intrinsic': max(put_strike - current_price, 0)
                    }
                }
                rr_puts, profit_puts, prob_otm_puts, _ = calculate_special_monetization(put_data, current_price, days_to_expiration)
                percent_change_puts = ((max_pain - current_price) / max_pain) * 100 if max_pain != 0 else 0
                put_loss = abs(max_pain - current_price) * total_puts if current_price > max_pain else (max_pain - current_price) * total_puts
                potential_move_puts = abs(max_pain - current_price)
                direction_puts = "Up" if current_price < max_pain else "Down"
            else:
                rr_puts, profit_puts, prob_otm_puts, percent_change_puts, put_loss, potential_move_puts, direction_puts = 0, 0, 0, 0, 0, 0, "N/A"

            if call_open_interest > 0 and closest_call:
                fig.add_scatter(x=[current_price], y=[avg_iv_calls], mode="markers", name="Current Price (CALLs)",
                              marker=dict(size=call_size, color="yellow", opacity=0.45, symbol="circle"),
                              hovertemplate=(f"Current Price (CALLs): {current_price:.2f}<br>Adjusted IV: {avg_iv_calls:.2f}%<br>"
                                           f"Open Interest: {call_open_interest:,}<br>% to Max Pain: {percent_change_calls:.2f}%<br>"
                                           f"R/R: {rr_calls:.2f}<br>Est. Loss: ${call_loss:,.2f}<br>"
                                           f"Potential Move: ${potential_move_calls:.2f}<br>Direction: {direction_calls}"))

            if put_open_interest > 0 and closest_put:
                fig.add_scatter(x=[current_price], y=[avg_iv_puts], mode="markers", name="Current Price (PUTs)",
                              marker=dict(size=put_size, color="yellow", opacity=0.45, symbol="circle"),
                              hovertemplate=(f"Current Price (PUTs): {current_price:.2f}<br>Adjusted IV: {avg_iv_puts:.2f}%<br>"
                                           f"Open Interest: {put_open_interest:,}<br>% to Max Pain: {percent_change_puts:.2f}%<br>"
                                           f"R/R: {rr_puts:.2f}<br>Est. Loss: ${put_loss:,.2f}<br>"
                                           f"Potential Move: ${potential_move_puts:.2f}<br>Direction: {direction_puts}"))

        if max_pain is not None:
            fig.add_scatter(x=[max_pain], y=[0], mode="markers", name="Max Pain",
                          marker=dict(size=15, color="white", symbol="circle"), hovertemplate=f"Max Pain: {max_pain:.2f}")

    return fig, total_calls, total_puts

def calculate_special_monetization(data: Dict, current_price: float, days_to_expiration: int) -> Tuple[float, float, float, str]:
    strike = list(data.keys())[0]
    option_type = 'CALL' if data[strike]['delta'] > 0 else 'PUT'
    mid_price = (data[strike]['bid'] + data[strike]['ask']) / 2
    delta = abs(data[strike]['delta'])
    gamma = data[strike]['gamma']
    theta = data[strike]['theta']
    iv = data[strike]['iv']
    intrinsic = data[strike]['intrinsic']
    open_interest = data[strike]['open_interest']
    
    gamma_iv_index = gamma * iv * (open_interest / 1000000.0) if gamma > 0 and iv > 0 else 0.001
    t = days_to_expiration / 365.0
    d1 = (np.log(current_price / strike) + (RISK_FREE_RATE + 0.5 * iv**2) * t) / (iv * np.sqrt(t))
    prob_otm = norm.cdf(-d1) if option_type == "PUT" else norm.cdf(d1)
    
    direction_factor = 1 if (option_type == "CALL" and current_price > strike) or (option_type == "PUT" and current_price < strike) else 0.5
    monetization_factor = mid_price * (1 + abs(theta) / (gamma + 0.001)) * direction_factor
    
    potential_profit = monetization_factor * 100
    risk = mid_price * 100 * (1 - prob_otm) * (1 + gamma * 5)
    rr_ratio = potential_profit / risk if risk > 0 else 10.0
    action = "SELL" if prob_otm > 0.5 else "BUY"
    
    return rr_ratio, potential_profit, prob_otm, action

def fetch_google_news(keywords):
    base_url = "https://www.google.com/search"
    query = "+".join(keywords)
    params = {"q": query, "tbm": "nws", "tbs": "qdr:h"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        news = []
        articles = soup.select("div.dbsr") or soup.select("div.Gx5Zad.fP1Qef.xpd.EtOod.pkphOe")
        for article in articles[:20]:
            title_tag = article.select_one("div.JheGif.nDgy9d") or article.select_one("div.BNeawe.vvjwJb.AP7Wnd")
            link_tag = article.a
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = link_tag["href"]
                time_tag = article.select_one("span.WG9SHc")
                time_posted = time_tag.text if time_tag else "Just now"
                news.append({"title": title, "link": link, "time": time_posted})
        return news
    except Exception as e:
        st.warning(f"Error fetching Data News: {e}")
        return []

def fetch_bing_news(keywords):
    base_url = "https://www.bing.com/news/search"
    query = " ".join(keywords)
    params = {"q": query, "qft": "+filterui:age-lt24h"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        news = []
        articles = soup.select("a.title")
        for article in articles[:20]:
            title = article.text.strip()
            link = article["href"]
            news.append({"title": title, "link": link, "time": "Recently"})
        return news
    except Exception as e:
        st.warning(f"Error fetching Bing News: {e}")
        return []

def calculate_retail_sentiment(news):
    if not news:
        return 0.5, "Neutral"
    
    positive_keywords = ["up", "bullish", "gain", "rise", "surge", "strong", "rally", "positive", "growth"]
    negative_keywords = ["down", "bearish", "loss", "drop", "fall", "crash", "weak", "decline", "negative"]
    
    sentiment_score = 0
    total_articles = len(news)
    
    for article in news:
        title = article["title"].lower()
        positive_count = sum(1 for word in positive_keywords if word in title)
        negative_count = sum(1 for word in negative_keywords if word in title)
        sentiment_score += (positive_count - negative_count)
    
    max_possible_score = max(total_articles, 1)
    normalized_score = (sentiment_score + max_possible_score) / (2 * max_possible_score)
    normalized_score = max(0, min(1, normalized_score))
    
    if normalized_score > 0.7:
        sentiment_text = "Very Bullish"
    elif normalized_score > 0.5:
        sentiment_text = "Bullish"
    elif normalized_score < 0.3:
        sentiment_text = "Very Bearish"
    elif normalized_score < 0.5:
        sentiment_text = "Bearish"
    else:
        sentiment_text = "Neutral"
    
    return normalized_score, sentiment_text

def calculate_volatility_sentiment(news):
    if not news:
        return 0, "Stable"
    
    high_volatility_keywords = ["crash", "surge", "volatile", "plunge", "spike", "wild", "turmoil", "shock", "boom"]
    low_volatility_keywords = ["steady", "calm", "stable", "flat", "unchanged", "quiet", "consistent"]
    
    volatility_score = 0
    total_articles = len(news)
    
    for article in news:
        title = article["title"].lower()
        high_vol_count = sum(1 for word in high_volatility_keywords if word in title)
        low_vol_count = sum(1 for word in low_volatility_keywords if word in title)
        volatility_score += (high_vol_count - low_vol_count)
    
    max_possible_score = max(total_articles, 1)
    normalized_score = (volatility_score + max_possible_score) / (2 * max_possible_score) * 100
    normalized_score = max(0, min(100, normalized_score))
    
    if normalized_score > 75:
        volatility_text = "Very High Volatility"
    elif normalized_score > 50:
        volatility_text = "High Volatility"
    elif normalized_score < 25:
        volatility_text = "Low Volatility"
    elif normalized_score < 50:
        volatility_text = "Moderate Volatility"
    else:
        volatility_text = "Stable"
    
    return normalized_score, volatility_text

def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    prices = np.array(prices)
    if len(prices) < period + 1:
        return None
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    return 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss != 0 else 100

def calculate_sma(prices: List[float], period: int = 20) -> Optional[float]:
    prices = np.array(prices)
    if len(prices) < period:
        return None
    return np.mean(prices[-period:])

def calculate_momentum(prices: List[float], vol_historical: float) -> float:
    if len(prices) < 2:
        return 0.0
    price_change = (prices[-1] - prices[-2]) / prices[-2]
    return price_change / vol_historical if vol_historical > 0 else 0.0

def scan_stock_batch(tickers: List[str], scan_type: str, breakout_period=10, volume_threshold=2.0) -> List[Dict]:
    prices_dict = get_current_prices(tickers)
    results = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(get_historical_prices_combined, ticker, limit=breakout_period+1): ticker for ticker in tickers}
        for future in futures:
            ticker = futures[future]
            try:
                prices, volumes = future.result()
                if len(prices) <= breakout_period or not volumes:
                    continue
                current_price = prices_dict.get(ticker, 0.0)
                if current_price == 0.0:
                    continue
                prices = np.array(prices)
                volumes = np.array(volumes)
                rsi = calculate_rsi(prices)
                sma = calculate_sma(prices)
                avg_volume = np.mean(volumes)
                current_volume = volumes[-1]
                recent_high = np.max(prices[-breakout_period:])
                recent_low = np.min(prices[-breakout_period:])
                last_price = prices[-1]
                near_support = abs(last_price - recent_low) / recent_low <= 0.05
                near_resistance = abs(last_price - recent_high) / recent_high <= 0.05
                breakout_type = "Up" if last_price > recent_high else "Down" if last_price < recent_low else None
                possible_change = (recent_low - last_price) / last_price * 100 if near_support else (recent_high - last_price) / last_price * 100 if near_resistance else None

                if scan_type == "Bullish (Upward Momentum)" and sma and last_price > sma and rsi and rsi < 70:
                    results.append({"Symbol": ticker, "Last Price": last_price, "SMA": round(sma, 2), "RSI": round(rsi, 2), "Volume": current_volume, "Breakout Type": breakout_type, "Possible Change (%)": round(possible_change, 2) if possible_change else None})
                elif scan_type == "Bearish (Downward Momentum)" and sma and last_price < sma and rsi and rsi > 30:
                    results.append({"Symbol": ticker, "Last Price": last_price, "SMA": round(sma, 2), "RSI": round(rsi, 2), "Volume": current_volume, "Breakout Type": breakout_type, "Possible Change (%)": round(possible_change, 2) if possible_change else None})
                elif scan_type == "Breakouts" and breakout_type:
                    results.append({"Symbol": ticker, "Breakout Type": breakout_type, "Last Price": last_price, "Recent High": recent_high, "Recent Low": recent_low, "Volume": current_volume, "Possible Change (%)": round(possible_change, 2) if possible_change else None})
                elif scan_type == "Unusual Volume" and current_volume > volume_threshold * avg_volume:
                    results.append({"Symbol": ticker, "Volume": current_volume, "Avg Volume": avg_volume, "Last Price": last_price})
            except Exception as e:
                logger.error(f"Error scanning {ticker}: {e}")
    return results

@st.cache_data(ttl=300)
def process_options_data(ticker: str, expiration_date: str) -> Tuple[Dict, set, float, pd.DataFrame]:
    options_data = get_options_data(ticker, expiration_date)
    if not options_data:
        return {}, set(), None, pd.DataFrame(columns=["strike", "total_loss"])
    
    processed_data = {}
    strikes_data = {}
    for opt in options_data:
        if not isinstance(opt, dict):
            continue
        strike = float(opt.get("strike", 0))
        opt_type = opt.get("option_type", "").upper()
        oi = int(opt.get("open_interest", 0))
        gamma = float(opt.get("greeks", {}).get("gamma", 0)) if isinstance(opt.get("greeks", {}), dict) else 0
        if strike not in processed_data:
            processed_data[strike] = {"CALL": {"OI": 0, "Gamma": 0}, "PUT": {"OI": 0, "Gamma": 0}}
            strikes_data[strike] = {"CALL": 0, "PUT": 0}
        processed_data[strike][opt_type]["OI"] += oi
        processed_data[strike][opt_type]["Gamma"] += gamma
        strikes_data[strike][opt_type] += oi
    
    prices, _ = get_historical_prices_combined(ticker)
    touched_strikes = detect_touched_strikes(processed_data.keys(), prices)
    max_pain = calculate_max_pain_optimized(options_data)
    
    strike_prices = sorted(strikes_data.keys())
    max_pain_data = []
    for strike in strike_prices:
        call_loss = sum((strikes_data[s]["CALL"] * max(0, s - strike)) for s in strike_prices)
        put_loss = sum((strikes_data[s]["PUT"] * max(0, strike - s)) for s in strike_prices)
        total_loss = call_loss + put_loss
        max_pain_data.append({"strike": strike, "total_loss": total_loss})
    max_pain_df = pd.DataFrame(max_pain_data)
    
    return processed_data, touched_strikes, max_pain, max_pain_df

@st.cache_data(ttl=300)
def process_order_flow_data(ticker: str, expiration_date: str, current_price: float) -> Tuple[pd.DataFrame, float, float, float, str]:
    option_data = get_option_data(ticker, expiration_date)
    if option_data.empty:
        return pd.DataFrame(), 0.0, 0.0, 0.0, "N/A"
    
    option_data_list = option_data.to_dict('records')
    max_pain = calculate_max_pain_optimized(option_data_list)
    
    all_strikes = sorted(set(option_data["strike"]))
    buy_calls = option_data[(option_data["option_type"] == "call") & (option_data["action"] == "buy")]
    sell_calls = option_data[(option_data["option_type"] == "call") & (option_data["action"] == "sell")]
    buy_puts = option_data[(option_data["option_type"] == "put") & (option_data["action"] == "buy")]
    sell_puts = option_data[(option_data["option_type"] == "put") & (option_data["action"] == "sell")]
    
    order_flow_df = pd.DataFrame({
        "Strike": all_strikes,
        "Buy_Call_OI": buy_calls.set_index("strike")["open_interest"].reindex(all_strikes, fill_value=0),
        "Sell_Call_OI": sell_calls.set_index("strike")["open_interest"].reindex(all_strikes, fill_value=0),
        "Buy_Put_OI": buy_puts.set_index("strike")["open_interest"].reindex(all_strikes, fill_value=0),
        "Sell_Put_OI": sell_puts.set_index("strike")["open_interest"].reindex(all_strikes, fill_value=0)
    })
    
    total_call_oi = sum(row["open_interest"] for row in option_data_list if row["option_type"] == "call" and row["strike"] > current_price)
    total_put_oi = sum(row["open_interest"] for row in option_data_list if row["option_type"] == "put" and row["strike"] < current_price)
    total_oi = max(total_call_oi + total_put_oi, 1)
    gamma_calls = sum(row["greeks"]["gamma"] * row["open_interest"] if isinstance(row["greeks"], dict) and "gamma" in row["greeks"] else 0
                      for row in option_data_list if row["option_type"] == "call" and "greeks" in row)
    gamma_puts = sum(row["greeks"]["gamma"] * row["open_interest"] if isinstance(row["greeks"], dict) and "gamma" in row["greeks"] else 0
                     for row in option_data_list if row["option_type"] == "put" and "greeks" in row)
    net_gamma = gamma_calls - gamma_puts
    
    oi_pressure = (total_call_oi - total_put_oi) / total_oi
    gamma_factor = net_gamma / 10000
    mm_score = oi_pressure * 0.6 + gamma_factor * 0.4
    direction_mm = "Up" if mm_score > 0.1 else "Down" if mm_score < -0.1 else "Neutral"
    
    return order_flow_df, total_call_oi, total_put_oi, net_gamma, direction_mm

@st.cache_data(ttl=300)
def process_rating_flow_data(ticker: str, expiration_date: str, current_price: float) -> Tuple[List[Dict], float, float]:
    options_data = get_options_data(ticker, expiration_date)
    if not options_data:
        return [], 0.0, 0.0
    
    strikes_data = {}
    for opt in options_data:
        if not isinstance(opt, dict):
            continue
        strike = float(opt.get("strike", 0))
        opt_type = opt.get("option_type", "").upper()
        oi = int(opt.get("open_interest", 0))
        if strike not in strikes_data:
            strikes_data[strike] = {"CALL": 0, "PUT": 0}
        strikes_data[strike][opt_type] += oi
    
    strike_prices = sorted(strikes_data.keys())
    min_loss = float('inf')
    max_pain = None
    call_loss_at_max_pain = 0
    put_loss_at_max_pain = 0
    for test_strike in strike_prices:
        call_loss = sum(max(0, s - test_strike) * strikes_data[s]["CALL"] for s in strike_prices)
        put_loss = sum(max(0, test_strike - s) * strikes_data[s]["PUT"] for s in strike_prices)
        total_loss = call_loss + put_loss
        if total_loss < min_loss:
            min_loss = total_loss
            max_pain = test_strike
            call_loss_at_max_pain = call_loss
            put_loss_at_max_pain = put_loss
    
    mm_gain = (call_loss_at_max_pain + put_loss_at_max_pain) * 100
    
    return options_data, max_pain, mm_gain

def get_option_data(symbol: str, expiration_date: str) -> pd.DataFrame:
    url = f"{TRADIER_BASE_URL}/markets/options/chains"
    params = {"symbol": symbol, "expiration": expiration_date, "greeks": "true"}
    try:
        response = requests.get(url, headers=HEADERS_TRADIER, params=params, timeout=10)
        if response.status_code != 200:
            st.error(f"Error al obtener los datos de opciones. Código de estado: {response.status_code}")
            return pd.DataFrame()
        
        data = response.json()
        if data is None or not isinstance(data, dict):
            st.error(f"Datos de opciones inválidos para {symbol}")
            return pd.DataFrame()
        
        if 'options' in data and isinstance(data['options'], dict) and 'option' in data['options']:
            options = data['options']['option']
            if not options:
                st.warning(f"No se encontraron contratos de opciones para {symbol} en {expiration_date}")
                return pd.DataFrame()
            df = pd.DataFrame(options)
            df['action'] = df.apply(lambda row: "buy" if (row.get("bid", 0) > 0 and row.get("ask", 0) > 0) else "sell", axis=1)
            return df
        
        st.error(f"No se encontraron datos de opciones válidos en la respuesta para {symbol}")
        return pd.DataFrame()
    
    except requests.RequestException as e:
        st.error(f"Error de red al obtener datos de opciones para {symbol}: {str(e)}")
        return pd.DataFrame()
    except ValueError as e:
        st.error(f"Error al procesar la respuesta JSON para {symbol}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def fetch_web_sentiment(ticker: str) -> float:
    try:
        keywords = [ticker]
        news = fetch_google_news(keywords)
        if not news:
            return 0.5
        
        sentiment_score, _ = calculate_retail_sentiment(news)
        return sentiment_score
    
    except Exception as e:
        logger.error(f"Error fetching sentiment for {ticker}: {str(e)}")
        return 0.5

@st.cache_data(ttl=60)
def get_daily_movement(ticker: str) -> Tuple[float, float]:
    try:
        prices, _ = get_historical_prices_combined(ticker, period="daily", limit=5)
        if not prices or len(prices) < 2:
            return 0.02, 0.0
        
        prices = np.array(prices)
        daily_returns = np.diff(prices) / prices[:-1]
        
        daily_range = np.std(daily_returns) * np.sqrt(252) / np.sqrt(252)
        daily_range = max(0.005, min(0.1, daily_range))
        
        momentum = daily_returns[-1] if len(daily_returns) > 0 else 0.0
        momentum = max(-0.05, min(0.05, momentum))
        
        return daily_range, momentum
    
    except Exception as e:
        logger.error(f"Error calculating daily movement for {ticker}: {str(e)}")
        return 0.02, 0.0

def init_db():
    with db_lock:
        with sqlite3.connect("options_tracker.db", timeout=DB_TIMEOUT) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assigned_contracts'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.execute("PRAGMA table_info(assigned_contracts)")
                columns = [info[1] for info in cursor.fetchall()]
                if 'preference' in columns:
                    cursor.execute("""
                        CREATE TABLE assigned_contracts_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticker TEXT NOT NULL,
                            strike REAL NOT NULL,
                            option_type TEXT NOT NULL,
                            expiration_date TEXT NOT NULL,
                            assigned_price REAL NOT NULL,
                            current_price REAL,
                            assigned_at TIMESTAMP NOT NULL,
                            profit_loss_percent REAL,
                            last_updated TIMESTAMP,
                            closed BOOLEAN DEFAULT FALSE
                        )
                    """)
                    cursor.execute("""
                        INSERT INTO assigned_contracts_new (
                            id, ticker, strike, option_type, expiration_date, assigned_price,
                            current_price, assigned_at, profit_loss_percent, last_updated, closed
                        )
                        SELECT id, ticker, strike, option_type, expiration_date, assigned_price,
                               current_price, assigned_at, profit_loss_percent, last_updated, closed
                        FROM assigned_contracts
                    """)
                    cursor.execute("DROP TABLE assigned_contracts")
                    cursor.execute("ALTER TABLE assigned_contracts_new RENAME TO assigned_contracts")
                    conn.commit()
            else:
                cursor.execute("""
                    CREATE TABLE assigned_contracts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        strike REAL NOT NULL,
                        option_type TEXT NOT NULL,
                        expiration_date TEXT NOT NULL,
                        assigned_price REAL NOT NULL,
                        current_price REAL,
                        assigned_at TIMESTAMP NOT NULL,
                        profit_loss_percent REAL,
                        last_updated TIMESTAMP,
                        closed BOOLEAN DEFAULT FALSE
                    )
                """)
                conn.commit()

@contextmanager
def get_db_connection():
    with db_lock:
        conn = sqlite3.connect("options_tracker.db", timeout=20)
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()

def assign_contract(ticker: str, strike: float, option_type: str, expiration_date: str, assigned_price: float):
    for attempt in range(DB_RETRIES):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM assigned_contracts 
                    WHERE ticker = ? AND strike = ? AND option_type = ? AND expiration_date = ? AND closed = FALSE
                """, (ticker, strike, option_type, expiration_date))
                if not cursor.fetchone():
                    assigned_at = datetime.now(timezone.utc).isoformat()
                    cursor.execute("""
                        INSERT INTO assigned_contracts (
                            ticker, strike, option_type, expiration_date, assigned_price, assigned_at, closed
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (ticker, strike, option_type, expiration_date, assigned_price, assigned_at, False))
                    conn.commit()
                return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < DB_RETRIES - 1:
                sleep(DB_RETRY_DELAY)
            else:
                raise

def update_contract_prices():
    retries = DB_RETRIES
    for attempt in range(retries):
        try:
            with db_lock:
                with sqlite3.connect("options_tracker.db", timeout=DB_TIMEOUT) as conn:
                    cursor = conn.cursor()
                    current_date = datetime.now(timezone.utc).date()
                    cursor.execute("""
                        SELECT id, ticker, strike, option_type, expiration_date, assigned_price 
                        FROM assigned_contracts 
                        WHERE date(expiration_date) >= ? AND closed = FALSE
                    """, (current_date.isoformat(),))
                    contracts = cursor.fetchall()
                    
                    pl_data = {}
                    updates = []
                    get_options_data.clear()
                    for contract in contracts:
                        contract_id, ticker, strike, option_type, expiration_date, assigned_price = contract
                        if assigned_price == 0:
                            pl_data[f"{ticker}_{strike}_{option_type}_{expiration_date}"] = {"pl": 0.0, "gamma": 0.0, "theta": 0.0}
                            continue
                        
                        options_data = get_options_data(ticker, expiration_date)
                        if not options_data:
                            pl_data[f"{ticker}_{strike}_{option_type}_{expiration_date}"] = {"pl": 0.0, "gamma": 0.0, "theta": 0.0}
                            continue
                        
                        current_price = None
                        gamma = 0.0
                        theta = 0.0
                        for opt in options_data:
                            if (float(opt["strike"]) == strike and 
                                opt["option_type"].upper() == option_type.upper()):
                                bid = float(opt.get("bid", 0) or 0)
                                ask = float(opt.get("ask", 0) or 0)
                                current_price = (bid + ask) / 2 if bid > 0 and ask > 0 else None
                                gamma = float(opt.get("greeks", {}).get("gamma", 0) or 0)
                                theta = float(opt.get("greeks", {}).get("theta", 0) or 0)
                                break
                        
                        if current_price is not None:
                            profit_loss_percent = ((current_price - assigned_price) / assigned_price) * 100
                            last_updated = datetime.now(timezone.utc).isoformat()
                            updates.append((current_price, profit_loss_percent, last_updated, contract_id))
                            pl_data[f"{ticker}_{strike}_{option_type}_{expiration_date}"] = {
                                "pl": profit_loss_percent,
                                "gamma": gamma,
                                "theta": theta
                            }
                        else:
                            pl_data[f"{ticker}_{strike}_{option_type}_{expiration_date}"] = {"pl": 0.0, "gamma": 0.0, "theta": 0.0}
                    
                    if updates:
                        cursor.executemany("""
                            UPDATE assigned_contracts 
                            SET current_price = ?, profit_loss_percent = ?, last_updated = ?
                            WHERE id = ?
                        """, updates)
                        conn.commit()
                    return pl_data
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < retries - 1:
                time.sleep(DB_RETRY_DELAY)
            else:
                raise

def close_contract(ticker: str, strike: float, option_type: str, expiration_date: str):
    retries = DB_RETRIES
    for attempt in range(retries):
        try:
            with db_lock:
                with sqlite3.connect("options_tracker.db", timeout=DB_TIMEOUT) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT closed FROM assigned_contracts 
                        WHERE ticker = ? AND strike = ? AND option_type = ? AND expiration_date = ?
                    """, (ticker, strike, option_type, expiration_date))
                    result = cursor.fetchone()
                    if result and result[0]:
                        return
                    
                    cursor.execute("""
                        UPDATE assigned_contracts 
                        SET closed = TRUE 
                        WHERE ticker = ? AND strike = ? AND option_type = ? AND expiration_date = ? AND closed = FALSE
                    """, (ticker, strike, option_type, expiration_date))
                    conn.commit()
                    return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < retries - 1:
                time.sleep(DB_RETRY_DELAY)
            else:
                st.error(f"Failed to close contract for {ticker} ${strike:.0f} {option_type}. Please try again.")
                raise

def auto_update_prices():
    if "last_update" not in st.session_state:
        st.session_state.last_update = time.time()
    
    current_time = time.time()
    interval = 15
    if current_time - st.session_state.last_update >= interval:
        try:
            pl_data = update_contract_prices()
            for key, data in pl_data.items():
                st.session_state[f"pl_{key}"] = data["pl"] if data["pl"] is not None else 0.0
                st.session_state[f"gamma_{key}"] = data["gamma"] if data["gamma"] is not None else 0.0
                st.session_state[f"theta_{key}"] = data["theta"] if data["theta"] is not None else 0.0
            st.session_state.last_update = current_time
        except sqlite3.OperationalError as e:
            st.session_state.last_update = current_time
            st.warning("Database temporarily locked. Retrying in next update cycle.")

def kraken_pair_to_api_format(ticker: str) -> str:
    base = ticker.upper()
    quote = "USD"
    if base == "BTC":
        base = "XBT"
    return f"X{base}Z{quote}"

def fetch_order_book(ticker: str, depth: int = 500) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
    api_pair = kraken_pair_to_api_format(ticker)
    try:
        response = kraken.query_public("Depth", {"pair": api_pair, "count": depth})
        if "error" in response and response["error"]:
            logger.error(f"Error fetching order book for {ticker}/USD: {response['error']}")
            return pd.DataFrame(), pd.DataFrame(), 0.0
        
        result = response["result"][api_pair]
        bids = pd.DataFrame(result["bids"], columns=["Price", "Volume", "Timestamp"]).astype(float)
        asks = pd.DataFrame(result["asks"], columns=["Price", "Volume", "Timestamp"]).astype(float)
        
        if bids.empty or asks.empty:
            logger.warning(f"Empty order book received for {ticker}/USD")
        
        best_bid = bids["Price"].max() if not bids.empty else 0
        best_ask = asks["Price"].min() if not asks.empty else 0
        current_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0.0
        
        return bids, asks, current_price
    except Exception as e:
        logger.error(f"Error fetching order book for {ticker}/USD: {e}")
        return pd.DataFrame(), pd.DataFrame(), 0.0

def fetch_coingecko_data(ticker: str) -> dict:
    coin_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "XRP": "ripple",
        "LTC": "litecoin",
        "ADA": "cardano"
    }
    coin_id = coin_map.get(ticker.upper(), ticker.lower())
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return {}
        data = response.json()
        market_data = data.get("market_data", {})
        history_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
        history_response = requests.get(history_url, timeout=5)
        history_data = history_response.json() if history_response.status_code == 200 else {"prices": []}
        prices = [price[1] for price in history_data.get("prices", [])]
        volatility = stats.stdev([p / prices[0] * 100 - 100 for p in prices]) * (365 ** 0.5) if len(prices) > 1 else 0
        return {
            "price": market_data.get("current_price", {}).get("usd", 0),
            "change_value": market_data.get("price_change_24h", 0),
            "change_percent": market_data.get("price_change_percentage_24h", 0),
            "volume": market_data.get("total_volume", {}).get("usd", 0),
            "market_cap": market_data.get("market_cap", {}).get("usd", 0),
            "volatility": volatility
        }
    except Exception as e:
        logger.error(f"Error fetching CoinGecko data for {ticker}: {str(e)}")
        return {}

def calculate_crypto_max_pain(bids: pd.DataFrame, asks: pd.DataFrame) -> float:
    if bids.empty or asks.empty:
        return 0.0
    
    all_prices = sorted(set(bids["Price"].tolist() + asks["Price"].tolist()))
    min_price = min(all_prices)
    max_price = max(all_prices)
    price_range = np.linspace(min_price, max_price, 200)
    
    max_pain_losses = {}
    for price in price_range:
        bid_loss = bids[bids["Price"] < price]["Volume"].sum() * (price - bids[bids["Price"] < price]["Price"]).sum()
        ask_loss = asks[asks["Price"] > price]["Volume"].sum() * (asks[asks["Price"] > price]["Price"] - price).sum()
        total_loss = bid_loss + ask_loss
        max_pain_losses[price] = total_loss
    
    max_pain_price = min(max_pain_losses, key=max_pain_losses.get, default=0.0)
    return max_pain_price

def calculate_metrics_with_whales(bids: pd.DataFrame, asks: pd.DataFrame, current_price: float, market_volatility: float) -> dict:
    total_bid_volume = bids["Volume"].sum() if not bids.empty else 0
    total_ask_volume = asks["Volume"].sum() if not asks.empty else 0
    total_volume = total_bid_volume + total_ask_volume
    net_pressure = total_bid_volume - total_ask_volume if total_volume > 0 else 0
    pressure_index = (net_pressure / total_volume * 100) if total_volume > 0 else 0
    
    whale_threshold = max(bids["Volume"].quantile(0.95) if not bids.empty else 0, 
                          asks["Volume"].quantile(0.95) if not asks.empty else 0, 
                          50.0)
    whale_bids = bids[bids["Volume"] >= whale_threshold] if not bids.empty else pd.DataFrame()
    whale_asks = asks[asks["Volume"] >= whale_threshold] if not asks.empty else pd.DataFrame()
    
    whale_bid_volume = whale_bids["Volume"].sum() if not whale_bids.empty else 0
    whale_ask_volume = whale_asks["Volume"].sum() if not whale_asks.empty else 0
    whale_net_pressure = whale_bid_volume - whale_ask_volume
    whale_pressure_weight = (whale_bid_volume + whale_ask_volume) / total_volume if total_volume > 0 else 0
    
    whale_bid_price = (whale_bids["Price"] * whale_bids["Volume"]).sum() / whale_bid_volume if whale_bid_volume > 0 else current_price
    whale_ask_price = (whale_asks["Price"] * whale_asks["Volume"]).sum() / whale_ask_volume if whale_ask_volume > 0 else current_price
    
    bids["CumVolume"] = bids["Volume"].cumsum()
    asks["CumVolume"] = asks["Volume"].cumsum()
    support = bids[bids["CumVolume"] >= total_bid_volume * 0.25]["Price"].min() if not bids.empty else current_price
    resistance = asks[asks["CumVolume"] >= total_ask_volume * 0.25]["Price"].max() if not asks.empty else current_price
    
    whale_zones = []
    if not whale_bids.empty:
        whale_zones.extend(whale_bids["Price"].tolist())
    if not whale_asks.empty:
        whale_zones.extend(whale_asks["Price"].tolist())
    whale_zones = sorted(set(whale_zones))[:6]
    
    max_pain_price = calculate_crypto_max_pain(bids, asks)
    if max_pain_price != 0.0 and current_price != 0.0:
        distance_to_max_pain = max_pain_price - current_price
        whale_influence = (whale_bid_price * whale_bid_volume - whale_ask_price * whale_ask_volume) / (whale_bid_volume + whale_ask_volume + 1) if (whale_bid_volume + whale_ask_volume) > 0 else 0
        whale_factor = whale_pressure_weight * whale_influence * 3
        volatility_factor = market_volatility / 100
        possible_move = (distance_to_max_pain * (pressure_index / 100) + whale_factor) * (1 + volatility_factor)
        target_price = current_price + possible_move
        direction = "BUY" if current_price < target_price else "SELL" if current_price > target_price else "HOLD"
        
        whale_momentum = whale_net_pressure / (whale_bid_volume + whale_ask_volume + 1) * 100 if (whale_bid_volume + whale_ask_volume) > 0 else 0
        edge_score = (pressure_index * 0.4 + whale_momentum * 0.4 + volatility_factor * 20)
    else:
        target_price = current_price
        direction = "HOLD"
        edge_score = 0
    
    return {
        "net_pressure": net_pressure,
        "volatility": market_volatility,
        "support": support,
        "resistance": resistance,
        "whale_zones": whale_zones,
        "target_price": target_price,
        "direction": direction,
        "trend": "Bullish" if net_pressure > 0 else "Bearish" if net_pressure < 0 else "Neutral",
        "whale_bids": whale_bids,
        "whale_asks": whale_asks,
        "edge_score": edge_score
    }

def plot_order_book_bubbles_with_max_pain(bids: pd.DataFrame, asks: pd.DataFrame, current_price: float, ticker: str, market_volatility: float) -> Tuple[go.Figure, dict]:
    fig = go.Figure()
    
    if not bids.empty:
        fig.add_trace(go.Scatter(x=bids["Price"], y=[0] * len(bids), mode="markers", name="Bids",
                                marker=dict(size=bids["Volume"] * 20 / bids["Volume"].max(), color="#32CD32", opacity=0.7, line=dict(width=0.5, color="white")),
                                customdata=bids[["Price", "Volume"]], hovertemplate="<b>Price:</b> $%{customdata[0]:.2f}<br><b>Volume:</b> %{customdata[1]:.2f}"))
    
    if not asks.empty:
        fig.add_trace(go.Scatter(x=asks["Price"], y=[0] * len(asks), mode="markers", name="Asks",
                                marker=dict(size=asks["Volume"] * 20 / asks["Volume"].max(), color="#FF4500", opacity=0.7, line=dict(width=0.5, color="white")),
                                customdata=asks[["Price", "Volume"]], hovertemplate="<b>Price:</b> $%{customdata[0]:.2f}<br><b>Volume:</b> %{customdata[1]:.2f}"))
    
    metrics = calculate_metrics_with_whales(bids, asks, current_price, market_volatility)
    
    if not metrics["whale_bids"].empty:
        fig.add_trace(go.Scatter(x=metrics["whale_bids"]["Price"], y=[0] * len(metrics["whale_bids"]), mode="markers", name="Whale Bids",
                                marker=dict(size=metrics["whale_bids"]["Volume"] * 20 / bids["Volume"].max(), color="#00FF00", opacity=0.9, line=dict(width=2, color="white")),
                                customdata=metrics["whale_bids"][["Price", "Volume"]], hovertemplate="<b>Whale Bid Price:</b> $%{customdata[0]:.2f}<br><b>Volume:</b> %{customdata[1]:.2f}"))
    
    if not metrics["whale_asks"].empty:
        fig.add_trace(go.Scatter(x=metrics["whale_asks"]["Price"], y=[0] * len(metrics["whale_asks"]), mode="markers", name="Whale Asks",
                                marker=dict(size=metrics["whale_asks"]["Volume"] * 20 / asks["Volume"].max(), color="#FF0000", opacity=0.9, line=dict(width=2, color="white")),
                                customdata=metrics["whale_asks"][["Price", "Volume"]], hovertemplate="<b>Whale Ask Price:</b> $%{customdata[0]:.2f}<br><b>Volume:</b> %{customdata[1]:.2f}"))
    
    if current_price > 0:
        fig.add_vline(x=current_price, line=dict(color="#FFD700", width=1, dash="dash"), annotation_text=f"Current: ${current_price:.2f}",
                     annotation_position="top left", annotation_font=dict(color="#FFD700", size=10))
    
    if metrics["target_price"] != current_price:
        fig.add_vline(x=metrics["target_price"], line=dict(color="#39FF14", width=1, dash="dot"), annotation_text=f"Target: ${metrics['target_price']:.2f} ({metrics['direction']})",
                     annotation_position="top right", annotation_font=dict(color="#39FF14", size=10))
    
    fig.add_vline(x=metrics["support"], line=dict(color="#1E90FF", width=1, dash="dot"), annotation_text=f"Support: ${metrics['support']:.2f}",
                 annotation_position="bottom left", annotation_font=dict(color="#1E90FF", size=8))
    fig.add_vline(x=metrics["resistance"], line=dict(color="#FF4500", width=1, dash="dot"), annotation_text=f"Resistance: ${metrics['resistance']:.2f}",
                 annotation_position="bottom right", annotation_font=dict(color="#FF4500", size=8))
    
    fig.update_layout(title=f"FlowS {ticker}/USD | Strategy", xaxis_title="Price (USD)", yaxis_title="", template="plotly_dark",
                     plot_bgcolor="#1E1E1E", paper_bgcolor="#1E1E1E", font=dict(color="#FFFFFF", size=12), hovermode="x unified",
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=600, showlegend=True,
                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
    
    return fig, metrics

def fetch_earnings_data(start_date: str, end_date: str) -> List[Dict]:
    url = f"{FMP_BASE_URL}/earning_calendar"
    params = {"apikey": FMP_API_KEY, "from": start_date, "to": end_date}
    try:
        response = session_fmp.get(url, params=params, headers=HEADERS_FMP, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
        return []
    except Exception as e:
        logger.error(f"Error fetching earnings data: {str(e)}")
        return []

# MAIN APP
def main():
    st.markdown("""
        <div class="header-container">
            <div class="header-title">ℙℝ𝕆 𝔼𝕊ℂ𝔸ℕℕ𝔼ℝ®</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .stApp {
            background-color: #000000;
        }
        .stTextInput, .stSelectbox {
            background-color: #2D2D2D;
            color: #FFFFFF;
        }
        .stSpinner > div > div {
            border-color: #32CD32 !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            background: none;
            padding: 5px;
            gap: 2px;
            margin-top: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 5px 10px;
            margin: 2px;
            color: rgba(57, 255, 20, 0.7);
            background: #000000;
            border: 1px solid rgba(57, 255, 20, 0.15);
            border-radius: 5px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 0 2.5px rgba(57, 255, 20, 0.1);
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: #39FF14;
            color: #1E1E1E;
            transform: translateY(-2px);
            box-shadow: 0 4px 5px rgba(57, 255, 20, 0.4);
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #00FFFF;
            color: #1E1E1E;
            font-weight: 700;
            transform: scale(1.1);
            box-shadow: 0 0 7.5px rgba(0, 255, 255, 0.4);
            border: 1px solid rgba(0, 255, 255, 0.5);
        }
        .stDownloadButton > button {
            padding: 5px 10px;
            margin: 2px;
            color: rgba(57, 255, 20, 0.7);
            background: #000000;
            border: 1px solid rgba(57, 255, 20, 0.15);
            border-radius: 5px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 0 2.5px rgba(57, 255, 20, 0.1);
        }
        .stDownloadButton > button:hover {
            background: #39FF14;
            color: #1E1E1E;
            transform: translateY(-2px);
            box-shadow: 0 4px 5px rgba(57, 255, 20, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "| Gummy Data Bubbles® |", "| Market Scanner |", "| News |"
    ])

    with tab1:
        ticker = st.text_input("Ticker", value="SPY", key="ticker_input").upper()
        
        expiration_dates = get_expiration_dates(ticker)
        if not expiration_dates:
            st.error(f"No future expiration dates found for '{ticker}'")
            st.stop()
        
        expiration_date = st.selectbox("Expiration Date", expiration_dates, key="expiration_date")
        
        with st.spinner("Fetching price..."):
            current_price = get_current_price(ticker)
            if current_price == 0.0:
                st.error(f"Unable to fetch current price for '{ticker}'")
                st.stop()
        
        st.markdown(f"**Current Price:** ${current_price:.2f}")
        
        with st.spinner(f"Fetching data for {expiration_date}..."):
            processed_data, touched_strikes, max_pain, max_pain_df = process_options_data(ticker, expiration_date)
            if not processed_data:
                st.error(f"No valid options data for {ticker}")
                st.stop()
            
            options_data = get_options_data(ticker, expiration_date)
            
            gamma_fig = gamma_exposure_chart(processed_data, current_price, touched_strikes)
            st.plotly_chart(gamma_fig, use_container_width=True)
            
            gamma_df = pd.DataFrame({
                "Strike": list(processed_data.keys()),
                "CALL_Gamma": [processed_data[s]["CALL"]["Gamma"] for s in processed_data],
                "PUT_Gamma": [processed_data[s]["PUT"]["Gamma"] for s in processed_data],
                "CALL_OI": [processed_data[s]["CALL"]["OI"] for s in processed_data],
                "PUT_OI": [processed_data[s]["PUT"]["OI"] for s in processed_data]
            })
            gamma_csv = gamma_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Gamma Exposure Data",
                data=gamma_csv,
                file_name=f"{ticker}_gamma_exposure_{expiration_date}.csv",
                mime="text/csv",
                key="download_gamma_tab1"
            )
            
            skew_fig, total_calls, total_puts = plot_skew_analysis_with_totals(options_data, current_price)
            st.plotly_chart(skew_fig, use_container_width=True)
            st.write(f"**Total CALLS:** {total_calls} | **Total PUTS:** {total_puts}")
            
            st.write(f"**Max Pain Strike:** {max_pain if max_pain else 'N/A'}")
            
            max_pain_fig = plot_max_pain_histogram_with_levels(max_pain_df, current_price)
            st.plotly_chart(max_pain_fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown("*Developed by Ozy | © 2025*")

    with tab2:
        st.subheader("Market Scanner Pro")
        
        scan_type = st.selectbox(
            "Select Scan Type",
            ["Bullish (Upward Momentum)", "Bearish (Downward Momentum)", "Breakouts", "Unusual Volume"],
            key="scan_type_tab2"
        )
        max_results = st.slider("Max Stocks to Display", 1, 200, 20, key="max_results_tab2")
        
        if st.button("🚀 Run Market Scan", key="run_scan_tab2"):
            with st.spinner(f"Scanning Market ({scan_type})..."):
                stocks_to_scan = get_metaverse_stocks()
                scan_results = scan_stock_batch(stocks_to_scan, scan_type)
                
                if scan_results:
                    df_scan = pd.DataFrame(scan_results)[:max_results]
                    st.dataframe(df_scan, use_container_width=True)
                    
                    csv_scan = df_scan.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Scan Results",
                        data=csv_scan,
                        file_name=f"market_scan_{scan_type.replace(' ', '_').lower()}.csv",
                        mime="text/csv",
                        key="download_scan_tab2"
                    )
                else:
                    st.warning(f"No stocks met the criteria for '{scan_type}'")
        
        st.markdown("---")
        st.markdown("*Developed by Ozy | © 2025*")

    with tab3:
        st.subheader("News Scanner")
        
        if "latest_news" not in st.session_state:
            with st.spinner("Fetching initial market news..."):
                google_news = fetch_google_news(["SPY"])
                bing_news = fetch_bing_news(["SPY"])
                st.session_state["latest_news"] = google_news + bing_news if google_news or bing_news else None
        
        st.markdown("#### Search News")
        keywords = st.text_input("Enter keywords (comma-separated):", "Trump", key="news_keywords").split(",")
        keywords = [k.strip() for k in keywords if k.strip()]
        
        if st.button("Fetch News", key="fetch_news"):
            with st.spinner("Fetching news..."):
                google_news = fetch_google_news(keywords)
                bing_news = fetch_bing_news(keywords)
                latest_news = google_news + bing_news
                
                if latest_news:
                    st.session_state["latest_news"] = latest_news
                    for idx, article in enumerate(latest_news[:10], 1):
                        st.markdown(f"### {idx}. [{article['title']}]({article['link']})")
                        st.markdown(f"**Published:** {article['time']}\n")
                        st.markdown("---")
                else:
                    st.error("No recent news found.")
                    st.session_state["latest_news"] = None
        
        st.markdown("---")
        st.markdown("#### Market Sentiment")
        if st.session_state["latest_news"]:
            sentiment_score, sentiment_text = calculate_retail_sentiment(st.session_state["latest_news"])
            volatility_score, volatility_text = calculate_volatility_sentiment(st.session_state["latest_news"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Retail Sentiment")
                st.markdown(f"**Sentiment:** {sentiment_text} ({sentiment_score:.2%})")
            
            with col2:
                st.markdown("##### Volatility Sentiment")
                st.markdown(f"**Volatility:** {volatility_text} ({volatility_score:.1f}/100)")
        else:
            st.warning("No news data available to analyze sentiment")
        
        st.markdown("---")
        st.markdown("*Developed by Ozy | © 2025*")

if __name__ == "__main__":
    main()
