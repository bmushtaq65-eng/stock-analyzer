"""
Configuration for Stock Trading & Investment Analysis Platform
"""
import os

# Application settings
APP_TITLE = "AI Stock Trading & Investment Analysis Platform"
APP_ICON = "📈"
APP_LAYOUT = "wide"
APP_CACHE_TTL = 300  # 5 minutes cache for market data

# Exchange configurations
EXCHANGES = {
    "NSE": {
        "suffix": ".NS",
        "name": "National Stock Exchange",
        "currency": "₹",
        "country": "India",
    },
    "BSE": {
        "suffix": ".BO",
        "name": "Bombay Stock Exchange",
        "currency": "₹",
        "country": "India",
    },
    "NYSE": {
        "suffix": "",
        "name": "New York Stock Exchange",
        "currency": "$",
        "country": "USA",
    },
    "NASDAQ": {
        "suffix": "",
        "name": "NASDAQ",
        "currency": "$",
        "country": "USA",
    },
}

# Common Indian stock mappings (ticker -> name)
INDIAN_STOCKS = {
    "RELIANCE": "Reliance Industries Ltd",
    "TCS": "Tata Consultancy Services",
    "HDFCBANK": "HDFC Bank Ltd",
    "INFY": "Infosys Ltd",
    "ICICIBANK": "ICICI Bank Ltd",
    "HINDUNILVR": "Hindustan Unilever Ltd",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel Ltd",
    "ITC": "ITC Ltd",
    "KOTAKBANK": "Kotak Mahindra Bank",
    "LT": "Larsen & Toubro Ltd",
    "AXISBANK": "Axis Bank Ltd",
    "ASIANPAINT": "Asian Paints Ltd",
    "MARUTI": "Maruti Suzuki India Ltd",
    "SUNPHARMA": "Sun Pharmaceutical",
    "TATAMOTORS": "Tata Motors Ltd",
    "WIPRO": "Wipro Ltd",
    "HCLTECH": "HCL Technologies Ltd",
    "BAJFINANCE": "Bajaj Finance Ltd",
    "TITAN": "Titan Company Ltd",
    "ADANIENT": "Adani Enterprises Ltd",
    "ADANIPORTS": "Adani Ports & SEZ",
    "POWERGRID": "Power Grid Corp",
    "NTPC": "NTPC Ltd",
    "ONGC": "Oil & Natural Gas Corp",
    "TATASTEEL": "Tata Steel Ltd",
    "JSWSTEEL": "JSW Steel Ltd",
    "ULTRACEMCO": "UltraTech Cement",
    "NESTLEIND": "Nestle India Ltd",
    "TECHM": "Tech Mahindra Ltd",
    "DRREDDY": "Dr. Reddy's Laboratories",
    "CIPLA": "Cipla Ltd",
    "DIVISLAB": "Divi's Laboratories",
    "EICHERMOT": "Eicher Motors Ltd",
    "HEROMOTOCO": "Hero MotoCorp Ltd",
    "BAJAJFINSV": "Bajaj Finserv Ltd",
    "COALINDIA": "Coal India Ltd",
    "GRASIM": "Grasim Industries",
    "TATACONSUM": "Tata Consumer Products",
    "APOLLOHOSP": "Apollo Hospitals",
    "BRITANNIA": "Britannia Industries",
    "INDUSINDBK": "IndusInd Bank",
    "HINDALCO": "Hindalco Industries",
    "BPCL": "Bharat Petroleum",
    "SHRIRAMFIN": "Shriram Finance",
}

# Technical analysis defaults
TA_DEFAULTS = {
    "sma_periods": [20, 50, 100, 200],
    "ema_periods": [9, 20, 50, 200],
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb_period": 20,
    "bb_std": 2,
    "atr_period": 14,
    "adx_period": 14,
    "stoch_rsi_period": 14,
    "stoch_k": 14,
    "stoch_d": 3,
    "supertrend_period": 10,
    "supertrend_multiplier": 3,
    "vwap_session": True,
    "roc_period": 12,
}

# Risk parameters
RISK_DEFAULTS = {
    "max_risk_per_trade_pct": 2.0,
    "default_investment": 100000,
    "max_position_pct": 20.0,
}

# Support/Resistance parameters
SR_DEFAULTS = {
    "lookback_period": 60,
    "min_touches": 2,
    "pivot_window": 5,
    "fibonacci_levels": [0.236, 0.382, 0.5, 0.618, 0.786],
}

# Timeframe configurations
TIMEFRAMES = {
    "1m": {"yf_interval": "1m", "yf_period": "1d", "label": "1 Minute"},
    "3m": {"yf_interval": "5m", "yf_period": "5d", "label": "3 Minute"},
    "5m": {"yf_interval": "5m", "yf_period": "5d", "label": "5 Minute"},
    "15m": {"yf_interval": "15m", "yf_period": "1mo", "label": "15 Minute"},
    "30m": {"yf_interval": "30m", "yf_period": "1mo", "label": "30 Minute"},
    "1h": {"yf_interval": "60m", "yf_period": "3mo", "label": "1 Hour"},
    "4h": {"yf_interval": "60m", "yf_period": "6mo", "label": "4 Hour"},
    "daily": {"yf_interval": "1d", "yf_period": "1y", "label": "Daily"},
    "weekly": {"yf_interval": "1wk", "yf_period": "5y", "label": "Weekly"},
    "monthly": {"yf_interval": "1mo", "yf_period": "max", "label": "Monthly"},
}

# Analysis timeframes
ANALYSIS_TIMEFRAMES = {
    "intraday": "Intraday",
    "swing": "Swing / Short Term (1-4 weeks)",
    "medium": "Medium Term (1-6 months)",
    "long": "Long Term (6 months - 5+ years)",
}

# News categories
NEWS_CATEGORIES = [
    "Earnings", "Orders", "Management Changes", "Regulatory Issues",
    "Litigation", "Debt", "Expansion", "M&A", "Government Policy",
    "Sector Developments", "General",
]
