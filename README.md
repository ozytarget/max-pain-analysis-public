# Pro Scanner 🚀

**Advanced Financial Market Scanner with AI-Powered Options Analysis**

## Overview

Pro Scanner is a sophisticated Streamlit-based financial analysis application that combines real-time market data, options analytics, and gamma exposure analysis to identify trading opportunities.

### Key Features

- **🎯 Gummy Data Bubbles®** - Gamma exposure analysis with real-time visualization
- **🔍 Market Scanner** - FinViz Elite integration for pattern detection (Cup & Handle, Head & Shoulders, Wedges, etc.)
- **📰 News Integration** - Real-time sentiment analysis from market news
- **📊 Stock Insights** - Institutional holdings, financial metrics, and analyst ratings
- **⚡ Options Order Flow** - Advanced options chain analysis with Greeks
- **🎭 Elliott Wave Analysis** - Technical pattern recognition
- **🔐 VIP Authentication** - Secure user access with password protection

## Technology Stack

### Core Framework
- **Streamlit** - Interactive web application framework
- **Python 3.12+** - Programming language
- **Plotly** - Professional interactive visualizations

### Market Data APIs
- **Tradier** - Real-time options data and quotes
- **Financial Modeling Prep (FMP)** - Financial metrics and historical data
- **Kraken** - Cryptocurrency data
- **FinViz Elite** - Stock screener with technical patterns
- **Yahoo Finance** - Alternative data source

### Security & Authentication
- **bcrypt** - Password hashing
- **SQLite3** - Secure credential storage
- **python-dotenv** - Environment variable management

### Data Processing
- **pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **scikit-learn** - Machine learning algorithms
- **BeautifulSoup4** - Web scraping

## Installation

### Prerequisites
- Python 3.12 or higher
- pip package manager
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/max-pain-analysis-public.git
   cd max-pain-analysis-public
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate      # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy template
   cp .env.example .env
   
   # Edit .env with your API keys
   # Add your actual API keys from:
   # - Tradier: https://tradier.com/api
   # - FMP: https://financialmodelingprep.com
   # - Kraken: https://www.kraken.com/features/api
   # - FinViz Elite: https://elite.finviz.com
   ```

5. **Create auth database**
   ```bash
   python app.py
   # Authentication database will be created automatically
   ```

## Running the Application

### Local Development
```bash
streamlit run app.py
```

### Headless Mode (Server Deployment)
```bash
streamlit run app.py --server.headless true --server.port 8501
```

### Access
- Local: `http://localhost:8501`
- Network: `http://your-ip:8501`

## Security

### API Key Management

⚠️ **IMPORTANT: Never commit your `.env` file to version control**

All sensitive credentials are managed through environment variables:

```python
# All API keys are loaded from .env
API_KEY = os.getenv("KRAKEN_API_KEY", "")
FMP_API_KEY = os.getenv("FMP_API_KEY", "")
FINVIZ_API_TOKEN = os.getenv("FINVIZ_API_TOKEN", "")
```

### File Protection

The `.gitignore` includes comprehensive security rules:
- `.env` files (all variants)
- `auth_data/` directory
- `credentials/` directory
- `__pycache__/` directories
- `.streamlit/` cache

### Authentication

User access is controlled via:
- bcrypt password hashing
- IP-based device tracking
- Usage counter per credential
- SQLite database with WAL mode

## Project Structure

```
max-pain-analysis-public/
├── app.py                      # Main application (6,098 lines)
├── requirements.txt            # Python dependencies (16 packages)
├── .env                        # API credentials (NEVER commit)
├── .env.example                # Template for .env
├── .gitignore                  # Git ignore rules (47 rules)
├── SECURITY.md                 # Security documentation
├── AUDIT_REPORT.md            # Code audit & validation
├── API_DEPENDENCIES.md        # API documentation
├── README.md                   # This file
└── auth_data/
    └── passwords.db           # User credentials database
```

## API Configuration

### Required APIs

1. **Tradier** (Required)
   - Real-time options data
   - Stock quotes
   - Historical data
   - Sign up: https://tradier.com/api

2. **Financial Modeling Prep** (Required)
   - Financial metrics
   - Historical prices
   - Sign up: https://financialmodelingprep.com

3. **FinViz Elite** (Optional)
   - Stock screener
   - Technical patterns
   - Sign up: https://elite.finviz.com

4. **Kraken** (Optional)
   - Cryptocurrency data
   - Sign up: https://www.kraken.com/features/api

## Performance Optimization

- **Rate limiting:** 2-second delays between API calls
- **Connection pooling:** Reusable HTTP sessions
- **Caching:** 300-second TTL on non-critical data
- **Threading:** Concurrent API requests
- **Database:** SQLite WAL mode for concurrent access

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.x | Web framework |
| pandas | Latest | Data manipulation |
| plotly | Latest | Visualizations |
| requests | Latest | HTTP client |
| scipy | Latest | Scientific computing |
| scikit-learn | Latest | Machine learning |
| bcrypt | Latest | Password hashing |
| beautifulsoup4 | Latest | Web scraping |
| krakenex | Latest | Kraken API |
| yfinance | Latest | Yahoo Finance |
| python-dotenv | Latest | Environment vars |
| pytz | Latest | Timezone handling |

See `requirements.txt` for complete list and versions.

## Troubleshooting

### Import Errors
```bash
# Ensure all dependencies installed
pip install -r requirements.txt --upgrade
```

### API Connection Issues
- Verify API keys in `.env`
- Check internet connection
- Test rate limiting (add delays between requests)
- Review API status pages

### Database Locked
- SQLite uses WAL mode for concurrent access
- Ensure only one Streamlit instance running
- Check `auth_data/` directory permissions

### Authentication Failed
- Verify password in database
- Check IP address restrictions
- Reset passwords by deleting `passwords.db`

## Code Quality

- ✅ **Syntax:** Python 3.12 validated
- ✅ **Imports:** 32 organized imports, no duplicates
- ✅ **Variables:** No duplicate definitions
- ✅ **Security:** Comprehensive .gitignore (47 rules)
- ✅ **Cache:** Clean (no __pycache__ or .streamlit)
- ✅ **Logging:** Comprehensive error handling

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is provided as-is for educational and professional use.

## Support & Documentation

- **Security Guide:** See `SECURITY.md`
- **API Documentation:** See `API_DEPENDENCIES.md`
- **Code Audit:** See `AUDIT_REPORT.md`

## Disclaimer

This application is for informational purposes only. Trading involves risk. Always consult with a financial advisor before making investment decisions.

---

**Developed with ❤️**  
**Last Updated:** December 1, 2025  
**Status:** Production Ready ✅
