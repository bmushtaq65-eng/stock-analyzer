"""
Candlestick Pattern Detection.
Detects: Doji, Hammer, Inverted Hammer, Shooting Star, Engulfing,
Morning Star, Evening Star, Harami, Piercing, Dark Cloud Cover.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any


def detect_candlestick_patterns(df: pd.DataFrame) -> List[Dict]:
    """Detect candlestick patterns in the last N candles."""
    if df is None or df.empty or len(df) < 3:
        return []

    patterns = []
    recent = df.tail(10)  # Check last 10 candles

    for i in range(2, len(recent)):
        curr = recent.iloc[i]
        prev = recent.iloc[i - 1]
        prev2 = recent.iloc[i - 2]

        body = abs(curr["close"] - curr["open"])
        upper_shadow = curr["high"] - max(curr["open"], curr["close"])
        lower_shadow = min(curr["open"], curr["close"]) - curr["low"]
        total_range = curr["high"] - curr["low"]

        if total_range == 0:
            continue

        # 1. Doji
        if body / total_range < 0.1:
            patterns.append({
                "pattern": "Doji",
                "bias": "Neutral",
                "confirmation_required": True,
                "description": "Indecision candle with very small body. Signals potential reversal at tops/bottoms. Needs confirmation from next candle.",
                "confidence": 50,
                "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
            })

        # 2. Hammer (bullish, at bottom of downtrend)
        if (lower_shadow > 2 * body and upper_shadow < body * 0.3 and
                curr["close"] > curr["open"]):  # Bullish hammer
            # Check if near recent lows
            recent_low = df["low"].tail(20).min()
            if curr["low"] <= recent_low * 1.02:
                patterns.append({
                    "pattern": "Hammer",
                    "bias": "Bullish",
                    "confirmation_required": True,
                    "description": "Small body at top with long lower shadow. Suggests buyers stepped in after selling pressure. Bullish if confirmed by next bullish candle.",
                    "confidence": 60,
                    "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
                })

        # 3. Inverted Hammer
        if (upper_shadow > 2 * body and lower_shadow < body * 0.3):
            patterns.append({
                "pattern": "Inverted Hammer",
                "bias": "Bullish (if at support)",
                "confirmation_required": True,
                "description": "Small body at bottom with long upper shadow. Can indicate reversal if it appears after a downtrend. Needs confirmation.",
                "confidence": 50,
                "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
            })

        # 4. Shooting Star
        if (upper_shadow > 2 * body and lower_shadow < body * 0.3 and
                curr["close"] < curr["open"]):
            recent_high = df["high"].tail(20).max()
            if curr["high"] >= recent_high * 0.98:
                patterns.append({
                    "pattern": "Shooting Star",
                    "bias": "Bearish",
                    "confirmation_required": True,
                    "description": "Small body at bottom with long upper shadow. Bearish reversal signal when at resistance. Suggests rejection of higher prices.",
                    "confidence": 60,
                    "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
                })

        # 5. Bullish Engulfing
        prev_body = abs(prev["close"] - prev["open"])
        if (prev["close"] < prev["open"] and  # Previous bearish
                curr["close"] > curr["open"] and  # Current bullish
                curr["open"] <= prev["close"] and
                curr["close"] >= prev["open"] and
                body > prev_body):
            patterns.append({
                "pattern": "Bullish Engulfing",
                "bias": "Bullish",
                "confirmation_required": False,
                "description": "Current bullish candle completely engulfs previous bearish candle. Strong bullish reversal signal, especially at support levels.",
                "confidence": 70,
                "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
            })

        # 6. Bearish Engulfing
        if (prev["close"] > prev["open"] and  # Previous bullish
                curr["close"] < curr["open"] and  # Current bearish
                curr["open"] >= prev["close"] and
                curr["close"] <= prev["open"] and
                body > prev_body):
            patterns.append({
                "pattern": "Bearish Engulfing",
                "bias": "Bearish",
                "confirmation_required": False,
                "description": "Current bearish candle completely engulfs previous bullish candle. Strong bearish reversal signal, especially at resistance levels.",
                "confidence": 70,
                "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
            })

        # 7. Morning Star (3-candle pattern)
        if i >= 2:
            prev2_body = abs(prev2["close"] - prev2["open"])
            prev2_bearish = prev2["close"] < prev2["open"]
            star_body = abs(curr["close"] - curr["open"])

            if (prev2_bearish and prev2_body > total_range * 0.3 and
                    prev_body / total_range < 0.2 and  # Small body middle candle
                    curr["close"] > curr["open"] and
                    curr["close"] > (prev2["open"] + prev2["close"]) / 2):
                patterns.append({
                    "pattern": "Morning Star",
                    "bias": "Bullish",
                    "confirmation_required": False,
                    "description": "Three-candle bullish reversal: large bearish, small body (star), then large bullish. Strong reversal signal.",
                    "confidence": 75,
                    "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
                })

        # 8. Evening Star
        if i >= 2:
            prev2_body = abs(prev2["close"] - prev2["open"])
            prev2_bullish = prev2["close"] > prev2["open"]
            star_body = abs(curr["close"] - curr["open"])

            if (prev2_bullish and prev2_body > total_range * 0.3 and
                    prev_body / total_range < 0.2 and
                    curr["close"] < curr["open"] and
                    curr["close"] < (prev2["open"] + prev2["close"]) / 2):
                patterns.append({
                    "pattern": "Evening Star",
                    "bias": "Bearish",
                    "confirmation_required": False,
                    "description": "Three-candle bearish reversal: large bullish, small body (star), then large bearish. Strong reversal signal.",
                    "confidence": 75,
                    "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
                })

        # 9. Harami (bullish)
        prev_body = abs(prev["close"] - prev["open"])
        if (prev["close"] < prev["open"] and
                curr["close"] > curr["open"] and
                curr["open"] > prev["close"] and
                curr["close"] < prev["open"] and
                body < prev_body * 0.5):
            patterns.append({
                "pattern": "Bullish Harami",
                "bias": "Bullish",
                "confirmation_required": True,
                "description": "Small bullish candle inside previous large bearish candle. Possible trend reversal. Needs confirmation.",
                "confidence": 55,
                "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
            })

        # 10. Piercing Pattern
        if (prev["close"] < prev["open"] and
                curr["close"] > curr["open"] and
                curr["open"] < prev["low"] and
                curr["close"] > (prev["open"] + prev["close"]) / 2 and
                curr["close"] < prev["open"]):
            patterns.append({
                "pattern": "Piercing Pattern",
                "bias": "Bullish",
                "confirmation_required": True,
                "description": "Bullish candle opens below previous low then closes above midpoint of previous bearish candle. Moderate bullish signal.",
                "confidence": 60,
                "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
            })

        # 11. Dark Cloud Cover
        if (prev["close"] > prev["open"] and
                curr["close"] < curr["open"] and
                curr["open"] > prev["high"] and
                curr["close"] < (prev["open"] + prev["close"]) / 2 and
                curr["close"] > prev["open"]):
            patterns.append({
                "pattern": "Dark Cloud Cover",
                "bias": "Bearish",
                "confirmation_required": True,
                "description": "Bearish candle opens above previous high then closes below midpoint of previous bullish candle. Moderate bearish signal.",
                "confidence": 60,
                "date": str(recent.index[i].date()) if hasattr(recent.index[i], 'date') else str(recent.index[i]),
            })

    # Deduplicate patterns from same date
    seen = set()
    unique = []
    for p in patterns:
        key = (p["date"], p["pattern"])
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique
