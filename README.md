# AI Stock Trading & Investment Analyzer

An AI-powered stock analysis platform that automatically collects market data, technical indicators, fundamentals, news, and price-action signals — converting them into clear analyses for **intraday trading, swing/short-term trading, and long-term investing**.

> **Important:** This project is a decision-support and research tool. It does not guarantee profits or provide certainty about future prices.

---

## 🚀 Overview

Instead of manually checking multiple charts, financial statements, and news sources, simply enter a stock symbol (e.g., `RELIANCE.NS`, `TCS.BO`, `AAPL`) to instantly generate a comprehensive report.

The platform automatically answers:
- What is the current trend across multiple timeframes?
- Where are key support and resistance levels?
- Is momentum bullish or bearish?
- What are the intraday and swing trade setups?
- What are the bullish, base, and bearish scenarios?
- What are the fundamental and technical scores?

## 🌍 Supported Markets
- **Indian Stock Market (NSE/BSE):** Analyze Indian equities by appending the exchange suffix (e.g., `RELIANCE.NS`, `TCS.BO`).
- **US Stock Market:** Support for NASDAQ, NYSE, etc. (e.g., `AAPL`, `TSLA`).
- **Cryptocurrencies & Forex:** Analyze pairs like `BTC-USD` or `EURUSD=X`.

---

## 📊 Core Features

- **Market Snapshot:** Current price, volume, average volume, 52-week high/low, and market cap.
- **Interactive Charts:** Professional candlestick charts with EMA, VWAP, Bollinger Bands, and automated Support/Resistance zones.
- **Technical Analysis Engine:** Automated interpretation of trends, momentum (RSI, MACD, Stochastic), volatility (ATR), and volume.
- **Support & Resistance Engine:** Auto-identifies major/minor levels, pivot points, and Fibonacci retracements with strength ratings.
- **Multi-Timeframe Analysis:** Correlates 5m, 15m, 1H, Daily, Weekly, and Monthly trends to build a cohesive market bias.
- **Actionable Setups:** Provides clear Entry, Stop Loss, Target Zones, Risk/Reward ratio, and Invalidation levels for intraday and swing trades.
- **AI Scenario Modeling (Bull/Base/Bear):** Generates probabilistic scenarios rather than fixed predictions.
- **Risk & Position Sizing Calculator:** Input your capital and risk tolerance to mathematically determine optimal share quantity and maximum loss.
- **Fundamental & News Engine:** Collects recent news sentiment and evaluates core fundamental metrics (P/E, ROE, Debt/Equity) for long-term health.

---

## 🏗️ Architecture

The project features a modular design, avoiding tight coupling to any single data provider:

```text
stock-analyzer/
├── data/        # Market data, historical, fundamentals, and news
├── indicators/  # Trend, momentum, volatility, and volume math
├── analysis/    # Price action, S&R, multi-timeframe, risk scoring
├── ai/          # AI explanations, scenarios, analyst engine
├── alerts/      # Price, technical, and news alerts
├── ui/          # Streamlit dashboard, charts, components
├── config.py
└── main.py
```

---

## ⚙️ Setup & Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the dashboard:**
   ```bash
   streamlit run main.py
   ```

---

## 🛡️ Risk Disclaimer
This application is designed strictly for **research, education, analysis, and decision support**. It does not guarantee profit, successful trades, or accurate predictions. All trade setups and scenarios are probabilistic. Users should independently verify information and consider their own risk tolerance before making financial decisions.
