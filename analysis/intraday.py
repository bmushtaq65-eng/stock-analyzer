"""
Intraday Analysis Module.
Analyzes opening price, VWAP, gaps, intraday support/resistance,
generates bullish/bearish scenarios.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def intraday_analysis(
    daily_df: pd.DataFrame,
    intraday_df: Optional[pd.DataFrame] = None,
    current_quote: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive intraday analysis.
    Returns scenarios, key levels, momentum, etc.
    """
    if daily_df is None or daily_df.empty:
        return {"error": "No data for intraday analysis"}

    result = {
        "key_levels": {},
        "scenarios": {},
        "momentum": {},
        "vwap_analysis": {},
        "opening_analysis": {},
    }

    # Current price
    if current_quote and current_quote.get("current_price"):
        current_price = current_quote["current_price"]
        day_open = current_quote.get("open")
        day_high = current_quote.get("day_high")
        day_low = current_quote.get("day_low")
        prev_close = current_quote.get("previous_close")
        volume = current_quote.get("volume", 0)
        avg_volume = current_quote.get("avg_volume", 0)
    else:
        last = daily_df.iloc[-1]
        current_price = last["close"]
        day_open = last.get("open", current_price)
        day_high = last.get("high", current_price)
        day_low = last.get("low", current_price)
        prev_close = daily_df["close"].iloc[-2] if len(daily_df) > 1 else current_price
        volume = last.get("volume", 0)
        avg_volume = daily_df["volume"].tail(20).mean() if "volume" in daily_df.columns else 0

    # Previous day data
    if len(daily_df) >= 2:
        prev_high = daily_df["high"].iloc[-2]
        prev_low = daily_df["low"].iloc[-2]
        prev_close_val = daily_df["close"].iloc[-2]
    else:
        prev_high = day_high
        prev_low = day_low
        prev_close_val = prev_close

    # Gap
    gap = None
    gap_pct = None
    if day_open and prev_close_val:
        gap = day_open - prev_close_val
        gap_pct = gap / prev_close_val * 100

    # VWAP
    if intraday_df is not None and not intraday_df.empty and "volume" in intraday_df.columns:
        typical = (intraday_df["high"] + intraday_df["low"] + intraday_df["close"]) / 3
        cum_tp_vol = (typical * intraday_df["volume"]).cumsum()
        cum_vol = intraday_df["volume"].cumsum()
        vwap = (cum_tp_vol / cum_vol.replace(0, np.nan)).iloc[-1]
    else:
        vwap = current_price  # Fallback

    # Relative volume
    rel_volume = volume / avg_volume if avg_volume > 0 else 1.0

    # Intraday support/resistance
    recent_daily = daily_df.tail(20)
    intraday_support = _find_intraday_levels(recent_daily, current_price, "support")
    intraday_resistance = _find_intraday_levels(recent_daily, current_price, "resistance")

    # Opening range
    opening_range_high = day_high
    opening_range_low = day_low
    opening_range_mid = (opening_range_high + opening_range_low) / 2

    # Momentum indicators
    momentum = _calculate_intraday_momentum(daily_df)

    # Trend strength
    if len(daily_df) >= 20:
        close_above_20 = (current_price > daily_df["close"].tail(20).mean())
        close_above_50 = (current_price > daily_df["close"].tail(50).mean()) if len(daily_df) >= 50 else None
    else:
        close_above_20 = current_price > prev_close_val
        close_above_50 = None

    # Build result
    result["key_levels"] = {
        "current_price": round(current_price, 2),
        "day_open": round(day_open, 2) if day_open else None,
        "day_high": round(day_high, 2) if day_high else None,
        "day_low": round(day_low, 2) if day_low else None,
        "prev_day_high": round(prev_high, 2),
        "prev_day_low": round(prev_low, 2),
        "prev_day_close": round(prev_close_val, 2),
        "vwap": round(vwap, 2) if not pd.isna(vwap) else None,
        "gap": round(gap, 2) if gap else None,
        "gap_pct": round(gap_pct, 2) if gap_pct else None,
        "opening_range_high": round(opening_range_high, 2),
        "opening_range_low": round(opening_range_low, 2),
        "opening_range_mid": round(opening_range_mid, 2),
        "intraday_support": intraday_support,
        "intraday_resistance": intraday_resistance,
    }

    result["momentum"] = {
        "price_vs_open": round(((current_price - day_open) / day_open * 100), 2) if day_open else 0,
        "price_vs_prev_close": round(((current_price - prev_close_val) / prev_close_val * 100), 2),
        "above_vwap": current_price > vwap if not pd.isna(vwap) else None,
        "relative_volume": round(rel_volume, 2),
        "trend_20d": "Bullish" if close_above_20 else "Bearish",
        "trend_50d": "Bullish" if close_above_50 else ("Bearish" if close_above_50 is not None else "N/A"),
    }

    result["vwap_analysis"] = {
        "vwap": round(vwap, 2) if not pd.isna(vwap) else None,
        "above_vwap": current_price > vwap if not pd.isna(vwap) else None,
        "vwap_distance_pct": round((current_price - vwap) / vwap * 100, 2) if not pd.isna(vwap) and vwap > 0 else None,
    }

    result["opening_analysis"] = {
        "gap": result["key_levels"]["gap"],
        "gap_pct": result["key_levels"]["gap_pct"],
        "gap_type": _classify_gap(gap_pct),
    }

    # Scenarios
    result["scenarios"] = _generate_intraday_scenarios(
        current_price, prev_high, prev_low, prev_close_val,
        day_open, day_high, day_low, vwap,
        intraday_support, intraday_resistance,
        momentum,
    )

    return result


def _find_intraday_levels(df: pd.DataFrame, current_price: float, level_type: str) -> list:
    """Find intraday support or resistance levels."""
    levels = []

    if level_type == "support":
        candidates = df["low"].values
        candidates = candidates[candidates < current_price]
        # Add prev day low, recent lows
        unique_lows = sorted(set(candidates), reverse=True)
        for price in unique_lows[:3]:
            distance_pct = (current_price - price) / current_price * 100
            levels.append({
                "price": round(price, 2),
                "distance_pct": round(distance_pct, 2),
                "type": "support",
            })
    else:
        candidates = df["high"].values
        candidates = candidates[candidates > current_price]
        unique_highs = sorted(set(candidates))
        for price in unique_highs[:3]:
            distance_pct = (price - current_price) / current_price * 100
            levels.append({
                "price": round(price, 2),
                "distance_pct": round(distance_pct, 2),
                "type": "resistance",
            })

    return levels


def _calculate_intraday_momentum(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate short-term momentum indicators."""
    if len(df) < 5:
        return {}

    close = df["close"]
    rsi = _rsi(close, 14)
    ema_9 = close.ewm(span=9, adjust=False).mean()

    return {
        "rsi_14": round(rsi.iloc[-1], 1) if not pd.isna(rsi.iloc[-1]) else None,
        "price_vs_ema9": round((close.iloc[-1] - ema_9.iloc[-1]) / ema_9.iloc[-1] * 100, 2),
    }


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).ewm(alpha=1 / period, min_periods=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1 / period, min_periods=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _classify_gap(gap_pct: Optional[float]) -> str:
    if gap_pct is None:
        return "No Gap"
    if gap_pct > 2:
        return "Large Gap Up"
    elif gap_pct > 0.5:
        return "Gap Up"
    elif gap_pct < -2:
        return "Large Gap Down"
    elif gap_pct < -0.5:
        return "Gap Down"
    return "Flat Open"


def _generate_intraday_scenarios(
    current_price, prev_high, prev_low, prev_close,
    day_open, day_high, day_low, vwap,
    supports, resistances, momentum
) -> Dict[str, Any]:
    """Generate bullish and bearish intraday scenarios."""
    # Determine key levels
    nearest_support = prev_low
    nearest_resistance = prev_high

    if supports:
        nearest_support = supports[0]["price"]
    if resistances:
        nearest_resistance = resistances[0]["price"]

    # Bullish scenario
    bullish = {
        "trigger": f"Price breaks above {round(nearest_resistance, 2)} with volume",
        "entry_zone": f"₹{round(nearest_resistance * 0.998, 2)} – ₹{round(nearest_resistance * 1.005, 2)}",
        "stop_loss": round(nearest_support, 2),
        "target_1": round(nearest_resistance + (nearest_resistance - nearest_support) * 0.5, 2),
        "target_2": round(nearest_resistance + (nearest_resistance - nearest_support) * 1.0, 2),
        "target_3": round(nearest_resistance + (nearest_resistance - nearest_support) * 1.5, 2),
        "invalidation": f"Price closes back below {round(nearest_resistance * 0.995, 2)}",
    }

    # Bearish scenario
    bearish = {
        "trigger": f"Price breaks below {round(nearest_support, 2)} with volume",
        "entry_zone": f"₹{round(nearest_support * 0.995, 2)} – ₹{round(nearest_support * 1.002, 2)}",
        "stop_loss": round(nearest_resistance, 2),
        "target_1": round(nearest_support - (nearest_resistance - nearest_support) * 0.5, 2),
        "target_2": round(nearest_support - (nearest_resistance - nearest_support) * 1.0, 2),
        "target_3": round(nearest_support - (nearest_resistance - nearest_support) * 1.5, 2),
        "invalidation": f"Price closes back above {round(nearest_support * 1.005, 2)}",
    }

    return {
        "bullish": bullish,
        "bearish": bearish,
    }
