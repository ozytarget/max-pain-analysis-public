"""
Client library para communicar con el API backend
Se usa en app.py para reemplazar las llamadas directas a terceros
"""

import requests
from typing import Dict, List, Optional, Tuple
import logging
from functools import lru_cache
import os

logger = logging.getLogger(__name__)

# Base URL del API backend
API_BASE_URL = os.getenv("API_BACKEND_URL", "http://localhost:8000")

class APIBackendClient:
    """Cliente para el API backend centralizado"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Helper para hacer requests al backend"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise
    
    def get_current_price(self, ticker: str) -> float:
        """Get current price for a ticker"""
        try:
            data = self._make_request("GET", f"/api/price/{ticker}")
            return data.get("price", 0.0)
        except Exception as e:
            logger.error(f"Failed to get price for {ticker}: {str(e)}")
            return 0.0
    
    def get_current_prices(self, tickers: List[str]) -> Dict[str, float]:
        """Get current prices for multiple tickers"""
        try:
            tickers_str = ",".join(tickers)
            data = self._make_request("GET", "/api/prices", params={"tickers": tickers_str})
            prices_dict = {}
            for ticker, info in data.get("prices", {}).items():
                prices_dict[ticker] = info.get("price", 0.0)
            return prices_dict
        except Exception as e:
            logger.error(f"Failed to get prices batch: {str(e)}")
            return {ticker: 0.0 for ticker in tickers}
    
    def get_historical_prices(self, ticker: str, days: int = 30) -> Tuple[List[float], List[int]]:
        """Get historical prices and volumes"""
        try:
            data = self._make_request("GET", f"/api/historical/{ticker}", params={"days": days})
            prices = data.get("prices", [])
            volumes = data.get("volumes", [])
            return prices, volumes
        except Exception as e:
            logger.error(f"Failed to get historical prices for {ticker}: {str(e)}")
            return [], []
    
    def get_options_chain(self, ticker: str, expiration: str) -> List[Dict]:
        """Get options chain for a specific expiration"""
        try:
            data = self._make_request("GET", f"/api/options/{ticker}/{expiration}")
            return data.get("options", [])
        except Exception as e:
            logger.error(f"Failed to get options for {ticker}: {str(e)}")
            return []
    
    def get_option_expirations(self, ticker: str) -> List[str]:
        """Get available option expirations"""
        try:
            data = self._make_request("GET", f"/api/expirations/{ticker}")
            return data.get("expirations", [])
        except Exception as e:
            logger.error(f"Failed to get expirations for {ticker}: {str(e)}")
            return []
    
    def get_financial_metrics(self, ticker: str) -> Dict:
        """Get financial metrics"""
        try:
            data = self._make_request("GET", f"/api/metrics/{ticker}")
            return data
        except Exception as e:
            logger.error(f"Failed to get metrics for {ticker}: {str(e)}")
            return {}
    
    def get_volatility(self, ticker: str, days: int = 30) -> float:
        """Get annualized volatility"""
        try:
            data = self._make_request("GET", f"/api/volatility/{ticker}", params={"days": days})
            return data.get("annualized_volatility", 0.0)
        except Exception as e:
            logger.error(f"Failed to get volatility for {ticker}: {str(e)}")
            return 0.0
    
    def health_check(self) -> Dict:
        """Check backend health"""
        try:
            return self._make_request("GET", "/health")
        except Exception as e:
            logger.error(f"Backend health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

# Crear instancia global del cliente
api_client = APIBackendClient()
