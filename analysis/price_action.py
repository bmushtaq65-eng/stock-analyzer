"""
Price Action Analysis: Higher highs/lows, consolidation, breakout/breakdown,
flags, triangles, wedges, double tops/bottoms, H&S, etc.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional


def analyze_price_action(df: pd.DataFrame) -> Dict[str, Any]:
    """Comprehensive price action analysis."""
    if df is None or df.empty or len(df) < 10:
        return {"error": "Insufficient data for price action analysis"}

    result = {
        "trend_structure": _analyze_trend_structure(df),
        "patterns": _detect_patterns(df),
        "consolidation": _detect_consolidation(df),
        "gaps": _detect_gaps(df),
        "candlestick_patterns": [],  # Handled by patterns.py module
        "current_structure": _current_structure(df),
    }

    return result


def _analyze_trend_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze higher highs/lows, lower highs/lows structure."""
    window = 5
    swing_highs, swing_lows = _get_swings(df, window)

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return {"trend": "Insufficient data", "structure": []}

    # Analyze last N swing points
    n = min(len(swing_highs), 6)
    recent_highs = swing_highs[-n:]
    recent_lows = swing_lows[-n:]

    # Check for higher highs
    hh_count = sum(1 for i in range(1, len(recent_highs)) if recent_highs[i] > recent_highs[i - 1])
    hl_count = sum(1 for i in range(1, len(recent_lows)) if recent_lows[i] > recent_lows[i - 1])
    lh_count = sum(1 for i in range(1, len(recent_highs)) if recent_highs[i] < recent_highs[i - 1])
    ll_count = sum(1 for i in range(1, len(recent_lows)) if recent_lows[i] < recent_lows[i - 1])

    total_pairs = len(recent_highs) - 1

    structure = []
    for i in range(1, len(recent_highs)):
        if recent_highs[i] > recent_highs[i - 1]:
            structure.append("HH")
        elif recent_highs[i] < recent_highs[i - 1]:
            structure.append("LH")
        else:
            structure.append("=")

    for i in range(1, len(recent_lows)):
        if recent_lows[i] > recent_lows[i - 1]:
            structure.append("HL")
        elif recent_lows[i] < recent_lows[i - 1]:
            structure.append("LL")
        else:
            structure.append("=")

    # Determine trend
    if hh_count > lh_count and hl_count > ll_count:
        trend = "Uptrend (Higher Highs, Higher Lows)"
        bullish = True
    elif lh_count > hh_count and ll_count > hl_count:
        trend = "Downtrend (Lower Highs, Lower Lows)"
        bullish = False
    elif hl_count > ll_count and hh_count <= lh_count:
        trend = "Potential reversal from downtrend (Higher Lows forming)"
        bullish = None
    else:
        trend = "Ranging / No clear structure"
        bullish = None

    return {
        "trend": trend,
        "higher_highs": hh_count,
        "higher_lows": hl_count,
        "lower_highs": lh_count,
        "lower_lows": ll_count,
        "structure": structure,
        "swing_highs": [round(h, 2) for h in recent_highs[-5:]],
        "swing_lows": [round(l, 2) for l in recent_lows[-5:]],
    }


def _detect_patterns(df: pd.DataFrame) -> List[Dict]:
    """Detect common price action patterns."""
    patterns = []

    # Double Top
    result = _detect_double_top(df)
    if result:
        patterns.append(result)

    # Double Bottom
    result = _detect_double_bottom(df)
    if result:
        patterns.append(result)

    # Head and Shoulders
    result = _detect_head_shoulders(df)
    if result:
        patterns.append(result)

    # Bull Flag / Bear Flag
    result = _detect_flags(df)
    if result:
        patterns.append(result)

    # Triangle
    result = _detect_triangle(df)
    if result:
        patterns.append(result)

    # Wedge
    result = _detect_wedge(df)
    if result:
        patterns.append(result)

    # Cup and Handle
    result = _detect_cup_handle(df)
    if result:
        patterns.append(result)

    return patterns


def _detect_double_top(df: pd.DataFrame) -> Optional[Dict]:
    """Detect double top pattern."""
    swing_highs, _ = _get_swings(df, 5)
    if len(swing_highs) < 3:
        return None

    last_three = swing_highs[-3:]
    # Two nearby highs with similar values
    if (abs(last_three[-1] - last_three[-3]) / last_three[-3] < 0.02 and
            last_three[-2] < last_three[-1] * 0.97):
        return {
            "name": "Double Top",
            "bias": "Bearish",
            "confidence": 65,
            "description": "Two peaks at similar levels with a trough in between. If confirmed with break below the trough, bearish continuation expected.",
        }
    return None


def _detect_double_bottom(df: pd.DataFrame) -> Optional[Dict]:
    """Detect double bottom pattern."""
    _, swing_lows = _get_swings(df, 5)
    if len(swing_lows) < 3:
        return None

    last_three = swing_lows[-3:]
    if (abs(last_three[-1] - last_three[-3]) / last_three[-3] < 0.02 and
            last_three[-2] > last_three[-1] * 1.03):
        return {
            "name": "Double Bottom",
            "bias": "Bullish",
            "confidence": 65,
            "description": "Two troughs at similar levels with a peak in between. If confirmed with break above the peak, bullish continuation expected.",
        }
    return None


def _detect_head_shoulders(df: pd.DataFrame) -> Optional[Dict]:
    """Detect head and shoulders pattern."""
    swing_highs, _ = _get_swings(df, 5)
    if len(swing_highs) < 3:
        return None

    last_three = swing_highs[-3:]
    left, head, right = last_three

    # Head should be highest
    if head > left and head > right:
        # Shoulders at similar levels
        if abs(left - right) / head < 0.03:
            return {
                "name": "Head and Shoulders",
                "bias": "Bearish",
                "confidence": 70,
                "description": "Classic bearish reversal pattern with left shoulder, higher head, and right shoulder at similar level to left.",
            }

    return None


def _detect_flags(df: pd.DataFrame) -> Optional[Dict]:
    """Detect flag patterns."""
    if len(df) < 20:
        return None

    recent = df.tail(20)
    # Flag pole: strong move in first 10 bars
    pole_start = recent["close"].iloc[0]
    pole_end = recent["close"].iloc[10]
    pole_pct = (pole_end - pole_start) / pole_start * 100

    # Flag: slight pullback in next 10 bars
    flag_start = recent["close"].iloc[10]
    flag_end = recent["close"].iloc[-1]
    flag_pct = (flag_end - flag_start) / flag_start * 100

    if pole_pct > 3 and -3 < flag_pct < 0:
        return {
            "name": "Bull Flag",
            "bias": "Bullish",
            "confidence": 60,
            "description": "Strong upward pole followed by slight downward consolidation. If it breaks above flag resistance, continuation expected.",
        }
    elif pole_pct < -3 and 0 < flag_pct < 3:
        return {
            "name": "Bear Flag",
            "bias": "Bearish",
            "confidence": 60,
            "description": "Strong downward pole followed by slight upward consolidation. If it breaks below flag support, continuation expected.",
        }

    return None


def _detect_triangle(df: pd.DataFrame) -> Optional[Dict]:
    """Detect triangle patterns."""
    swing_highs, swing_lows = _get_swings(df, 3)
    if len(swing_highs) < 3 or len(swing_lows) < 3:
        return None

    # Converging highs and lows
    highs_trend = np.polyfit(range(len(swing_highs[-3:])), swing_highs[-3:], 1)[0]
    lows_trend = np.polyfit(range(len(swing_lows[-3:])), swing_lows[-3:], 1)[0]

    if highs_trend < 0 and lows_trend > 0:
        return {
            "name": "Symmetrical Triangle",
            "bias": "Neutral (breakout direction TBD)",
            "confidence": 55,
            "description": "Converging trendlines with lower highs and higher lows. Breakout direction determines bias.",
        }
    elif highs_trend < 0 and lows_trend <= 0:
        return {
            "name": "Descending Triangle",
            "bias": "Bearish",
            "confidence": 60,
            "description": "Flat support with descending resistance. More likely to break down.",
        }
    elif highs_trend >= 0 and lows_trend > 0:
        return {
            "name": "Ascending Triangle",
            "bias": "Bullish",
            "confidence": 60,
            "description": "Flat resistance with ascending support. More likely to break up.",
        }

    return None


def _detect_wedge(df: pd.DataFrame) -> Optional[Dict]:
    """Detect wedge patterns."""
    swing_highs, swing_lows = _get_swings(df, 3)
    if len(swing_highs) < 3 or len(swing_lows) < 3:
        return None

    highs_trend = np.polyfit(range(len(swing_highs[-3:])), swing_highs[-3:], 1)[0]
    lows_trend = np.polyfit(range(len(swing_lows[-3:])), swing_lows[-3:], 1)[0]

    # Rising wedge (both rising, highs slower than lows)
    if highs_trend > 0 and lows_trend > 0 and highs_trend < lows_trend:
        return {
            "name": "Rising Wedge",
            "bias": "Bearish",
            "confidence": 60,
            "description": "Both trendlines rising but converging. Typically resolves to the downside.",
        }
    # Falling wedge
    elif highs_trend < 0 and lows_trend < 0 and highs_trend > lows_trend:
        return {
            "name": "Falling Wedge",
            "bias": "Bullish",
            "confidence": 60,
            "description": "Both trendlines falling but converging. Typically resolves to the upside.",
        }

    return None


def _detect_cup_handle(df: pd.DataFrame) -> Optional[Dict]:
    """Detect cup and handle pattern."""
    if len(df) < 30:
        return None

    # Simplified: check if we have a U-shape followed by a slight pullback
    prices = df["close"].tail(30).values
    mid = len(prices) // 2

    # Cup: first half drops, second half recovers
    if prices[mid] < prices[0] * 0.92 and prices[-5] > prices[mid] * 1.08:
        # Handle: slight pullback in last few bars
        if prices[-1] < prices[-5]:
            handle_pct = (prices[-5] - prices[-1]) / prices[-5] * 100
            if handle_pct < 5:
                return {
                    "name": "Cup and Handle",
                    "bias": "Bullish",
                    "confidence": 55,
                    "description": "U-shaped recovery (cup) followed by slight pullback (handle). If it breaks above the cup rim, bullish.",
                }

    return None


def _detect_consolidation(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect consolidation (range-bound) periods."""
    if len(df) < 20:
        return {"is_consolidating": False}

    recent = df.tail(20)
    price_range = recent["high"].max() - recent["low"].min()
    avg_price = recent["close"].mean()
    range_pct = price_range / avg_price * 100

    # Check if range is narrow (less than 8% over 20 bars)
    is_consolidating = range_pct < 8

    # ATR-based check
    if "atr" in recent.columns:
        avg_atr = recent["atr"].mean()
        atr_pct = avg_atr / avg_price * 100
        is_narrow = atr_pct < 1.5
    else:
        is_narrow = False

    return {
        "is_consolidating": is_consolidating and is_narrow,
        "range_pct": round(range_pct, 2),
        "upper_range": round(recent["high"].max(), 2),
        "lower_range": round(recent["low"].min(), 2),
        "atr_narrow": is_narrow,
    }


def _detect_gaps(df: pd.DataFrame) -> List[Dict]:
    """Detect gap up / gap down events."""
    gaps = []
    if len(df) < 2:
        return gaps

    for i in range(1, len(df)):
        prev_high = df["high"].iloc[i - 1]
        prev_low = df["low"].iloc[i - 1]
        curr_open = df["open"].iloc[i]
        curr_close = df["close"].iloc[i]

        # Gap up: open > previous high
        if curr_open > prev_high:
            gap_pct = (curr_open - prev_high) / prev_high * 100
            gaps.append({
                "date": str(df.index[i].date()) if hasattr(df.index[i], 'date') else str(df.index[i]),
                "type": "Gap Up",
                "gap_pct": round(gap_pct, 2),
                "from": round(prev_high, 2),
                "to": round(curr_open, 2),
            })

        # Gap down: open < previous low
        elif curr_open < prev_low:
            gap_pct = (prev_low - curr_open) / prev_low * 100
            gaps.append({
                "date": str(df.index[i].date()) if hasattr(df.index[i], 'date') else str(df.index[i]),
                "type": "Gap Down",
                "gap_pct": round(gap_pct, 2),
                "from": round(prev_low, 2),
                "to": round(curr_open, 2),
            })

    return gaps[-5:]  # Last 5 gaps


def _current_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """Summarize the current price action structure."""
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last

    candle_type = "bullish" if last["close"] > last["open"] else "bearish"
    body_pct = abs(last["close"] - last["open"]) / last["open"] * 100 if last["open"] > 0 else 0

    # Upper shadow / lower shadow ratio
    upper_shadow = last["high"] - max(last["open"], last["close"])
    lower_shadow = min(last["open"], last["close"]) - last["low"]
    body = abs(last["close"] - last["open"])

    return {
        "last_candle": candle_type,
        "body_pct": round(body_pct, 2),
        "upper_shadow": round(upper_shadow, 2),
        "lower_shadow": round(lower_shadow, 2),
        "prev_close": round(prev["close"], 2),
        "changed_pct": round((last["close"] - prev["close"]) / prev["close"] * 100, 2),
    }


def _get_swings(df: pd.DataFrame, window: int = 5) -> Tuple[List[float], List[float]]:
    """Get swing highs and lows."""
    swing_highs = []
    swing_lows = []

    if len(df) < 2 * window + 1:
        return [df["high"].max()], [df["low"].min()]

    highs = df["high"].values
    lows = df["low"].values

    for i in range(window, len(df) - window):
        if highs[i] == max(highs[i - window: i + window + 1]):
            swing_highs.append(highs[i])
        if lows[i] == min(lows[i - window: i + window + 1]):
            swing_lows.append(lows[i])

    if not swing_highs:
        swing_highs = [df["high"].max()]
    if not swing_lows:
        swing_lows = [df["low"].min()]

    return swing_highs, swing_lows
