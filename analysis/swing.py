"""
Swing / Short-Term Analysis (1-5 days to 1-4 weeks).
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def swing_analysis(
    daily_df: pd.DataFrame,
    current_quote: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Short-term swing trading analysis."""
    if daily_df is None or daily_df.empty or len(daily_df) < 20:
        return {"error": "Insufficient data for swing analysis"}

    close = daily_df["close"]
    current_price = current_quote.get("current_price", close.iloc[-1]) if current_quote else close.iloc[-1]

    # Trend
    ema_9 = close.ewm(span=9, adjust=False).mean()
    ema_20 = close.ewm(span=20, adjust=False).mean()
    ema_50 = close.ewm(span=50, adjust=False).mean()

    # RSI
    rsi = _rsi(close, 14)
    current_rsi = rsi.iloc[-1]

    # MACD
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    macd_crossover = macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]
    macd_crossunder = macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]

    # Support / Resistance
    recent = daily_df.tail(40)
    support = recent["low"].min()
    resistance = recent["high"].max()

    # Recent swing points
    swing_highs, swing_lows = _find_recent_swings(daily_df, window=5)

    # Breakout level
    breakout_level = max(swing_highs) if swing_highs else resistance
    breakdown_level = min(swing_lows) if swing_lows else support

    # Risk/Reward
    distance_to_resistance = (breakout_level - current_price) / current_price * 100
    distance_to_support = (current_price - breakdown_level) / current_price * 100

    # Determine trend
    if current_price > ema_20.iloc[-1] > ema_50.iloc[-1]:
        trend = "Bullish"
        trend_detail = "Price above EMA20 and EMA50, short-term uptrend intact"
    elif current_price < ema_20.iloc[-1] < ema_50.iloc[-1]:
        trend = "Bearish"
        trend_detail = "Price below EMA20 and EMA50, short-term downtrend"
    else:
        trend = "Neutral"
        trend_detail = "Price between EMA20 and EMA50, no clear short-term direction"

    # Momentum assessment
    if current_rsi > 70:
        momentum = "Overbought"
    elif current_rsi < 30:
        momentum = "Oversold"
    elif macd_crossover:
        momentum = "Bullish Crossover"
    elif macd_crossunder:
        momentum = "Bearish Crossover"
    elif hist.iloc[-1] > 0:
        momentum = "Positive"
    else:
        momentum = "Negative"

    # Stop loss
    stop_loss = breakdown_level * 0.99

    # Targets
    range_size = breakout_level - breakdown_level
    target_1 = breakout_level + range_size * 0.3
    target_2 = breakout_level + range_size * 0.6
    target_3 = breakout_level + range_size * 1.0

    # Risk/Reward ratio
    risk = current_price - stop_loss
    reward = target_2 - current_price
    rr_ratio = reward / risk if risk > 0 else 0

    # Confidence
    confidence = _calculate_swing_confidence(trend, current_rsi, macd, signal, close)

    return {
        "trend": trend,
        "trend_detail": trend_detail,
        "momentum": momentum,
        "rsi": round(current_rsi, 1) if not pd.isna(current_rsi) else None,
        "macd_crossover": macd_crossover,
        "macd_crossunder": macd_crossunder,
        "support": round(breakdown_level, 2),
        "resistance": round(breakout_level, 2),
        "stop_loss": round(stop_loss, 2),
        "target_1": round(target_1, 2),
        "target_2": round(target_2, 2),
        "target_3": round(target_3, 2),
        "risk_reward": round(rr_ratio, 2),
        "confidence": confidence,
        "ema_9": round(ema_9.iloc[-1], 2),
        "ema_20": round(ema_20.iloc[-1], 2),
        "ema_50": round(ema_50.iloc[-1], 2) if len(close) >= 50 else None,
        "confirmations": _swing_confirmations(trend, momentum, current_rsi, macd, signal),
    }


def _rsi(close, period):
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).ewm(alpha=1/period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/period, min_periods=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _find_recent_swings(df, window=5):
    highs, lows = [], []
    h, l = df["high"].values, df["low"].values
    for i in range(window, len(df) - window):
        if h[i] == max(h[i-window:i+window+1]):
            highs.append(h[i])
        if l[i] == min(l[i-window:i+window+1]):
            lows.append(l[i])
    return highs[-3:], lows[-3:]


def _calculate_swing_confidence(trend, rsi, macd, signal, close):
    score = 0
    if trend == "Bullish":
        score += 30
        if close.iloc[-1] > close.iloc[-5]:
            score += 10
    elif trend == "Bearish":
        score += 30
        if close.iloc[-1] < close.iloc[-5]:
            score += 10

    if not pd.isna(rsi):
        if 40 <= rsi <= 60:
            score += 10
        elif 30 <= rsi <= 70:
            score += 5

    if macd.iloc[-1] > signal.iloc[-1]:
        score += 15
    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
        score += 10

    return min(85, 30 + score)


def _swing_confirmations(trend, momentum, rsi, macd, signal):
    confirms = []
    if trend == "Bullish":
        confirms.append("✅ Price above key EMAs")
        if momentum in ("Positive", "Bullish Crossover"):
            confirms.append("✅ MACD positive")
        if rsi and 40 < rsi < 70:
            confirms.append(f"✅ RSI in healthy range ({rsi:.0f})")
    elif trend == "Bearish":
        confirms.append("🔴 Price below key EMAs")
        if momentum in ("Negative", "Bearish Crossover"):
            confirms.append("🔴 MACD negative")

    if not confirms:
        confirms.append("⚠ No strong confirming signals")
    return confirms
