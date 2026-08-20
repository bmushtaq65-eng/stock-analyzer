"""
Technical Scoring Engine.
Generates objective technical scores based on indicator evidence.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def technical_score(df: pd.DataFrame, indicators_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Calculate a technical score from 0-100 based on multiple indicator signals.
    Transparent and rule-based.
    """
    if df is None or df.empty or len(df) < 20:
        return {"score": 50, "signals": {}, "explanation": "Insufficient data"}

    close = df["close"]
    current_price = close.iloc[-1]

    signals = {}
    total_weight = 0
    weighted_score = 0

    # 1. Trend Score (weight: 25%)
    trend_score = _trend_score(df)
    signals["trend"] = trend_score
    weighted_score += trend_score["score"] * 0.25
    total_weight += 0.25

    # 2. Momentum Score (weight: 25%)
    momentum_score = _momentum_score(df)
    signals["momentum"] = momentum_score
    weighted_score += momentum_score["score"] * 0.25
    total_weight += 0.25

    # 3. Volatility Score (weight: 15%)
    volatility_score = _volatility_score(df)
    signals["volatility"] = volatility_score
    weighted_score += volatility_score["score"] * 0.15
    total_weight += 0.15

    # 4. Volume Score (weight: 15%)
    volume_score = _volume_score(df)
    signals["volume"] = volume_score
    weighted_score += volume_score["score"] * 0.15
    total_weight += 0.15

    # 5. Price Action Score (weight: 20%)
    price_action_score = _price_action_score(df)
    signals["price_action"] = price_action_score
    weighted_score += price_action_score["score"] * 0.20
    total_weight += 0.20

    overall = weighted_score / total_weight if total_weight > 0 else 50

    # Determine signal
    if overall >= 65:
        signal = "Bullish"
    elif overall <= 35:
        signal = "Bearish"
    else:
        signal = "Neutral"

    return {
        "score": round(overall, 1),
        "signal": signal,
        "signals": signals,
        "explanation": _explain_score(signals, overall),
    }


def _trend_score(df: pd.DataFrame) -> Dict:
    """Score trend indicators."""
    score = 50
    reasons = []
    close = df["close"]
    current = close.iloc[-1]

    # EMA alignment
    for period in [9, 20, 50, 200]:
        if len(close) >= period:
            ema = close.ewm(span=period, adjust=False).mean().iloc[-1]
            if current > ema:
                score += 5
                reasons.append(f"Above EMA{period}")
            else:
                score -= 5
                reasons.append(f"Below EMA{period}")

    # Supertrend
    if "supertrend_direction" in df.columns:
        st_dir = df["supertrend_direction"].iloc[-1]
        if st_dir == 1:
            score += 10
            reasons.append("Supertrend bullish")
        else:
            score -= 10
            reasons.append("Supertrend bearish")

    # ADX
    if "adx" in df.columns:
        adx = df["adx"].iloc[-1]
        if not pd.isna(adx):
            if adx > 25:
                reasons.append(f"ADX {adx:.0f} - strong trend")
            else:
                reasons.append(f"ADX {adx:.0f} - weak trend")
                score -= 5

    return {
        "score": max(0, min(100, score)),
        "reasons": reasons,
    }


def _momentum_score(df: pd.DataFrame) -> Dict:
    """Score momentum indicators."""
    score = 50
    reasons = []
    close = df["close"]

    # RSI
    if "rsi" in df.columns:
        rsi = df["rsi"].iloc[-1]
        if not pd.isna(rsi):
            if rsi > 70:
                score -= 10
                reasons.append(f"RSI overbought ({rsi:.0f})")
            elif rsi > 55:
                score += 5
                reasons.append(f"RSI bullish ({rsi:.0f})")
            elif rsi < 30:
                score += 5  # Potential bounce
                reasons.append(f"RSI oversold ({rsi:.0f}) - potential bounce")
            elif rsi < 45:
                score -= 5
                reasons.append(f"RSI bearish ({rsi:.0f})")

    # MACD
    if "macd" in df.columns and "macd_signal" in df.columns:
        macd = df["macd"].iloc[-1]
        signal = df["macd_signal"].iloc[-1]
        if not pd.isna(macd) and not pd.isna(signal):
            if macd > signal:
                score += 10
                reasons.append("MACD above signal")
            else:
                score -= 10
                reasons.append("MACD below signal")

            # Crossover
            if len(df) > 1:
                prev_macd = df["macd"].iloc[-2]
                prev_signal = df["macd_signal"].iloc[-2]
                if not pd.isna(prev_macd) and not pd.isna(prev_signal):
                    if macd > signal and prev_macd <= prev_signal:
                        score += 5
                        reasons.append("MACD bullish crossover")
                    elif macd < signal and prev_macd >= prev_signal:
                        score -= 5
                        reasons.append("MACD bearish crossover")

    # Stochastic RSI
    if "stoch_rsi_k" in df.columns:
        k = df["stoch_rsi_k"].iloc[-1]
        if not pd.isna(k):
            if k > 80:
                score -= 5
                reasons.append(f"StochRSI overbought ({k:.0f})")
            elif k < 20:
                score += 5
                reasons.append(f"StochRSI oversold ({k:.0f})")

    # ROC
    if "roc" in df.columns:
        roc = df["roc"].iloc[-1]
        if not pd.isna(roc):
            if roc > 0:
                score += 3
                reasons.append(f"Positive ROC ({roc:.1f}%)")
            else:
                score -= 3
                reasons.append(f"Negative ROC ({roc:.1f}%)")

    return {
        "score": max(0, min(100, score)),
        "reasons": reasons,
    }


def _volatility_score(df: pd.DataFrame) -> Dict:
    """Score volatility indicators."""
    score = 50
    reasons = []

    # ATR
    if "atr" in df.columns and "close" in df.columns:
        atr = df["atr"].iloc[-1]
        close = df["close"].iloc[-1]
        if not pd.isna(atr) and close > 0:
            atr_pct = atr / close * 100
            if atr_pct > 4:
                reasons.append(f"ATR {atr_pct:.1f}% - very high volatility")
                score -= 10
            elif atr_pct > 2:
                reasons.append(f"ATR {atr_pct:.1f}% - moderate volatility")
            else:
                reasons.append(f"ATR {atr_pct:.1f}% - low volatility")
                score += 5

    # Bollinger Bands
    if "bb_pct_b" in df.columns:
        bb = df["bb_pct_b"].iloc[-1]
        if not pd.isna(bb):
            if bb > 0.8:
                reasons.append(f"Price near upper Bollinger Band")
                score -= 5
            elif bb < 0.2:
                reasons.append(f"Price near lower Bollinger Band")
                score += 5
            else:
                reasons.append(f"Price within Bollinger Bands")

    # Historical volatility
    if "historical_volatility" in df.columns:
        hv = df["historical_volatility"].iloc[-1]
        if not pd.isna(hv):
            reasons.append(f"Historical volatility: {hv*100:.1f}% annualized")

    return {
        "score": max(0, min(100, score)),
        "reasons": reasons,
    }


def _volume_score(df: pd.DataFrame) -> Dict:
    """Score volume indicators."""
    score = 50
    reasons = []

    if "volume" not in df.columns:
        return {"score": 50, "reasons": ["Volume data unavailable"]}

    # Relative volume
    if "relative_volume" in df.columns:
        rv = df["relative_volume"].iloc[-1]
        if not pd.isna(rv):
            if rv > 2:
                score += 5
                reasons.append(f"Very high volume ({rv:.1f}x avg)")
            elif rv > 1.2:
                score += 3
                reasons.append(f"Above average volume ({rv:.1f}x)")
            elif rv < 0.5:
                score -= 3
                reasons.append(f"Low volume ({rv:.1f}x avg)")

    # OBV trend
    if "obv" in df.columns and len(df) > 20:
        obv_recent = df["obv"].tail(20)
        obv_trend = obv_recent.iloc[-1] - obv_recent.iloc[0]
        if obv_trend > 0:
            score += 5
            reasons.append("OBV trending up - accumulation")
        else:
            score -= 5
            reasons.append("OBV trending down - distribution")

    # A/D line
    if "ad_line" in df.columns and len(df) > 20:
        ad_recent = df["ad_line"].tail(20)
        ad_trend = ad_recent.iloc[-1] - ad_recent.iloc[0]
        if ad_trend > 0:
            score += 3
            reasons.append("Accumulation/Distribution trending up")
        else:
            score -= 3
            reasons.append("Accumulation/Distribution trending down")

    return {
        "score": max(0, min(100, score)),
        "reasons": reasons,
    }


def _price_action_score(df: pd.DataFrame) -> Dict:
    """Score price action."""
    score = 50
    reasons = []

    close = df["close"]
    current = close.iloc[-1]

    # Price vs recent range
    if len(close) >= 20:
        range_20 = close.tail(20)
        pct_in_range = (current - range_20.min()) / (range_20.max() - range_20.min()) if range_20.max() != range_20.min() else 0.5
        if pct_in_range > 0.7:
            score += 5
            reasons.append("Price in upper part of recent range")
        elif pct_in_range < 0.3:
            score -= 5
            reasons.append("Price in lower part of recent range")

    # Recent momentum
    if len(close) >= 5:
        recent_return = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100
        if recent_return > 3:
            score += 5
            reasons.append(f"Strong recent momentum (+{recent_return:.1f}%)")
        elif recent_return < -3:
            score -= 5
            reasons.append(f"Weak recent momentum ({recent_return:.1f}%)")

    # Higher highs / higher lows
    if len(df) >= 10:
        highs = df["high"].tail(10)
        lows = df["low"].tail(10)
        recent_hh = sum(1 for i in range(1, len(highs)) if highs.iloc[i] > highs.iloc[i-1])
        recent_hl = sum(1 for i in range(1, len(lows)) if lows.iloc[i] > lows.iloc[i-1])
        if recent_hh >= 5 and recent_hl >= 5:
            score += 10
            reasons.append("Strong HH/HL structure")
        elif recent_hh >= 4 or recent_hl >= 4:
            score += 5
            reasons.append("Moderately bullish price structure")

    return {
        "score": max(0, min(100, score)),
        "reasons": reasons,
    }


def _explain_score(signals: Dict, overall: float) -> str:
    """Generate human-readable explanation of the score."""
    parts = []
    for key, signal in signals.items():
        score = signal["score"]
        if score >= 65:
            parts.append(f"{key.title()} is bullish ({score:.0f}/100)")
        elif score <= 35:
            parts.append(f"{key.title()} is bearish ({score:.0f}/100)")
        else:
            parts.append(f"{key.title()} is neutral ({score:.0f}/100)")

    overall_label = "Bullish" if overall >= 65 else ("Bearish" if overall <= 35 else "Neutral")
    summary = f"Overall technical score: {overall:.0f}/100 ({overall_label})"
    detail = " | ".join(parts)

    return f"{summary}\n{detail}"
