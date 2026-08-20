"""
AI Stock Trading & Investment Analysis Platform
Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import EXCHANGES, INDIAN_STOCKS, TIMEFRAMES, TA_DEFAULTS, RISK_DEFAULTS
from data.market_data import MarketDataProvider
from data.news import NewsProvider
from indicators import calculate_all_indicators
from analysis.support_resistance import find_support_resistance
from analysis.price_action import analyze_price_action
from analysis.patterns import detect_candlestick_patterns
from analysis.multi_timeframe import multi_timeframe_analysis
from analysis.intraday import intraday_analysis
from analysis.swing import swing_analysis
from analysis.long_term import long_term_analysis
from analysis.risk import risk_analysis
from analysis.scoring import technical_score
from ai.analyst import generate_full_analysis
from alerts.technical_alerts import check_technical_alerts
from alerts.price_alerts import check_price_alerts

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Stock Trading Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 1.8em; color: white; }
    .main-header p { margin: 5px 0 0 0; color: #a0aec0; font-size: 0.95em; }

    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-card .label { color: #94a3b8; font-size: 0.85em; }
    .metric-card .value { color: #f1f5f9; font-size: 1.4em; font-weight: 700; }
    .metric-card .sub { color: #64748b; font-size: 0.8em; }

    .bullish { color: #22c55e; }
    .bearish { color: #ef4444; }
    .neutral { color: #eab308; }

    .alert-card {
        background: #1e293b;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .alert-card.warning { border-left-color: #f59e0b; }
    .alert-card.danger { border-left-color: #ef4444; }
    .alert-card.success { border-left-color: #22c55e; }

    .section-header {
        background: #1e293b;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 16px 0 12px 0;
    }
    .section-header h2 { margin: 0; font-size: 1.2em; color: #e2e8f0; }

    .score-bar {
        height: 8px;
        background: #334155;
        border-radius: 4px;
        overflow: hidden;
    }
    .score-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }

    div[data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize sidebar variables with defaults before the sidebar block
stock_input = ""
exchange = "NSE"
analysis_tf = "Swing / Short Term"
investment = 100000
risk_tolerance = "Moderate"
max_risk_pct = 2.0

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Stock Analysis Platform")
    st.markdown("---")

    # Stock input
    stock_input = st.text_input(
        "🔍 Enter Stock Name / Ticker",
        placeholder="e.g., RELIANCE, TCS, AAPL",
        help="Enter a stock symbol or company name"
    )

    # Exchange selection
    exchange = st.selectbox(
        "🏦 Exchange",
        options=list(EXCHANGES.keys()),
        index=0,
    )

    # Analysis timeframe
    analysis_tf = st.selectbox(
        "⏱ Analysis Timeframe",
        options=["Intraday", "Swing / Short Term", "Medium Term", "Long Term"],
        index=1,
    )

    st.markdown("---")

    # Investment amount
    investment = st.number_input(
        "💰 Investment Amount",
        min_value=0,
        value=int(RISK_DEFAULTS["default_investment"]),
        step=10000,
        help="Optional: Enter your investment capital for position sizing",
    )

    # Risk tolerance
    risk_tolerance = st.select_slider(
        "⚖️ Risk Tolerance",
        options=["Conservative", "Moderate", "Aggressive"],
        value="Moderate",
    )

    # Risk per trade
    max_risk_pct = st.slider(
        "🎯 Max Risk Per Trade (%)",
        min_value=0.5,
        max_value=5.0,
        value=RISK_DEFAULTS["max_risk_per_trade_pct"],
        step=0.5,
    )

    st.markdown("---")
    st.caption("⚠ This is an analysis tool, not financial advice.")
    st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")


# ── Main Content ─────────────────────────────────────────────
def main():
    global stock_input, exchange

    # Check for session state updates (button clicks)
    if "stock_input" in st.session_state and st.session_state["stock_input"]:
        stock_input = st.session_state.pop("stock_input")
    if "exchange_override" in st.session_state:
        exchange = st.session_state.pop("exchange_override")

    if not stock_input:
        st.markdown("""
        <div class="main-header">
            <h1>📈 AI Stock Trading & Investment Analysis Platform</h1>
            <p>Professional-grade stock analysis powered by data. Enter a stock ticker to begin.</p>
        </div>
        """, unsafe_allow_html=True)

        # Quick start guide
        st.markdown("### Getting Started")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**1. Enter Stock**\nType any stock symbol (e.g., TCS, RELIANCE, AAPL)")
        with col2:
            st.info("**2. Select Exchange**\nChoose NSE, BSE, NYSE, or NASDAQ")
        with col3:
            st.info("**3. Analyze**\nThe system automatically fetches and analyzes all data")

        st.markdown("---")
        st.markdown("### Popular Stocks")

        tabs = st.tabs(["🇮🇳 NSE", "🇺🇸 US"])
        with tabs[0]:
            cols = st.columns(4)
            popular_nse = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN", "ITC", "BAJFINANCE", "TATAMOTORS"]
            for i, stock in enumerate(popular_nse):
                if cols[i % 4].button(stock, key=f"pop_{stock}", use_container_width=True):
                    st.session_state["stock_input"] = stock
                    st.rerun()

        with tabs[1]:
            cols = st.columns(4)
            popular_us = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM"]
            for i, stock in enumerate(popular_us):
                if cols[i % 4].button(stock, key=f"us_{stock}", use_container_width=True):
                    st.session_state["stock_input"] = stock
                    st.session_state["exchange_override"] = "NYSE" if stock in ["JPM"] else "NASDAQ"
                    st.rerun()

        return

    # ── Run Analysis ─────────────────────────────────────────
    with st.spinner(f"Fetching data for {stock_input.upper()}..."):
        try:
            run_full_analysis(stock_input.upper(), exchange, analysis_tf, investment, risk_tolerance, max_risk_pct)
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            st.exception(e)


def run_full_analysis(ticker, exchange, timeframe, investment, risk_tolerance, max_risk_pct):
    """Run the complete analysis pipeline."""

    # ── STEP 1: Fetch Data ───────────────────────────────────
    provider = MarketDataProvider(exchange)
    news_provider = NewsProvider()

    with st.status("Fetching market data...", expanded=True) as status:
        st.write("📡 Fetching quote data...")
        quote = provider.get_quote(ticker)

        if "error" in quote:
            st.error(f"❌ {quote['error']}")
            st.info("Try a different ticker or exchange combination.")
            return

        st.write("📊 Fetching historical data...")
        daily_df = provider.get_history(ticker, period="2y", interval="1d")
        weekly_df = provider.get_history(ticker, period="5y", interval="1wk")
        monthly_df = provider.get_history(ticker, period="max", interval="1mo")

        st.write("📈 Fetching intraday data...")
        df_5m = provider.get_intraday(ticker, interval="5m", period="5d")
        df_15m = provider.get_intraday(ticker, interval="15m", period="1mo")
        df_1h = provider.get_intraday(ticker, interval="60m", period="3mo")

        st.write("📰 Fetching news...")
        news = news_provider.get_news(ticker, exchange)

        st.write("🏢 Fetching fundamentals...")
        financials = provider.get_financials(ticker)
        holder_data = provider.get_holder_data(ticker)

        status.update(label=f"✅ Data loaded for {quote.get('name', ticker)}", state="complete")

    # ── STEP 2: Calculate Indicators ─────────────────────────
    with st.status("Calculating technical indicators..."):
        if not daily_df.empty:
            daily_df = calculate_all_indicators(daily_df)
        if not df_5m.empty:
            df_5m = calculate_all_indicators(df_5m)
        if not df_15m.empty:
            df_15m = calculate_all_indicators(df_15m)
        if not df_1h.empty:
            df_1h = calculate_all_indicators(df_1h)
        if not weekly_df.empty:
            weekly_df = calculate_all_indicators(weekly_df)
        if not monthly_df.empty:
            monthly_df = calculate_all_indicators(monthly_df)

        # Get latest indicators from daily
        latest = daily_df.iloc[-1].to_dict() if not daily_df.empty else {}
        for key in list(latest.keys()):
            val = latest[key]
            try:
                if pd.isna(val) if isinstance(val, float) else False:
                    del latest[key]
            except:
                pass

        st.write("✅ Indicators calculated")
        st.empty()

    # ── STEP 3: Run Analysis Engines ─────────────────────────
    with st.status("Running analysis engines..."):
        sr_data = find_support_resistance(daily_df)
        price_action = analyze_price_action(daily_df)
        candlestick_patterns = detect_candlestick_patterns(daily_df)
        mtf_data = multi_timeframe_analysis(daily_df, weekly_df, monthly_df, df_1h, df_15m, df_5m)
        intraday_data = intraday_analysis(daily_df, df_5m, quote)
        swing_data = swing_analysis(daily_df, quote)
        longterm_data = long_term_analysis(quote, daily_df, financials, holder_data)
        risk_data = risk_analysis(quote, daily_df, sr_data)
        tech_score = technical_score(daily_df)
        tech_alerts = check_technical_alerts(daily_df, quote)
        price_alerts = check_price_alerts(quote.get("current_price", 0), sr_data, quote)

        st.write("✅ All analysis complete")
        st.empty()

    # ── STEP 4: Generate AI Analysis ─────────────────────────
    with st.status("Generating analysis..."):
        ai_analysis = generate_full_analysis(
            quote, latest, sr_data, price_action, mtf_data,
            intraday_data, swing_data, longterm_data, risk_data,
            tech_score, news, timeframe,
        )
        st.empty()

    # ══════════════════════════════════════════════════════════
    # ── DISPLAY DASHBOARD ─────────────────────────────────────
    # ══════════════════════════════════════════════════════════

    # Header
    currency = quote.get("currency", "")
    current_price = quote.get("current_price", 0)
    prev_close = quote.get("previous_close")
    change = current_price - prev_close if prev_close else 0
    change_pct = (change / prev_close * 100) if prev_close else 0
    change_color = "#22c55e" if change >= 0 else "#ef4444"
    change_arrow = "▲" if change >= 0 else "▼"

    st.markdown(f"""
    <div class="main-header">
        <h1>📈 {quote.get('name', ticker)} ({ticker})</h1>
        <p>{exchange} | {quote.get('sector', 'N/A')} | {quote.get('industry', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick Metrics Row ────────────────────────────────────
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    with m1:
        st.metric("Price", f"{currency}{current_price}",
                  f"{change_arrow} {abs(change_pct):.2f}%")
    with m2:
        st.metric("Open", f"{currency}{quote.get('open', 'N/A')}")
    with m3:
        st.metric("Day High", f"{currency}{quote.get('day_high', 'N/A')}")
    with m4:
        st.metric("Day Low", f"{currency}{quote.get('day_low', 'N/A')}")
    with m5:
        vol = quote.get('volume', 0)
        st.metric("Volume", f"{vol:,}" if vol else "N/A")
    with m6:
        mc = quote.get('market_cap', 0)
        st.metric("Market Cap", f"₹{mc/1e9:.0f}B" if mc else "N/A")
    with m7:
        st.metric("P/E", f"{quote.get('pe_ratio', 'N/A'):.1f}" if quote.get('pe_ratio') else "N/A")

    # 52-week range bar
    w52h = quote.get("fifty_two_week_high", 0)
    w52l = quote.get("fifty_two_week_low", 0)
    if w52h and w52l and w52h > w52l:
        pct_52w = (current_price - w52l) / (w52h - w52l) * 100
        st.markdown(f"""
        <div style="background:#1e293b; padding:12px 16px; border-radius:8px; margin:10px 0;">
            <span style="color:#94a3b8; font-size:0.85em;">52-Week Range: {currency}{w52l:.2f} — {currency}{w52h:.2f}</span>
            <div style="background:#334155; height:6px; border-radius:3px; margin-top:6px; position:relative;">
                <div style="width:{pct_52w:.1f}%; background:linear-gradient(90deg, #ef4444, #eab308, #22c55e); height:100%; border-radius:3px;"></div>
                <div style="position:absolute; left:{pct_52w:.1f}%; top:-4px; width:3px; height:14px; background:white; border-radius:2px; transform:translateX(-1px);"></div>
            </div>
            <span style="color:#64748b; font-size:0.75em;">Position in range: {pct_52w:.0f}%</span>
        </div>
        """, unsafe_allow_html=True)

    # ── ALERTS ────────────────────────────────────────────────
    all_alerts = tech_alerts + price_alerts
    if all_alerts:
        with st.expander(f"🔔 Active Alerts ({len(all_alerts)})", expanded=len(all_alerts) > 0):
            cols = st.columns(2)
            for i, alert in enumerate(all_alerts[:10]):
                col = cols[i % 2]
                severity = alert.get("severity", "")
                icon = {"Warning": "⚠️", "Signal": "📊", "Notable": "📌", "Opportunity": "💡", "Watch": "👀", "Strong Signal": "🔥"}.get(severity, "ℹ️")
                col.markdown(f"""
                <div class="alert-card {'warning' if 'Warning' in severity else 'success' if 'Opportunity' in severity else ''}">
                    <strong>{icon} {alert['type']}</strong><br>
                    <span style="color:#94a3b8;">{alert['message']}</span>
                </div>
                """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────
    tab_names = [
        "📊 Quick View", "📈 Chart", "🔧 Technical Indicators",
        "🎯 Support/Resistance", "📋 Price Action", "🕯 Candlestick Patterns",
        "⏰ Multi-Timeframe", "💹 Intraday", "📉 Swing Trading",
        "🏦 Long-Term Analysis", "📰 News & Sentiment",
        "⚖️ Risk Analysis", "🎯 Trade Setups", "📊 Scenarios",
        "🧮 Position Calculator"
    ]
    tabs = st.tabs(tab_names)

    # ── TAB: Quick View ───────────────────────────────────────
    with tabs[0]:
        _render_quick_view(ai_analysis, quote, tech_score, longterm_data, risk_data)

    # ── TAB: Chart ────────────────────────────────────────────
    with tabs[1]:
        _render_chart(daily_df, df_5m, df_15m, df_1h, sr_data, ticker)

    # ── TAB: Technical Indicators ─────────────────────────────
    with tabs[2]:
        _render_indicators(latest, daily_df)

    # ── TAB: Support/Resistance ───────────────────────────────
    with tabs[3]:
        _render_support_resistance(sr_data, quote)

    # ── TAB: Price Action ─────────────────────────────────────
    with tabs[4]:
        _render_price_action(price_action)

    # ── TAB: Candlestick Patterns ─────────────────────────────
    with tabs[5]:
        _render_candlestick_patterns(candlestick_patterns)

    # ── TAB: Multi-Timeframe ──────────────────────────────────
    with tabs[6]:
        _render_multi_timeframe(mtf_data)

    # ── TAB: Intraday ─────────────────────────────────────────
    with tabs[7]:
        _render_intraday(intraday_data)

    # ── TAB: Swing Trading ────────────────────────────────────
    with tabs[8]:
        _render_swing(swing_data)

    # ── TAB: Long-Term ────────────────────────────────────────
    with tabs[9]:
        _render_long_term(longterm_data, quote)

    # ── TAB: News ─────────────────────────────────────────────
    with tabs[10]:
        _render_news(news)

    # ── TAB: Risk ─────────────────────────────────────────────
    with tabs[11]:
        _render_risk(risk_data)

    # ── TAB: Trade Setups ─────────────────────────────────────
    with tabs[12]:
        _render_trade_setups(intraday_data, swing_data, tech_score, sr_data)

    # ── TAB: Scenarios ────────────────────────────────────────
    with tabs[13]:
        _render_scenarios(ai_analysis)

    # ── TAB: Position Calculator ──────────────────────────────
    with tabs[14]:
        _render_calculator(investment, risk_tolerance, max_risk_pct, current_price, swing_data, sr_data, currency)

    # ── Data timestamp ────────────────────────────────────────
    st.markdown("---")
    st.caption(f"Data as of: {quote.get('last_updated', 'N/A')} | Market State: {quote.get('market_state', 'N/A')} | "
               f"Exchange Timezone: {quote.get('exchange_timezone', 'N/A')}")


# ══════════════════════════════════════════════════════════════
# ── RENDER FUNCTIONS ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════════

def _render_quick_view(ai, quote, tech_score, longterm_data, risk_data):
    """Render the quick view / 30-second summary."""
    dashboard = ai.get("dashboard", {})

    st.markdown('<div class="section-header"><h2>⚡ Quick View — 30-Second Summary</h2></div>', unsafe_allow_html=True)

    # Dashboard metrics
    cols = st.columns(5)
    labels = ["Overall Trend", "Technical Score", "Fundamental Score", "Momentum", "Risk"]
    keys = ["overall_trend", "technical_score", "fundamental_score", "momentum", "risk"]
    colors = {
        "Bullish": "#22c55e", "Bearish": "#ef4444", "Neutral": "#eab308",
        "Low": "#22c55e", "MODERATE": "#eab308", "HIGH": "#f59e0b", "VERY HIGH": "#ef4444",
    }

    for i, (label, key) in enumerate(zip(labels, keys)):
        val = dashboard.get(key, "N/A")
        with cols[i]:
            color = "white"
            for k, c in colors.items():
                if k in str(val):
                    color = c
                    break
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">{label}</div>
                <div class="value" style="color:{color};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # Verdicts
    st.markdown("### 📋 Verdicts")
    v1, v2, v3 = st.columns(3)
    with v1:
        intra = dashboard.get("intraday", "WAIT")
        color = "#22c55e" if "BUY" in intra else ("#ef4444" if "SELL" in intra else "#eab308")
        st.markdown(f"**Intraday:** <span style='color:{color}; font-size:1.2em;'>{intra}</span>", unsafe_allow_html=True)
    with v2:
        short = dashboard.get("short_term", "NEUTRAL")
        color = "#22c55e" if "BULLISH" in short else ("#ef4444" if "BEARISH" in short else "#eab308")
        st.markdown(f"**Short Term:** <span style='color:{color}; font-size:1.2em;'>{short}</span>", unsafe_allow_html=True)
    with v3:
        lt = dashboard.get("long_term", "FAIR")
        color = "#22c55e" if "ATTRACTIVE" in lt else ("#ef4444" if "AVOID" in lt else "#eab308")
        st.markdown(f"**Long Term:** <span style='color:{color}; font-size:1.2em;'>{lt}</span>", unsafe_allow_html=True)

    # Quick View text
    st.markdown("---")
    st.markdown(ai.get("quick_view", ""))

    # What's happening + Why
    st.markdown("### 🔍 What Is Happening?")
    st.info(ai.get("what_happening", ""))

    st.markdown("### 🤔 Why Is It Happening?")
    st.info(ai.get("why_happening", ""))

    # Signal confidence
    confidence = ai.get("signal_confidence", {})
    if confidence:
        st.markdown("### 📊 Signal Confidence")
        cols = st.columns(4)
        for i, (key, val) in enumerate(confidence.items()):
            with cols[i]:
                label = key.replace("_", " ").title()
                color = "#22c55e" if val >= 65 else ("#ef4444" if val <= 35 else "#eab308")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">{label}</div>
                    <div class="value" style="color:{color};">{val}%</div>
                </div>
                """, unsafe_allow_html=True)

    # Watch next
    st.markdown("### 👀 What Should I Watch Next?")
    st.warning(ai.get("watch_next", "Monitor key levels."))


def _render_chart(daily_df, df_5m, df_15m, df_1h, sr_data, ticker):
    """Render interactive candlestick chart."""
    st.markdown('<div class="section-header"><h2>📈 Interactive Price Chart</h2></div>', unsafe_allow_html=True)

    # Timeframe selector
    tf_cols = st.columns([2, 1, 1, 1])
    with tf_cols[1]:
        show_volume = st.checkbox("Volume", value=True)
    with tf_cols[2]:
        show_ma = st.checkbox("Moving Averages", value=True)
    with tf_cols[3]:
        show_sr = st.checkbox("S/R Levels", value=True)

    chart_tf = st.select_slider(
        "Chart Timeframe",
        options=["5m", "15m", "1H", "Daily", "Weekly"],
        value="Daily",
    )

    # Select data
    tf_map = {"5m": df_5m, "15m": df_15m, "1H": df_1h, "Daily": daily_df, "Weekly": daily_df}
    df = tf_map.get(chart_tf, daily_df)

    if df.empty:
        st.warning("No data available for this timeframe")
        return

    # Create chart
    rows = 2 if show_volume else 1
    row_heights = [0.7, 0.3] if show_volume else [1.0]

    fig = make_subplots(
        rows=rows, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
        ),
        row=1, col=1,
    )

    # Moving averages
    if show_ma:
        colors = {"sma_20": "#3b82f6", "sma_50": "#f59e0b", "sma_200": "#ef4444",
                  "ema_9": "#22c55e", "ema_20": "#3b82f6", "ema_50": "#f59e0b"}
        for col_name, color in colors.items():
            if col_name in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[col_name], name=col_name.upper(),
                              line=dict(width=1, color=color), opacity=0.8),
                    row=1, col=1,
                )

    # Bollinger Bands
    if "bb_upper" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_upper"], name="BB Upper",
                      line=dict(width=1, color="rgba(99,102,241,0.3)", dash="dot")),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_lower"], name="BB Lower",
                      line=dict(width=1, color="rgba(99,102,241,0.3)", dash="dot"),
                      fill="tonexty", fillcolor="rgba(99,102,241,0.05)"),
            row=1, col=1,
        )

    # Supertrend
    if "supertrend" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["supertrend"], name="Supertrend",
                      line=dict(width=2, color="rgba(168,85,247,0.8)")),
            row=1, col=1,
        )

    # Support/Resistance lines
    if show_sr:
        resistances = sr_data.get("resistance_levels", [])
        supports = sr_data.get("support_levels", [])

        for r in resistances[:3]:
            fig.add_hline(y=r["price"], line_dash="dash", line_color="#ef4444",
                         annotation_text=f"R {r['price']}", row=1, col=1)
        for s in supports[:3]:
            fig.add_hline(y=s["price"], line_dash="dash", line_color="#22c55e",
                         annotation_text=f"S {s['price']}", row=1, col=1)

        # Previous day high/low
        prev_hl = sr_data.get("previous_highs_lows", {})
        if prev_hl.get("prev_day_high"):
            fig.add_hline(y=prev_hl["prev_day_high"], line_dash="dot",
                         line_color="rgba(255,255,255,0.3)",
                         annotation_text="Prev High", row=1, col=1)
        if prev_hl.get("prev_day_low"):
            fig.add_hline(y=prev_hl["prev_day_low"], line_dash="dot",
                         line_color="rgba(255,255,255,0.3)",
                         annotation_text="Prev Low", row=1, col=1)

    # Volume
    if show_volume and rows > 1:
        colors = ["#22c55e" if c >= o else "#ef4444" for c, o in zip(df["close"], df["open"])]
        fig.add_trace(
            go.Bar(x=df.index, y=df["volume"], name="Volume",
                  marker_color=colors, opacity=0.7),
            row=2, col=1,
        )

    # Layout
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        height=600,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=20, t=30, b=30),
    )
    fig.update_xaxes(gridcolor="#1e293b")
    fig.update_yaxes(gridcolor="#1e293b")

    st.plotly_chart(fig, use_container_width=True)


def _render_indicators(latest, daily_df):
    """Render technical indicators."""
    st.markdown('<div class="section-header"><h2>🔧 Technical Indicators</h2></div>', unsafe_allow_html=True)

    # Trend indicators
    st.markdown("### 📈 Trend Indicators")
    cols = st.columns(4)
    trend_items = [
        ("SMA 20", latest.get("sma_20")), ("SMA 50", latest.get("sma_50")),
        ("SMA 100", latest.get("sma_100")), ("SMA 200", latest.get("sma_200")),
        ("EMA 9", latest.get("ema_9")), ("EMA 20", latest.get("ema_20")),
        ("EMA 50", latest.get("ema_50")), ("EMA 200", latest.get("ema_200")),
        ("VWAP", latest.get("vwap")), ("Supertrend", latest.get("supertrend")),
        ("ADX", latest.get("adx")), ("+DI", latest.get("plus_di")),
    ]
    for i, (name, val) in enumerate(trend_items):
        with cols[i % 4]:
            display = f"{val:.2f}" if val and not _isnan(val) else "N/A"
            color = "#94a3b8" if val is None else "white"
            st.markdown(f"**{name}**<br><span style='color:{color}; font-size:1.1em;'>{display}</span>", unsafe_allow_html=True)

    # Supertrend direction
    st_dir = latest.get("supertrend_direction")
    if st_dir is not None:
        st.markdown(f"**Supertrend Direction:** {'🟢 Bullish' if st_dir == 1 else '🔴 Bearish'}")

    # ADX interpretation
    adx = latest.get("adx")
    if adx and not _isnan(adx):
        if adx > 25:
            st.success(f"ADX at {adx:.1f} — Strong trending market")
        else:
            st.warning(f"ADX at {adx:.1f} — Weak trend / ranging market")

    st.markdown("---")

    # Momentum indicators
    st.markdown("### ⚡ Momentum Indicators")
    cols = st.columns(4)
    momentum_items = [
        ("RSI 14", latest.get("rsi")), ("MACD", latest.get("macd")),
        ("MACD Signal", latest.get("macd_signal")), ("MACD Histogram", latest.get("macd_histogram")),
        ("Stoch RSI K", latest.get("stoch_rsi_k")), ("Stoch RSI D", latest.get("stoch_rsi_d")),
        ("Stoch %K", latest.get("stoch_k")), ("Stoch %D", latest.get("stoch_d")),
        ("ROC", latest.get("roc")),
    ]
    for i, (name, val) in enumerate(momentum_items):
        with cols[i % 4]:
            display = f"{val:.2f}" if val and not _isnan(val) else "N/A"
            color = "#94a3b8" if val is None else "white"
            st.markdown(f"**{name}**<br><span style='color:{color}; font-size:1.1em;'>{display}</span>", unsafe_allow_html=True)

    # RSI interpretation
    rsi = latest.get("rsi")
    if rsi and not _isnan(rsi):
        if rsi > 70:
            st.warning(f"RSI at {rsi:.1f} — Overbought zone. Caution: may see pullback.")
        elif rsi < 30:
            st.success(f"RSI at {rsi:.1f} — Oversold zone. Potential bounce opportunity.")
        elif rsi > 55:
            st.info(f"RSI at {rsi:.1f} — Bullish momentum, not yet overbought.")
        elif rsi < 45:
            st.info(f"RSI at {rsi:.1f} — Bearish momentum, not yet oversold.")
        else:
            st.info(f"RSI at {rsi:.1f} — Neutral zone.")

    # MACD interpretation
    macd = latest.get("macd")
    macd_sig = latest.get("macd_signal")
    macd_hist = latest.get("macd_histogram")
    if macd and macd_sig:
        if macd > macd_sig:
            st.success("MACD above signal line — bullish momentum")
        else:
            st.warning("MACD below signal line — bearish momentum")
        if macd_hist and not _isnan(macd_hist):
            if macd_hist > 0:
                st.info(f"MACD Histogram positive ({macd_hist:.2f}) — bullish momentum strengthening")
            else:
                st.info(f"MACD Histogram negative ({macd_hist:.2f}) — bearish momentum strengthening")

    st.markdown("---")

    # Volatility indicators
    st.markdown("### 📊 Volatility Indicators")
    cols = st.columns(4)
    vol_items = [
        ("ATR", latest.get("atr")), ("BB Upper", latest.get("bb_upper")),
        ("BB Middle", latest.get("bb_middle")), ("BB Lower", latest.get("bb_lower")),
        ("BB Width", latest.get("bb_width")), ("BB %B", latest.get("bb_pct_b")),
        ("Historical Vol", latest.get("historical_volatility")),
    ]
    for i, (name, val) in enumerate(vol_items):
        with cols[i % 4]:
            display = f"{val:.2f}" if val and not _isnan(val) else "N/A"
            color = "#94a3b8" if val is None else "white"
            st.markdown(f"**{name}**<br><span style='color:{color}; font-size:1.1em;'>{display}</span>", unsafe_allow_html=True)

    # BB interpretation
    bb_pct = latest.get("bb_pct_b")
    if bb_pct and not _isnan(bb_pct):
        if bb_pct > 0.8:
            st.warning("Price near upper Bollinger Band — potential resistance")
        elif bb_pct < 0.2:
            st.info("Price near lower Bollinger Band — potential support/bounce")

    st.markdown("---")

    # Volume indicators
    st.markdown("### 📊 Volume Indicators")
    cols = st.columns(4)
    vol_ind = [
        ("Volume", latest.get("volume")), ("Vol SMA 20", latest.get("volume_sma_20")),
        ("Rel Volume", latest.get("relative_volume")), ("OBV", latest.get("obv")),
        ("A/D Line", latest.get("ad_line")),
    ]
    for i, (name, val) in enumerate(vol_ind):
        with cols[i % 4]:
            if val and not _isnan(val):
                if abs(val) > 1e6:
                    display = f"{val/1e6:.2f}M"
                else:
                    display = f"{val:.2f}"
            else:
                display = "N/A"
            color = "#94a3b8" if val is None else "white"
            st.markdown(f"**{name}**<br><span style='color:{color}; font-size:1.1em;'>{display}</span>", unsafe_allow_html=True)


def _render_support_resistance(sr_data, quote):
    """Render support and resistance analysis."""
    st.markdown('<div class="section-header"><h2>🎯 Support & Resistance Analysis</h2></div>', unsafe_allow_html=True)

    current_price = quote.get("current_price", 0)

    # Resistance levels
    st.markdown("### 🔴 Resistance Levels")
    resistances = sr_data.get("resistance_levels", [])
    if resistances:
        for i, r in enumerate(resistances[:5], 1):
            strength = r.get("strength", "N/A")
            color = {"Very Strong": "#ef4444", "Strong": "#f59e0b", "Moderate": "#eab308", "Weak": "#64748b"}.get(strength, "#64748b")
            dist = ((r["price"] - current_price) / current_price * 100) if current_price > 0 else 0
            st.markdown(f"""
            <div style="background:#1e293b; border-left:4px solid {color}; padding:12px 16px; border-radius:6px; margin:6px 0;">
                <strong style="color:{color};">R{i} — {r['price']:.2f} — {strength}</strong>
                <br><span style="color:#94a3b8; font-size:0.85em;">
                Distance: {dist:.1f}% above current | {r.get('reason', '')}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No clear resistance levels identified")

    # Support levels
    st.markdown("### 🟢 Support Levels")
    supports = sr_data.get("support_levels", [])
    if supports:
        for i, s in enumerate(supports[:5], 1):
            strength = s.get("strength", "N/A")
            color = {"Very Strong": "#22c55e", "Strong": "#22c55e", "Moderate": "#eab308", "Weak": "#64748b"}.get(strength, "#64748b")
            dist = ((current_price - s["price"]) / current_price * 100) if current_price > 0 else 0
            st.markdown(f"""
            <div style="background:#1e293b; border-left:4px solid {color}; padding:12px 16px; border-radius:6px; margin:6px 0;">
                <strong style="color:{color};">S{i} — {s['price']:.2f} — {strength}</strong>
                <br><span style="color:#94a3b8; font-size:0.85em;">
                Distance: {dist:.1f}% below current | {s.get('reason', '')}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No clear support levels identified")

    # Pivot Points
    pivots = sr_data.get("pivot_points", {})
    if pivots:
        st.markdown("### 📐 Pivot Points")
        cols = st.columns(7)
        labels = ["S3", "S2", "S1", "PP", "R1", "R2", "R3"]
        for i, label in enumerate(labels):
            with cols[i]:
                val = pivots.get(label, "N/A")
                color = "#22c55e" if "S" in label else ("#ef4444" if "R" in label else "#3b82f6")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="label">{label}</div>
                    <div class="value" style="color:{color}; font-size:1.1em;">{val}</div>
                </div>
                """, unsafe_allow_html=True)

    # Fibonacci
    fib = sr_data.get("fibonacci", {})
    if fib.get("retracements"):
        st.markdown("### 📏 Fibonacci Retracement Levels")
        st.caption(f"Swing High: {fib['swing_high']:.2f} | Swing Low: {fib['swing_low']:.2f}")
        cols = st.columns(len(fib["retracements"]))
        for i, (level, price) in enumerate(fib["retracements"].items()):
            with cols[i]:
                st.metric(level, f"{price:.2f}")

    if fib.get("extensions"):
        st.markdown("### 📏 Fibonacci Extension Levels")
        cols = st.columns(len(fib["extensions"]))
        for i, (level, price) in enumerate(fib["extensions"].items()):
            with cols[i]:
                st.metric(level, f"{price:.2f}")

    # High Volume Zones
    hvol = sr_data.get("high_volume_zones", [])
    if hvol:
        st.markdown("### 📊 High Volume Price Zones")
        for z in hvol[:5]:
            st.markdown(f"- **{z['price_range']}** — Total Volume: {z['total_volume']:,}")


def _render_price_action(price_action):
    """Render price action analysis."""
    st.markdown('<div class="section-header"><h2>📋 Price Action Analysis</h2></div>', unsafe_allow_html=True)

    if "error" in price_action:
        st.warning(price_action["error"])
        return

    # Trend structure
    structure = price_action.get("trend_structure", {})
    st.markdown("### 📈 Trend Structure")
    st.info(f"**{structure.get('trend', 'N/A')}**")

    cols = st.columns(4)
    with cols[0]:
        st.metric("Higher Highs", structure.get("higher_highs", 0))
    with cols[1]:
        st.metric("Higher Lows", structure.get("higher_lows", 0))
    with cols[2]:
        st.metric("Lower Highs", structure.get("lower_highs", 0))
    with cols[3]:
        st.metric("Lower Lows", structure.get("lower_lows", 0))

    # Swing points
    if structure.get("swing_highs"):
        st.markdown(f"**Recent Swing Highs:** {', '.join(str(h) for h in structure['swing_highs'])}")
    if structure.get("swing_lows"):
        st.markdown(f"**Recent Swing Lows:** {', '.join(str(l) for l in structure['swing_lows'])}")

    # Patterns
    patterns = price_action.get("patterns", [])
    if patterns:
        st.markdown("### 📊 Detected Patterns")
        for p in patterns:
            color = "#22c55e" if "Bullish" in p.get("bias", "") else ("#ef4444" if "Bearish" in p.get("bias", "") else "#eab308")
            st.markdown(f"""
            <div style="background:#1e293b; border-left:4px solid {color}; padding:12px 16px; border-radius:6px; margin:8px 0;">
                <strong style="color:{color};">{p.get('name', 'N/A')}</strong>
                <span style="color:#94a3b8; margin-left:10px;">Bias: {p.get('bias', 'N/A')} | Confidence: {p.get('confidence', 0)}%</span>
                <br><span style="color:#cbd5e1;">{p.get('description', '')}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No significant patterns detected")

    # Consolidation
    consol = price_action.get("consolidation", {})
    if consol.get("is_consolidating"):
        st.warning(f"Stock is consolidating in range {consol.get('lower_range', 'N/A')} — {consol.get('upper_range', 'N/A')} ({consol.get('range_pct', 0)}% range)")

    # Gaps
    gaps = price_action.get("gaps", [])
    if gaps:
        st.markdown("### 🕳 Recent Gaps")
        for g in gaps[-3:]:
            color = "#22c55e" if "Up" in g.get("type", "") else "#ef4444"
            st.markdown(f"- **{g.get('date', '')}**: {g['type']} ({g.get('gap_pct', 0):.1f}%) — {g.get('from', 'N/A')} → {g.get('to', 'N/A')}")


def _render_candlestick_patterns(patterns):
    """Render candlestick patterns."""
    st.markdown('<div class="section-header"><h2>🕯 Candlestick Pattern Analysis</h2></div>', unsafe_allow_html=True)

    if not patterns:
        st.info("No significant candlestick patterns detected in recent candles.")
        return

    for p in patterns:
        color = "#22c55e" if "Bullish" in p.get("bias", "") else ("#ef4444" if "Bearish" in p.get("bias", "") else "#eab308")
        conf = p.get("confidence", 0)
        conf_bar = "█" * (conf // 10) + "░" * (10 - conf // 10)

        st.markdown(f"""
        <div style="background:#1e293b; border-left:4px solid {color}; padding:16px; border-radius:8px; margin:10px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="color:{color}; font-size:1.1em;">{p.get('pattern', 'N/A')}</strong>
                    <span style="margin-left:12px; color:#94a3b8;">{p.get('date', '')}</span>
                </div>
                <div>
                    <span style="color:{color};">{p.get('bias', 'N/A')}</span>
                    <span style="margin-left:8px; color:#64748b;">Confidence: {conf}%</span>
                </div>
            </div>
            <p style="color:#cbd5e1; margin:8px 0 0 0;">{p.get('description', '')}</p>
            <p style="color:{color}; margin:4px 0 0 0; font-size:0.85em;">
                {'⚠ Confirmation required' if p.get('confirmation_required') else '✅ No additional confirmation needed'}
            </p>
        </div>
        """, unsafe_allow_html=True)


def _render_multi_timeframe(mtf_data):
    """Render multi-timeframe analysis."""
    st.markdown('<div class="section-header"><h2>⏰ Multi-Timeframe Analysis</h2></div>', unsafe_allow_html=True)

    timeframes = mtf_data.get("timeframes", {})
    overall = mtf_data.get("overall", {})

    # Display each timeframe
    cols = st.columns(6)
    for i, (tf, data) in enumerate(timeframes.items()):
        with cols[i % 6]:
            bias = data.get("bias", "N/A")
            conf = data.get("confidence", 0)
            color = "#22c55e" if "Bullish" in bias else ("#ef4444" if "Bearish" in bias else "#eab308")
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">{tf}</div>
                <div class="value" style="color:{color}; font-size:1em;">{bias}</div>
                <div class="sub">Confidence: {conf}%</div>
            </div>
            """, unsafe_allow_html=True)

    # Overall
    st.markdown("### 🎯 Combined Signal")
    bias = overall.get("bias", "Neutral")
    color = "#22c55e" if "Bullish" in bias else ("#ef4444" if "Bearish" in bias else "#eab308")
    st.markdown(f"""
    <div style="background:#1e293b; padding:20px; border-radius:10px; border-left:5px solid {color};">
        <strong style="color:{color}; font-size:1.5em;">Overall: {bias}</strong>
        <br><span style="color:#94a3b8;">Confidence: {overall.get('confidence', 0)}% | Alignment: {overall.get('alignment', 0)}%</span>
        <br><span style="color:#cbd5e1;">{overall.get('detail', '')}</span>
    </div>
    """, unsafe_allow_html=True)

    if overall.get("override_note"):
        st.warning(f"⚠ {overall['override_note']}")


def _render_intraday(intraday_data):
    """Render intraday analysis."""
    st.markdown('<div class="section-header"><h2>💹 Intraday Analysis</h2></div>', unsafe_allow_html=True)

    if not intraday_data or "error" in intraday_data:
        st.warning(intraday_data.get("error", "Intraday data unavailable"))
        return

    key = intraday_data.get("key_levels", {})
    momentum = intraday_data.get("momentum", {})
    scenarios = intraday_data.get("scenarios", {})

    # Key levels
    st.markdown("### 📊 Key Levels")
    cols = st.columns(5)
    items = [
        ("Current", key.get("current_price")),
        ("Open", key.get("day_open")),
        ("Prev High", key.get("prev_day_high")),
        ("Prev Low", key.get("prev_day_low")),
        ("VWAP", key.get("vwap")),
    ]
    for i, (label, val) in enumerate(items):
        with cols[i]:
            if val:
                st.metric(label, f"{val:.2f}")

    # Gap
    gap_pct = key.get("gap_pct")
    if gap_pct is not None:
        st.markdown(f"**Gap:** {key.get('gap', 0):.2f} ({gap_pct:.2f}%) — {intraday_data.get('opening_analysis', {}).get('gap_type', 'N/A')}")

    # Momentum
    st.markdown("### ⚡ Momentum")
    cols = st.columns(4)
    with cols[0]:
        st.metric("vs Open", f"{momentum.get('price_vs_open', 0):.2f}%")
    with cols[1]:
        st.metric("vs Prev Close", f"{momentum.get('price_vs_prev_close', 0):.2f}%")
    with cols[2]:
        st.metric("Above VWAP", "Yes" if momentum.get('above_vwap') else "No")
    with cols[3]:
        st.metric("Rel Volume", f"{momentum.get('relative_volume', 1):.2f}x")

    # Scenarios
    st.markdown("### 📋 Scenarios")

    bull = scenarios.get("bullish", {})
    bear = scenarios.get("bearish", {})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🟢 Bullish Scenario")
        st.markdown(f"""
        - **Entry Zone:** {bull.get('entry_zone', 'N/A')}
        - **Stop Loss:** {bull.get('stop_loss', 'N/A')}
        - **Target 1:** {bull.get('target_1', 'N/A')}
        - **Target 2:** {bull.get('target_2', 'N/A')}
        - **Target 3:** {bull.get('target_3', 'N/A')}
        - **Invalidation:** {bull.get('invalidation', 'N/A')}
        """)
    with col2:
        st.markdown("#### 🔴 Bearish Scenario")
        st.markdown(f"""
        - **Entry Zone:** {bear.get('entry_zone', 'N/A')}
        - **Stop Loss:** {bear.get('stop_loss', 'N/A')}
        - **Target 1:** {bear.get('target_1', 'N/A')}
        - **Target 2:** {bear.get('target_2', 'N/A')}
        - **Target 3:** {bear.get('target_3', 'N/A')}
        - **Invalidation:** {bear.get('invalidation', 'N/A')}
        """)

    st.warning("⚠ These are scenarios, not guaranteed predictions. Always use stop losses.")


def _render_swing(swing_data):
    """Render swing analysis."""
    st.markdown('<div class="section-header"><h2>📉 Swing / Short-Term Trading Analysis</h2></div>', unsafe_allow_html=True)

    if not swing_data or "error" in swing_data:
        st.warning(swing_data.get("error", "Swing analysis unavailable"))
        return

    # Summary
    cols = st.columns(4)
    with cols[0]:
        trend = swing_data.get("trend", "N/A")
        color = "#22c55e" if "Bullish" in trend else ("#ef4444" if "Bearish" in trend else "#eab308")
        st.markdown(f"**Trend:** <span style='color:{color};'>{trend}</span>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"**Momentum:** {swing_data.get('momentum', 'N/A')}")
    with cols[2]:
        st.markdown(f"**RSI:** {swing_data.get('rsi', 'N/A')}")
    with cols[3]:
        st.markdown(f"**Confidence:** {swing_data.get('confidence', 'N/A')}%")

    st.info(swing_data.get("trend_detail", ""))

    # Key levels
    st.markdown("### 🎯 Key Levels")
    cols = st.columns(6)
    items = [
        ("Support", swing_data.get("support"), "#22c55e"),
        ("Resistance", swing_data.get("resistance"), "#ef4444"),
        ("Stop Loss", swing_data.get("stop_loss"), "#ef4444"),
        ("Target 1", swing_data.get("target_1"), "#22c55e"),
        ("Target 2", swing_data.get("target_2"), "#22c55e"),
        ("R:R Ratio", f"1:{swing_data.get('risk_reward', 'N/A')}", "#3b82f6"),
    ]
    for i, (label, val, color) in enumerate(items):
        with cols[i]:
            st.markdown(f"**{label}**<br><span style='color:{color}; font-size:1.2em;'>{val}</span>", unsafe_allow_html=True)

    # EMAs
    st.markdown("### 📈 Key EMAs")
    cols = st.columns(3)
    for i, (label, key) in enumerate([("EMA 9", "ema_9"), ("EMA 20", "ema_20"), ("EMA 50", "ema_50")]):
        with cols[i]:
            val = swing_data.get(key)
            if val:
                st.metric(label, f"{val:.2f}")

    # Confirmations
    confirms = swing_data.get("confirmations", [])
    if confirms:
        st.markdown("### ✅ Confirmations")
        for c in confirms:
            st.markdown(c)


def _render_long_term(longterm_data, quote):
    """Render long-term investment analysis."""
    st.markdown('<div class="section-header"><h2>🏦 Long-Term Investment Analysis</h2></div>', unsafe_allow_html=True)

    if not longterm_data or "error" in longterm_data:
        st.warning("Long-term analysis unavailable")
        return

    # Investment Thesis
    thesis = longterm_data.get("investment_thesis", {})
    st.markdown("### 📋 Investment Thesis")
    t = thesis.get("thesis", "N/A")
    color = "#22c55e" if "ATTRACTIVE" in t else ("#ef4444" if "AVOID" in t else "#eab308")
    st.markdown(f"**Thesis:** <span style='color:{color}; font-size:1.5em;'>{t}</span>", unsafe_allow_html=True)
    st.info(thesis.get("detail", ""))

    # Quality Score
    quality = longterm_data.get("quality_score", {})
    st.markdown("### ⭐ Fundamental Quality Score")
    st.markdown(f"**Overall: {quality.get('overall', 'N/A')}/10**")

    categories = [
        ("Business Quality", quality.get("business_quality", 0)),
        ("Growth", quality.get("growth", 0)),
        ("Profitability", quality.get("profitability", 0)),
        ("Balance Sheet", quality.get("balance_sheet", 0)),
        ("Valuation", quality.get("valuation", 0)),
        ("Management/Shareholding", quality.get("management_shareholding", 0)),
    ]

    for name, score in categories:
        pct = score * 10
        color = "#22c55e" if score >= 7 else ("#eab308" if score >= 5 else "#ef4444")
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; margin:6px 0;">
            <span style="width:200px; color:#94a3b8;">{name}</span>
            <div style="flex:1; background:#334155; height:8px; border-radius:4px;">
                <div style="width:{pct}%; background:{color}; height:100%; border-radius:4px;"></div>
            </div>
            <span style="color:{color}; font-weight:bold; width:50px;">{score}/10</span>
        </div>
        """, unsafe_allow_html=True)

    # Score explanation
    if quality.get("explanation"):
        with st.expander("📐 Score Calculation Detail"):
            st.code(quality["explanation"])

    # Strengths & Weaknesses
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ✅ Strengths")
        for s in thesis.get("strengths", []):
            st.markdown(f"- {s}")
    with col2:
        st.markdown("### ⚠ Weaknesses")
        for w in thesis.get("weaknesses", []):
            st.markdown(f"- {w}")

    # Valuation
    valuation = longterm_data.get("valuation", {})
    st.markdown("### 💰 Valuation")
    st.markdown(f"**Assessment:** {valuation.get('assessment', 'N/A')}")
    for reason in valuation.get("reasons", []):
        st.markdown(f"- {reason}")

    # Key Ratios
    st.markdown("### 📊 Key Ratios")
    cols = st.columns(6)
    ratio_items = [
        ("P/E", valuation.get("pe_ratio")),
        ("P/B", valuation.get("price_to_book")),
        ("PEG", valuation.get("peg_ratio")),
        ("EV/EBITDA", valuation.get("ev_to_ebitda")),
        ("EV/Revenue", valuation.get("ev_to_revenue")),
        ("Mkt Cap", valuation.get("market_cap_formatted")),
    ]
    for i, (label, val) in enumerate(ratio_items):
        with cols[i]:
            display = f"{val:.2f}" if val and isinstance(val, (int, float)) else (val if val else "N/A")
            st.metric(label, display)

    # Fundamentals
    fund = longterm_data.get("fundamentals", {})
    st.markdown("### 📈 Fundamental Metrics")
    cols = st.columns(4)
    fund_items = [
        ("Revenue", fund.get("revenue")),
        ("Revenue Growth", fund.get("revenue_growth")),
        ("Profit Margin", fund.get("profit_margins")),
        ("Operating Margin", fund.get("operating_margins")),
        ("ROE", fund.get("roe")),
        ("ROA", fund.get("roa")),
        ("Debt/Equity", fund.get("debt_to_equity")),
        ("Free Cash Flow", fund.get("free_cashflow")),
        ("Dividend Yield", fund.get("dividend_yield")),
        ("Current Ratio", fund.get("current_ratio")),
    ]
    for i, (label, val) in enumerate(fund_items):
        with cols[i % 4]:
            st.markdown(f"**{label}**<br>{val}", unsafe_allow_html=True)


def _render_news(news):
    """Render news and sentiment."""
    st.markdown('<div class="section-header"><h2>📰 News & Sentiment Analysis</h2></div>', unsafe_allow_html=True)

    if not news:
        st.info("No recent news available for this stock.")
        return

    # Sentiment summary
    pos = sum(1 for n in news if n.get("sentiment_hint") == "Positive")
    neg = sum(1 for n in news if n.get("sentiment_hint") == "Negative")
    neu = sum(1 for n in news if n.get("sentiment_hint") == "Neutral")

    cols = st.columns(3)
    with cols[0]:
        st.metric("Positive", pos, delta=None)
    with cols[1]:
        st.metric("Negative", neg, delta=None)
    with cols[2]:
        st.metric("Neutral", neu, delta=None)

    # Category breakdown
    categories = {}
    for n in news:
        cat = n.get("category", "General")
        categories[cat] = categories.get(cat, 0) + 1

    if categories:
        st.markdown("### 📂 Categories")
        cols = st.columns(min(len(categories), 5))
        for i, (cat, count) in enumerate(sorted(categories.items(), key=lambda x: -x[1])[:5]):
            with cols[i % 5]:
                st.metric(cat, count)

    st.markdown("---")

    # News items
    for n in news[:15]:
        sentiment = n.get("sentiment_hint", "Neutral")
        color = "#22c55e" if sentiment == "Positive" else ("#ef4444" if sentiment == "Negative" else "#94a3b8")
        icon = "🟢" if sentiment == "Positive" else ("🔴" if sentiment == "Negative" else "⚪")

        st.markdown(f"""
        <div style="background:#1e293b; padding:12px 16px; border-radius:6px; margin:6px 0; border-left:3px solid {color};">
            <div style="display:flex; justify-content:space-between;">
                <strong>{icon} {n.get('title', 'N/A')}</strong>
                <span style="color:#64748b; font-size:0.8em;">{n.get('date', '')}</span>
            </div>
            <div style="color:#94a3b8; font-size:0.85em; margin-top:4px;">
                {n.get('source', 'N/A')} | Category: {n.get('category', 'N/A')} | Sentiment: <span style="color:{color};">{sentiment}</span>
            </div>
            {f'<p style="color:#cbd5e1; margin:6px 0 0 0; font-size:0.9em;">{n["summary"][:200]}...</p>' if n.get("summary") else ""}
        </div>
        """, unsafe_allow_html=True)


def _render_risk(risk_data):
    """Render risk analysis."""
    st.markdown('<div class="section-header"><h2>⚖️ Risk Analysis</h2></div>', unsafe_allow_html=True)

    if not risk_data:
        st.warning("Risk analysis unavailable")
        return

    # Overall risk
    rating = risk_data.get("overall_rating", "MODERATE")
    score = risk_data.get("overall_score", 5)
    color = {"LOW": "#22c55e", "MODERATE": "#eab308", "HIGH": "#f59e0b", "VERY HIGH": "#ef4444"}.get(rating, "#eab308")

    st.markdown(f"""
    <div style="background:#1e293b; padding:20px; border-radius:10px; border-left:5px solid {color};">
        <strong style="color:{color}; font-size:1.5em;">Overall Risk: {rating}</strong>
        <br><span style="color:#94a3b8;">Score: {score}/10</span>
        <br><span style="color:#cbd5e1;">{risk_data.get('explanation', '')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Individual risks
    risks = risk_data.get("individual_risks", {})
    st.markdown("### 📋 Individual Risk Factors")

    for name, risk in risks.items():
        level = risk.get("level", "MODERATE")
        score = risk.get("score", 5)
        icon = {"VERY HIGH": "🔴", "HIGH": "🟠", "MODERATE": "🟡", "LOW": "🟢"}.get(level, "⚪")
        color = {"VERY HIGH": "#ef4444", "HIGH": "#f59e0b", "MODERATE": "#eab308", "LOW": "#22c55e"}.get(level, "#94a3b8")

        with st.expander(f"{icon} {name.replace('_', ' ').title()} — {level} ({score}/10)"):
            for detail in risk.get("details", []):
                st.markdown(f"- {detail}")

    # Risk rating bar
    st.markdown("### 📊 Risk Rating Scale")
    st.markdown("""
    ```
    🟢 LOW (1-3)    🟡 MODERATE (4-5)    🟠 HIGH (6-7)    🔴 VERY HIGH (8-10)
    |████████|████████|████████|████████|████████|████████|████████|████████|
    0        1.25     2.5      3.75     5.0      6.25     7.5      8.75     10
    ```
    """)


def _render_trade_setups(intraday_data, swing_data, tech_score, sr_data):
    """Render trade setups."""
    st.markdown('<div class="section-header"><h2>🎯 Trade Setups</h2></div>', unsafe_allow_html=True)

    score = tech_score.get("score", 50)
    signal = tech_score.get("signal", "Neutral")

    st.markdown(f"**Current Technical Signal:** {signal} ({score:.0f}/100)")
    st.warning("⚠ Trade setups are scenarios, not guaranteed outcomes. Always use stop losses and proper position sizing.")

    # Intraday setup
    st.markdown("### ⏱ Intraday Setup")
    if intraday_data and "scenarios" in intraday_data:
        scenarios = intraday_data["scenarios"]
        bull = scenarios.get("bullish", {})
        bear = scenarios.get("bearish", {})

        cols = st.columns(2)
        with cols[0]:
            st.markdown("**🟢 Bullish Setup**")
            for key in ["entry_zone", "stop_loss", "target_1", "target_2", "target_3", "invalidation"]:
                label = key.replace("_", " ").title()
                st.markdown(f"- {label}: {bull.get(key, 'N/A')}")
        with cols[1]:
            st.markdown("**🔴 Bearish Setup**")
            for key in ["entry_zone", "stop_loss", "target_1", "target_2", "target_3", "invalidation"]:
                label = key.replace("_", " ").title()
                st.markdown(f"- {label}: {bear.get(key, 'N/A')}")

    # Swing setup
    st.markdown("### 📅 Swing Setup")
    if swing_data and "error" not in swing_data:
        cols = st.columns(6)
        items = [
            ("Support", swing_data.get("support"), "#22c55e"),
            ("Resistance", swing_data.get("resistance"), "#ef4444"),
            ("Stop Loss", swing_data.get("stop_loss"), "#ef4444"),
            ("Target 1", swing_data.get("target_1"), "#22c55e"),
            ("Target 2", swing_data.get("target_2"), "#22c55e"),
            ("R:R", f"1:{swing_data.get('risk_reward', 'N/A')}", "#3b82f6"),
        ]
        for i, (label, val, color) in enumerate(items):
            with cols[i]:
                st.markdown(f"**{label}**<br><span style='color:{color}; font-size:1.1em;'>{val}</span>", unsafe_allow_html=True)

        # Confirmation requirements
        confirms = swing_data.get("confirmations", [])
        st.markdown("**Confirmation Requirements:**")
        for c in confirms:
            st.markdown(f"  {c}")


def _render_scenarios(ai_analysis):
    """Render bull/base/bear scenarios."""
    st.markdown('<div class="section-header"><h2>📊 Scenario Analysis</h2></div>', unsafe_allow_html=True)

    scenarios = ai_analysis.get("scenarios", {})

    for case_name, case_data in [("🟢 Bull Case", scenarios.get("bull", {})),
                                   ("🟡 Base Case", scenarios.get("base", {})),
                                   ("🔴 Bear Case", scenarios.get("bear", {}))]:
        st.markdown(f"### {case_name}")
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"**Trigger:** {case_data.get('trigger', 'N/A')}")
            st.markdown(f"**Expected Zone:** {case_data.get('expected_zone', 'N/A')}")
        with cols[1]:
            st.markdown(f"**Confirmation:** {case_data.get('confirmation', 'N/A')}")
            st.markdown(f"**Invalidation:** {case_data.get('invalidation', 'N/A')}")
        st.caption(f"Probability methodology: {case_data.get('probability', 'N/A')}")

    st.warning("⚠ These are scenarios, not predictions. Markets are inherently uncertain.")

    # Invalidation thesis
    st.markdown("### ⚠ What Would Invalidate the Thesis?")
    st.info(ai_analysis.get("invalidation", "Monitor key levels for changes."))

    # What to watch
    st.markdown("### 👀 What Should I Watch Next?")
    st.warning(ai_analysis.get("watch_next", "Monitor key levels."))


def _render_calculator(investment, risk_tolerance, max_risk_pct, current_price, swing_data, sr_data, currency):
    """Render position size calculator."""
    st.markdown('<div class="section-header"><h2>🧮 Investment Calculator</h2></div>', unsafe_allow_html=True)

    st.info(f"Investment: {currency}{investment:,} | Risk per trade: {max_risk_pct}% | Tolerance: {risk_tolerance}")

    if investment <= 0:
        st.warning("Enter an investment amount in the sidebar to use the calculator.")
        return

    if current_price <= 0:
        st.warning("Current price not available.")
        return

    # User inputs
    cols = st.columns(3)
    with cols[0]:
        entry_price = st.number_input("Entry Price", value=float(current_price), step=0.01)
    with cols[1]:
        stop_loss_price = st.number_input(
            "Stop Loss Price",
            value=float(swing_data.get("stop_loss", current_price * 0.97)) if swing_data and "error" not in swing_data else float(current_price * 0.97),
            step=0.01,
        )
    with cols[2]:
        target_price = st.number_input(
            "Target Price",
            value=float(swing_data.get("target_2", current_price * 1.06)) if swing_data and "error" not in swing_data else float(current_price * 1.06),
            step=0.01,
        )

    # Calculate
    max_loss_amount = investment * (max_risk_pct / 100)
    risk_per_share = abs(entry_price - stop_loss_price)
    reward_per_share = abs(target_price - entry_price)

    if risk_per_share > 0:
        position_size = max_loss_amount / risk_per_share
        num_shares = int(position_size)
        actual_investment = num_shares * entry_price
        potential_loss = num_shares * risk_per_share
        potential_profit = num_shares * reward_per_share
        rr_ratio = reward_per_share / risk_per_share
        pct_of_portfolio = (actual_investment / investment * 100) if investment > 0 else 0
    else:
        num_shares = 0
        actual_investment = 0
        potential_loss = 0
        potential_profit = 0
        rr_ratio = 0
        pct_of_portfolio = 0

    # Display results
    st.markdown("### 📋 Position Sizing Results")
    cols = st.columns(5)
    with cols[0]:
        st.metric("Number of Shares", f"{num_shares}")
    with cols[1]:
        st.metric("Position Value", f"{currency}{actual_investment:,.2f}")
    with cols[2]:
        st.metric("Max Loss", f"{currency}{potential_loss:,.2f}", f"{max_risk_pct}% of capital")
    with cols[3]:
        st.metric("Potential Profit", f"{currency}{potential_profit:,.2f}")
    with cols[4]:
        st.metric("Risk/Reward", f"1:{rr_ratio:.2f}")

    st.markdown(f"**Portfolio Allocation:** {pct_of_portfolio:.1f}% of total capital")

    # Visual risk/reward
    st.markdown("### 📊 Risk/Reward Visualization")
    if rr_ratio > 0:
        max_visual = max(potential_profit, potential_loss, 1)
        profit_width = potential_profit / max_visual * 100
        loss_width = potential_loss / max_visual * 100

        st.markdown(f"""
        <div style="margin:10px 0;">
            <div style="display:flex; align-items:center; gap:10px; margin:4px 0;">
                <span style="width:100px; color:#22c55e;">Profit</span>
                <div style="background:#1e293b; flex:1; height:20px; border-radius:4px; position:relative;">
                    <div style="width:{profit_width}%; background:#22c55e; height:100%; border-radius:4px; display:flex; align-items:center; justify-content:center;">
                        <span style="font-size:0.8em;">{currency}{potential_profit:,.0f}</span>
                    </div>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:10px; margin:4px 0;">
                <span style="width:100px; color:#ef4444;">Loss</span>
                <div style="background:#1e293b; flex:1; height:20px; border-radius:4px; position:relative;">
                    <div style="width:{loss_width}%; background:#ef4444; height:100%; border-radius:4px; display:flex; align-items:center; justify-content:center;">
                        <span style="font-size:0.8em;">{currency}{potential_loss:,.0f}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Kelly Criterion
    if rr_ratio > 0:
        win_rate = 0.5  # Assume 50% for illustration
        kelly = (win_rate * rr_ratio - (1 - win_rate)) / rr_ratio
        st.markdown(f"**Kelly Criterion (assumed 50% win rate):** {kelly*100:.1f}% of bankroll")
        st.caption("Note: Use fractional Kelly (typically 25-50%) for safety.")


def _isnan(val) -> bool:
    try:
        if val is None:
            return True
        if isinstance(val, float) and (pd.isna(val) or np.isinf(val)):
            return True
        return False
    except:
        return True


# ── Run ──────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
