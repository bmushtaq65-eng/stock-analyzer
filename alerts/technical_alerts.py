"""
Technical Alert System.
Checks for RSI, MACD, SMA/EMA crossovers, VWAP, volume spikes, etc.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List


def check_technical_alerts(df: pd.DataFrame, quote: Dict = None) -> List[Dict]:
    """Check all technical conditions and generate alerts."""
    alerts = []

    if df is None or df.empty or len(df) < 5:
        return alerts

    close = df["close"]
    current_price = quote.get("current_price", close.iloc[-1]) if quote else close.iloc[-1]

    # 1. RSI Alerts
    if "rsi" in df.columns:
        rsi = df["rsi"].iloc[-1]
        if not _isnan(rsi):
            if rsi > 70:
                alerts.append({
                    "type": "RSI Overbought",
                    "severity": "Warning",
                    "message": f"RSI is at {rsi:.1f} — overbought territory",
                    "value": round(rsi, 1),
                })
            elif rsi < 30:
                alerts.append({
                    "type": "RSI Oversold",
                    "severity": "Opportunity",
                    "message": f"RSI is at {rsi:.1f} — oversold territory",
                    "value": round(rsi, 1),
                })

    # 2. MACD Crossover
    if "macd" in df.columns and "macd_signal" in df.columns and len(df) > 1:
        macd_now = df["macd"].iloc[-1]
        sig_now = df["macd_signal"].iloc[-1]
        macd_prev = df["macd"].iloc[-2]
        sig_prev = df["macd_signal"].iloc[-2]

        if not any(_isnan(v) for v in [macd_now, sig_now, macd_prev, sig_prev]):
            if macd_now > sig_now and macd_prev <= sig_prev:
                alerts.append({
                    "type": "MACD Bullish Crossover",
                    "severity": "Signal",
                    "message": "MACD has crossed above the signal line — bullish momentum",
                    "value": round(macd_now, 2),
                })
            elif macd_now < sig_now and macd_prev >= sig_prev:
                alerts.append({
                    "type": "MACD Bearish Crossover",
                    "severity": "Signal",
                    "message": "MACD has crossed below the signal line — bearish momentum",
                    "value": round(macd_now, 2),
                })

    # 3. SMA/EMA Crossover (Golden/Death Cross)
    for short, long in [(20, 50), (50, 200)]:
        short_col = f"ema_{short}"
        long_col = f"ema_{long}"
        if short_col in df.columns and long_col in df.columns and len(df) > 1:
            s_now = df[short_col].iloc[-1]
            l_now = df[long_col].iloc[-1]
            s_prev = df[short_col].iloc[-2]
            l_prev = df[long_col].iloc[-2]

            if not any(_isnan(v) for v in [s_now, l_now, s_prev, l_prev]):
                if s_now > l_now and s_prev <= l_prev:
                    alerts.append({
                        "type": f"EMA{short}/EMA{long} Bullish Crossover",
                        "severity": "Strong Signal",
                        "message": f"EMA{short} crossed above EMA{long} — bullish trend confirmation",
                        "value": round(s_now, 2),
                    })
                elif s_now < l_now and s_prev >= l_prev:
                    alerts.append({
                        "type": f"EMA{short}/EMA{long} Bearish Crossover",
                        "severity": "Strong Signal",
                        "message": f"EMA{short} crossed below EMA{long} — bearish trend confirmation",
                        "value": round(s_now, 2),
                    })

    # 4. VWAP Crossover
    if "vwap" in df.columns and len(df) > 1:
        vwap_now = df["vwap"].iloc[-1]
        vwap_prev = df["vwap"].iloc[-2]
        if not _isnan(vwap_now) and not _isnan(vwap_prev):
            if current_price > vwap_now and close.iloc[-2] <= vwap_prev:
                alerts.append({
                    "type": "VWAP Bullish Crossover",
                    "severity": "Signal",
                    "message": f"Price crossed above VWAP ({vwap_now:.2f}) — intraday bullish",
                    "value": round(vwap_now, 2),
                })
            elif current_price < vwap_now and close.iloc[-2] >= vwap_prev:
                alerts.append({
                    "type": "VWAP Bearish Crossover",
                    "severity": "Signal",
                    "message": f"Price crossed below VWAP ({vwap_now:.2f}) — intraday bearish",
                    "value": round(vwap_now, 2),
                })

    # 5. Volume Spike
    if "relative_volume" in df.columns:
        rv = df["relative_volume"].iloc[-1]
        if not _isnan(rv) and rv > 2.0:
            alerts.append({
                "type": "Volume Spike",
                "severity": "Notable",
                "message": f"Volume is {rv:.1f}x the 20-day average — unusual activity",
                "value": round(rv, 1),
            })

    # 6. Supertrend Crossover
    if "supertrend_direction" in df.columns and len(df) > 1:
        st_now = df["supertrend_direction"].iloc[-1]
        st_prev = df["supertrend_direction"].iloc[-2]
        if not _isnan(st_now) and not _isnan(st_prev):
            if st_now == 1 and st_prev == -1:
                alerts.append({
                    "type": "Supertrend Buy Signal",
                    "severity": "Signal",
                    "message": "Supertrend flipped to bullish",
                    "value": 1,
                })
            elif st_now == -1 and st_prev == 1:
                alerts.append({
                    "type": "Supertrend Sell Signal",
                    "severity": "Signal",
                    "message": "Supertrend flipped to bearish",
                    "value": -1,
                })

    # 7. New 52-week high/low
    if len(df) >= 252:
        high_52w = df["high"].tail(252).max()
        low_52w = df["low"].tail(252).min()
        if current_price >= high_52w * 0.99:
            alerts.append({
                "type": "Near 52-Week High",
                "severity": "Notable",
                "message": f"Price ({current_price:.2f}) is near 52-week high ({high_52w:.2f})",
                "value": round(high_52w, 2),
            })
        if current_price <= low_52w * 1.01:
            alerts.append({
                "type": "Near 52-Week Low",
                "severity": "Warning",
                "message": f"Price ({current_price:.2f}) is near 52-week low ({low_52w:.2f})",
                "value": round(low_52w, 2),
            })

    return alerts


def _isnan(val) -> bool:
    try:
        if val is None:
            return True
        return isinstance(val, float) and (np.isnan(val) or np.isinf(val))
    except:
        return True
