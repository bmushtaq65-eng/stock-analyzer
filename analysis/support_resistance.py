"""
Support & Resistance Engine.
Identifies major/minor levels, pivot points, Fibonacci, high-volume zones.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional


def find_support_resistance(df: pd.DataFrame, lookback: int = 60) -> Dict[str, Any]:
    """
    Comprehensive support & resistance analysis.
    Returns dict with resistance levels, support levels, pivot points, fibonacci levels.
    """
    if df is None or df.empty or len(df) < 5:
        return _empty_sr()

    recent = df.tail(lookback).copy()
    current_price = df["close"].iloc[-1]

    result = {
        "current_price": current_price,
        "resistance_levels": [],
        "support_levels": [],
        "pivot_points": {},
        "fibonacci": {},
        "high_volume_zones": [],
        "breakout_zones": [],
        "breakdown_zones": [],
        "previous_highs_lows": {},
    }

    # 1. Swing high/low based S/R
    swing_highs, swing_lows = _find_swing_points(recent)
    all_levels = []

    for price in swing_highs:
        strength = _level_strength(price, recent, "resistance")
        all_levels.append({"price": price, "type": "resistance", **strength})

    for price in swing_lows:
        strength = _level_strength(price, recent, "support")
        all_levels.append({"price": price, "type": "support", **strength})

    # 2. Cluster nearby levels
    all_levels = _cluster_levels(all_levels, current_price, tolerance_pct=0.5)

    result["resistance_levels"] = sorted(
        [l for l in all_levels if l["price"] > current_price],
        key=lambda x: x["price"],
    )[:5]
    result["support_levels"] = sorted(
        [l for l in all_levels if l["price"] <= current_price],
        key=lambda x: x["price"],
        reverse=True,
    )[:5]

    # 3. Classic Pivot Points
    if len(recent) >= 2:
        prev_high = recent["high"].iloc[-2]
        prev_low = recent["low"].iloc[-2]
        prev_close = recent["close"].iloc[-2]
        result["pivot_points"] = _calculate_pivot_points(prev_high, prev_low, prev_close)

    # 4. Fibonacci Retracement Levels
    result["fibonacci"] = _calculate_fibonacci(recent)

    # 5. High Volume Zones
    result["high_volume_zones"] = _find_high_volume_zones(recent)

    # 6. Previous day high/low
    if len(df) >= 2:
        result["previous_highs_lows"] = {
            "prev_day_high": df["high"].iloc[-2],
            "prev_day_low": df["low"].iloc[-2],
            "prev_day_close": df["close"].iloc[-2],
        }

    # Add 52-week high/low if we have enough data
    if len(df) >= 200:
        result["previous_highs_lows"]["52w_high"] = df["high"].tail(252).max()
        result["previous_highs_lows"]["52w_low"] = df["low"].tail(252).min()

    return result


def _find_swing_points(
    df: pd.DataFrame, window: int = 5
) -> Tuple[List[float], List[float]]:
    """Find swing highs and swing lows."""
    swing_highs = []
    swing_lows = []

    if len(df) < 2 * window + 1:
        return swing_highs, swing_lows

    highs = df["high"].values
    lows = df["low"].values

    for i in range(window, len(df) - window):
        # Swing high
        if highs[i] == max(highs[i - window: i + window + 1]):
            swing_highs.append(highs[i])
        # Swing low
        if lows[i] == min(lows[i - window: i + window + 1]):
            swing_lows.append(lows[i])

    return swing_highs, swing_lows


def _level_strength(price: float, df: pd.DataFrame, level_type: str) -> Dict:
    """Evaluate the strength of a support/resistance level."""
    tolerance = price * 0.01  # 1% tolerance

    # Count touches
    if level_type == "resistance":
        touches = ((df["high"] >= price - tolerance) & (df["high"] <= price + tolerance)).sum()
        # How many times price was rejected
        rejections = 0
        for i in range(1, len(df)):
            if (df["high"].iloc[i] >= price - tolerance and
                df["high"].iloc[i] <= price + tolerance and
                df["close"].iloc[i] < price):
                rejections += 1
    else:
        touches = ((df["low"] <= price + tolerance) & (df["low"] >= price - tolerance)).sum()
        rejections = 0
        for i in range(1, len(df)):
            if (df["low"].iloc[i] <= price + tolerance and
                df["low"].iloc[i] >= price - tolerance and
                df["close"].iloc[i] > price):
                rejections += 1

    # Volume at the level
    mask = (df["low"] <= price + tolerance) & (df["high"] >= price - tolerance)
    avg_vol_at_level = df.loc[mask, "volume"].mean() if mask.any() else 0
    overall_avg_vol = df["volume"].mean()
    vol_ratio = avg_vol_at_level / overall_avg_vol if overall_avg_vol > 0 else 1

    # Determine strength
    score = touches * 2 + rejections * 3 + (vol_ratio * 2)
    if score >= 8:
        strength = "Very Strong"
    elif score >= 5:
        strength = "Strong"
    elif score >= 3:
        strength = "Moderate"
    else:
        strength = "Weak"

    reason = f"{touches} touch(es), {rejections} rejection(s)"
    if vol_ratio > 1.5:
        reason += f", high volume ({vol_ratio:.1f}x avg)"

    return {
        "strength": strength,
        "touches": int(touches),
        "volume_ratio": round(vol_ratio, 2),
        "reason": reason,
    }


def _cluster_levels(
    levels: List[Dict], current_price: float, tolerance_pct: float = 0.5
) -> List[Dict]:
    """Cluster nearby levels into zones."""
    if not levels:
        return levels

    levels.sort(key=lambda x: x["price"])
    clustered = []
    used = set()

    for i, level in enumerate(levels):
        if i in used:
            continue

        cluster = [level]
        for j in range(i + 1, len(levels)):
            if j in used:
                continue
            if abs(levels[j]["price"] - level["price"]) / level["price"] * 100 < tolerance_pct:
                cluster.append(levels[j])
                used.add(j)

        # Merge cluster
        if len(cluster) > 1:
            avg_price = np.mean([c["price"] for c in cluster])
            total_touches = sum(c.get("touches", 0) for c in cluster)
            max_strength = max(
                ["Weak", "Moderate", "Strong", "Very Strong"].index(c.get("strength", "Weak"))
                for c in cluster
            )
            strength_names = ["Weak", "Moderate", "Strong", "Very Strong"]
            merged = {
                "price": avg_price,
                "type": cluster[0]["type"],
                "strength": strength_names[min(max_strength + 1, 3)],
                "touches": total_touches,
                "reason": f"Clustered from {len(cluster)} nearby levels ({total_touches} total touches)",
            }
            clustered.append(merged)
        else:
            clustered.append(level)
        used.add(i)

    return clustered


def _calculate_pivot_points(
    high: float, low: float, close: float
) -> Dict[str, float]:
    """Calculate classic pivot points."""
    pp = (high + low + close) / 3

    return {
        "PP": round(pp, 2),
        "R1": round(2 * pp - low, 2),
        "R2": round(pp + (high - low), 2),
        "R3": round(high + 2 * (pp - low), 2),
        "S1": round(2 * pp - high, 2),
        "S2": round(pp - (high - low), 2),
        "S3": round(low - 2 * (high - pp), 2),
    }


def _calculate_fibonacci(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Fibonacci retracement and extension levels."""
    swing_high = df["high"].max()
    swing_low = df["low"].min()
    diff = swing_high - swing_low

    retracement_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    retracements = {}
    for level in retracement_levels:
        price = swing_high - (diff * level)
        retracements[f"Fib {level:.1%}"] = round(price, 2)

    # Extensions (beyond 100%)
    extension_levels = [1.272, 1.618, 2.0]
    extensions = {}
    for level in extension_levels:
        price = swing_low + (diff * level)
        extensions[f"Ext {level:.1%}"] = round(price, 2)

    return {
        "swing_high": swing_high,
        "swing_low": swing_low,
        "retracements": retracements,
        "extensions": extensions,
    }


def _find_high_volume_zones(df: pd.DataFrame, bins: int = 10) -> List[Dict]:
    """Find price zones with highest volume."""
    if "volume" not in df.columns or df["volume"].isna().all():
        return []

    # Create price bins
    price_min = df["low"].min()
    price_max = df["high"].max()
    price_bins = np.linspace(price_min, price_max, bins + 1)

    zones = []
    for i in range(len(price_bins) - 1):
        lower = price_bins[i]
        upper = price_bins[i + 1]
        mask = (df["low"] >= lower) & (df["high"] <= upper)
        vol = df.loc[mask, "volume"].sum()
        zones.append({
            "price_center": round((lower + upper) / 2, 2),
            "price_range": f"{round(lower, 2)} - {round(upper, 2)}",
            "total_volume": int(vol),
        })

    # Sort by volume, take top zones
    zones.sort(key=lambda x: x["total_volume"], reverse=True)
    return [z for z in zones if z["total_volume"] > 0][:5]


def _empty_sr() -> Dict:
    """Empty S/R result."""
    return {
        "current_price": 0,
        "resistance_levels": [],
        "support_levels": [],
        "pivot_points": {},
        "fibonacci": {},
        "high_volume_zones": [],
        "breakout_zones": [],
        "breakdown_zones": [],
        "previous_highs_lows": {},
    }
