"""
Multi-Timeframe Analysis.
Analyzes 5m, 15m, 1h, daily, weekly, monthly independently then combines.
Higher timeframes take priority over lower timeframes.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def multi_timeframe_analysis(
    daily_df: pd.DataFrame,
    weekly_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    hourly_df: Optional[pd.DataFrame] = None,
    df_15m: Optional[pd.DataFrame] = None,
    df_5m: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """Perform multi-timeframe analysis and combine signals."""
    results = {}
    signals = []

    # Analyze each timeframe
    for tf_name, tf_df in [
        ("5m", df_5m),
        ("15m", df_15m),
        ("1H", hourly_df),
        ("Daily", daily_df),
        ("Weekly", weekly_df),
        ("Monthly", monthly_df),
    ]:
        if tf_df is not None and not tf_df.empty and len(tf_df) > 10:
            signal = _analyze_timeframe(tf_df, tf_name)
            results[tf_name] = signal
            signals.append({"timeframe": tf_name, **signal})
        else:
            results[tf_name] = {"trend": "Data unavailable", "bias": "Neutral"}

    # Combine signals with higher timeframe weighting
    overall = _combine_signals(signals)

    return {
        "timeframes": results,
        "overall": overall,
    }


def _analyze_timeframe(df: pd.DataFrame, tf_name: str) -> Dict[str, Any]:
    """Analyze a single timeframe and return trend/bias."""
    if df is None or df.empty or len(df) < 20:
        return {"trend": "Insufficient data", "bias": "Neutral", "confidence": 0}

    close = df["close"]
    current_price = close.iloc[-1]

    # EMA alignment
    ema_20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
    ema_50 = close.ewm(span=50, adjust=False).mean().iloc[-1] if len(df) >= 50 else ema_20

    # SMA 200 if enough data
    sma_200 = close.rolling(window=min(200, len(df)), min_periods=1).mean().iloc[-1]

    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).ewm(alpha=1 / 14, min_periods=14).mean()
    loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1 / 14, min_periods=14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = (100 - (100 / (1 + rs))).iloc[-1]

    # MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_val = macd_line.iloc[-1]
    signal_val = signal_line.iloc[-1]

    # ADX (simplified)
    if "adx" in df.columns:
        adx = df["adx"].iloc[-1]
    else:
        adx = 25  # default assumption

    # Score
    score = 0  # -100 to +100

    # EMA alignment
    if current_price > ema_20 > ema_50:
        score += 25
    elif current_price < ema_20 < ema_50:
        score -= 25

    # Price vs SMA 200
    if current_price > sma_200:
        score += 15
    else:
        score -= 15

    # RSI
    if rsi > 70:
        score -= 10  # Overbought
    elif rsi < 30:
        score += 10  # Oversold
    elif 50 < rsi < 70:
        score += 5
    elif 30 < rsi < 50:
        score -= 5

    # MACD
    if macd_val > signal_val:
        score += 10
    else:
        score -= 10

    # Determine bias
    if score >= 20:
        bias = "Bullish"
        confidence = min(90, 50 + score)
    elif score <= -20:
        bias = "Bearish"
        confidence = min(90, 50 + abs(score))
    else:
        bias = "Neutral"
        confidence = 50 - abs(score)

    # Trend description
    trend_parts = []
    if current_price > ema_20:
        trend_parts.append("above EMA20")
    else:
        trend_parts.append("below EMA20")

    if current_price > sma_200:
        trend_parts.append("above SMA200")
    else:
        trend_parts.append("below SMA200")

    trend = f"Price {' and '.join(trend_parts)}, RSI {rsi:.1f}"

    return {
        "trend": trend,
        "bias": bias,
        "confidence": confidence,
        "ema_20": round(ema_20, 2),
        "ema_50": round(ema_50, 2),
        "sma_200": round(sma_200, 2),
        "rsi": round(rsi, 1),
        "macd": round(macd_val, 2),
        "macd_signal": round(signal_val, 2),
        "score": score,
    }


def _combine_signals(signals: list) -> Dict[str, Any]:
    """Combine signals from multiple timeframes. Higher TFs have more weight."""
    if not signals:
        return {"trend": "No data", "bias": "Neutral", "confidence": 0, "detail": ""}

    # Weight mapping: higher timeframes get more weight
    weights = {
        "5m": 0.05,
        "15m": 0.1,
        "1H": 0.15,
        "Daily": 0.3,
        "Weekly": 0.25,
        "Monthly": 0.15,
    }

    total_score = 0
    total_weight = 0
    breakdown = []

    for s in signals:
        tf = s.get("timeframe", "Daily")
        w = weights.get(tf, 0.1)
        score = s.get("score", 0)
        total_score += score * w
        total_weight += w
        breakdown.append(f"{tf}: {s.get('bias', 'Neutral')} (score: {score})")

    if total_weight > 0:
        avg_score = total_score / total_weight
    else:
        avg_score = 0

    # Overall bias
    if avg_score >= 15:
        overall_bias = "Bullish"
    elif avg_score <= -15:
        overall_bias = "Bearish"
    else:
        overall_bias = "Neutral"

    # Check alignment
    bullish_count = sum(1 for s in signals if s.get("bias") == "Bullish")
    bearish_count = sum(1 for s in signals if s.get("bias") == "Bearish")
    total_count = len(signals)
    alignment = max(bullish_count, bearish_count) / total_count if total_count > 0 else 0

    # Higher timeframe dominance
    htf_signals = [s for s in signals if s.get("timeframe") in ("Daily", "Weekly", "Monthly")]
    htf_bullish = sum(1 for s in htf_signals if s.get("bias") == "Bullish")
    htf_bearish = sum(1 for s in htf_signals if s.get("bias") == "Bearish")

    # Override lower TFs with HTF direction
    if htf_bullish > htf_bearish and overall_bias == "Bearish":
        overall_bias = "Neutral"  # HTF bullish, so don't go fully bearish
        override_note = "Lower timeframes bearish but higher timeframe trend is bullish"
    elif htf_bearish > htf_bullish and overall_bias == "Bullish":
        overall_bias = "Neutral"
        override_note = "Lower timeframes bullish but higher timeframe trend is bearish"
    else:
        override_note = None

    confidence = min(95, 40 + (alignment * 40) + (abs(avg_score) * 0.5))

    detail = " → ".join(breakdown)
    if override_note:
        detail += f"\n⚠ {override_note}"

    return {
        "trend": overall_bias,
        "bias": overall_bias,
        "confidence": round(confidence),
        "avg_score": round(avg_score, 1),
        "alignment": round(alignment * 100, 1),
        "breakdown": breakdown,
        "detail": detail,
        "override_note": override_note,
    }
