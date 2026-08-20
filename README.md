# AI Stock Trading & Investment Analysis Platform

🚀 **[Live Demo: Try the Web App Here](https://stock-analyzer-i6j5e5wgujndqisabqhhaz.streamlit.app/)** 🚀

An AI-powered stock analysis platform that automatically collects market data, technical indicators, fundamentals, news, and price-action signals â€” converting them into clear analyses for **intraday trading, swing/short-term trading, and long-term investing**.

> **Important:** This is a decision-support and research tool. It does **not** guarantee profits or certainty about future prices.

---

## ðŸ”´ Live Demo

**[Try it live â†’](https://stock-analyzer.streamlit.app)**

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://stock-analyzer.streamlit.app)

---

## ðŸš€ What It Does

Enter any stock ticker (e.g., `TCS`, `RELIANCE`, `AAPL`, `NVDA`) and get an instant comprehensive analysis:

- ðŸ“Š Live market snapshot with price, volume, and 52-week range
- ðŸ“ˆ Interactive candlestick chart with MAs, Bollinger Bands, and S/R levels
- ðŸ”§ 40+ technical indicators with plain-English interpretations
- ðŸŽ¯ Automated support & resistance with strength ratings
- ðŸ“‹ Price action & candlestick pattern detection
- â° Multi-timeframe trend alignment (5m â†’ Monthly)
- ðŸ’¹ Intraday, swing, and long-term trade setups
- ðŸ¦ Fundamental analysis with quality scoring
- ðŸ“° News sentiment analysis
- âš–ï¸ Risk assessment and position-sizing calculator

---

## ðŸ“Š Screenshots

The dashboard provides a dark-themed professional interface with:

- **Quick View** â€” 30-second summary with verdicts
- **Interactive Charts** â€” Zoom, pan, overlay indicators
- **Technical Indicators** â€” Trend, momentum, volatility, volume
- **Support/Resistance** â€” Auto-detected levels with Fibonacci & pivots
- **Trade Setups** â€” Entry, SL, targets, R:R ratios
- **Scenario Analysis** â€” Bull/Base/Bear cases
- **Position Calculator** â€” Risk-based sizing

---

## ðŸŒ Supported Markets

| Exchange | Examples | Notes |
|----------|----------|-------|
| **NSE** (India) | RELIANCE, TCS, INFY, HDFCBANK | Appends `.NS` automatically |
| **BSE** (India) | RELIANCE, TCS, INFY, HDFCBANK | Appends `.BO` automatically |
| **NYSE** | JPM, GS, BAC | US equities |
| **NASDAQ** | AAPL, MSFT, NVDA, TSLA | US tech & growth |
| **Crypto** | BTC-USD, ETH-USD | Yahoo Finance format |

---

## ðŸ—ï¸ Architecture

Modular, provider-agnostic design:

```
stock-analyzer/
â”œâ”€â”€ data/                    # Market data providers
â”‚   â”œâ”€â”€ market_data.py       #   Quote, history, fundamentals (yfinance)
â”‚   â””â”€â”€ news.py              #   News aggregation & sentiment
â”œâ”€â”€ indicators/              # Technical indicator calculations
â”‚   â”œâ”€â”€ trend.py             #   SMA, EMA, VWAP, Supertrend, ADX
â”‚   â”œâ”€â”€ momentum.py          #   RSI, MACD, Stochastic, ROC
â”‚   â”œâ”€â”€ volatility.py        #   ATR, Bollinger Bands, Historical Vol
â”‚   â””â”€â”€ volume.py            #   OBV, A/D, Relative Volume
â”œâ”€â”€ analysis/                # Analysis engines
â”‚   â”œâ”€â”€ support_resistance.py #  S/R levels, Fibonacci, Pivots
â”‚   â”œâ”€â”€ price_action.py      #   Trend structure, patterns, gaps
â”‚   â”œâ”€â”€ patterns.py          #   Candlestick pattern detection
â”‚   â”œâ”€â”€ multi_timeframe.py   #   MTF trend alignment
â”‚   â”œâ”€â”€ intraday.py          #   Intraday setups & scenarios
â”‚   â”œâ”€â”€ swing.py             #   Swing/short-term analysis
â”‚   â”œâ”€â”€ long_term.py         #   Long-term investment analysis
â”‚   â”œâ”€â”€ risk.py              #   Risk assessment
â”‚   â””â”€â”€ scoring.py           #   Technical scoring engine
â”œâ”€â”€ ai/
â”‚   â””â”€â”€ analyst.py           # AI reasoning & explanation engine
â”œâ”€â”€ alerts/
â”‚   â”œâ”€â”€ technical_alerts.py  # Technical signal alerts
â”‚   â””â”€â”€ price_alerts.py      # Price level alerts
â”œâ”€â”€ .streamlit/
â”‚   â””â”€â”€ config.toml          # Streamlit theme & server config
â”œâ”€â”€ config.py                # Exchange configs, defaults
â”œâ”€â”€ main.py                  # Main Streamlit dashboard
â””â”€â”€ requirements.txt         # Python dependencies
```

---

## âš™ï¸ Local Setup

### Prerequisites
- Python 3.10+
- pip

### Install & Run

```bash
# Clone the repository
git clone https://github.com/bmushtaq65-eng/stock-analyzer.git
cd stock-analyzer

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run main.py
```

Open **http://localhost:8501** in your browser.

---

## â˜ï¸ Deploy to Streamlit Community Cloud (Free)

### Option A: One-Click Deploy

1. **Push your code to GitHub** (already done)
2. Go to [**share.streamlit.io**](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click **"New app"**
5. Select:
   - **Repository:** `bmushtaq65-eng/stock-analyzer`
   - **Branch:** `master`
   - **Main file path:** `main.py`
6. Click **"Deploy"**
7. Your app will be live at `https://stock-analyzer.streamlit.app`

### Option B: Streamlit.toml Config

The `.streamlit/config.toml` is already configured with:
- Dark theme matching the dashboard
- Headless server mode (required for cloud)
- CORS and XSRF protection enabled

### Free Tier Limits
- **1 GB RAM** â€” sufficient for this app
- **Community apps** are public by default
- Auto-restarts after 1 hour of inactivity

---

## ðŸ”§ Alternative Deployment Options

### Render (Free Tier)

Create a `render.yaml` at the project root:

```yaml
services:
  - type: web
    name: stock-analyzer
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run main.py --server.port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
```

Then:
1. Connect your GitHub repo on [render.com](https://render.com)
2. Select "New > Blueprint" and point to the repo
3. Render auto-detects the `render.yaml`

### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and init
railway login
railway init

# Set build/start commands
railway variables set PYTHON_VERSION=3.11
railway up
```

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t stock-analyzer .
docker run -p 8501:8501 stock-analyzer
```

---

## âš ï¸ Known Limitations

| Issue | Details |
|-------|---------|
| **Indian stock suffixes** | Some tickers may need manual `.NS`/`.BO` suffix for yfinance |
| **Intraday data** | yfinance limits intraday history (5m: 60 days, 1m: 7 days) |
| **Fundamentals** | Indian stock fundamentals may be limited via yfinance |
| **News** | Web-scraped news may fail if source sites change |
| **Real-time data** | yfinance provides ~15 min delayed quotes, not real-time |

---

## ðŸ›¡ï¸ Risk Disclaimer

This application is designed strictly for **research, education, analysis, and decision support**. It does not guarantee profit, successful trades, or accurate predictions. All trade setups and scenarios are probabilistic. Users should independently verify information and consider their own risk tolerance before making financial decisions.

---

## ðŸ“„ License

MIT License â€” use freely, modify freely, deploy freely.

---

**Built with:** Python, Streamlit, yfinance, Plotly, pandas-ta, scipy


