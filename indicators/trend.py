"""
Trend Indicators: SMA, EMA, VWAP, Supertrend, ADX, +DI/-DI
"""
import pandas as pd
import numpy as np
from typing import Optional


def calculate_sma(df: pd.DataFrame, period: int, col: str = "close") -> pd.Series:
    """Simple Moving Average."""
    return df[col].rolling(window=period, min_periods=1).mean()


def calculate_ema(df: pd.DataFrame, period: int, col: str = "close") -> pd.Series:
    """Exponential Moving Average."""
    return df[col].ewm(span=period, adjust=False).mean()


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """Volume Weighted Average Price (intraday cumulative)."""
    if "high" not in df.columns or "low" not in df.columns or "volume" not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_tp_vol = (typical_price * df["volume"]).cumsum()
    cumulative_vol = df["volume"].cumsum()
    vwap = cumulative_tp_vol / cumulative_vol.replace(0, np.nan)
    return vwap


def calculate_supertrend(
    df: pd.DataFrame, period: int = 10, multiplier: float = 3.0
) -> pd.DataFrame:
    """Supertrend indicator."""
    atr = _calculate_atr_raw(df, period)

    hl2 = (df["high"] + df["low"]) / 2
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    supertrend.iloc[0] = upper_band.iloc[0]
    direction.iloc[0] = 1

    for i in range(1, len(df)):
        # Upper band
        if lower_band.iloc[i] > lower_band.iloc[i - 1] or df["close"].iloc[i - 1] < lower_band.iloc[i - 1]:
            lower_band.iloc[i] = lower_band.iloc[i]
        else:
            lower_band.iloc[i] = lower_band.iloc[i - 1]

        # Lower band
        if upper_band.iloc[i] < upper_band.iloc[i - 1] or df["close"].iloc[i - 1] > upper_band.iloc[i - 1]:
            upper_band.iloc[i] = upper_band.iloc[i]
        else:
            upper_band.iloc[i] = upper_band.iloc[i - 1]

        # Direction
        if direction.iloc[i - 1] == 1:  # Was bullish
            if df["close"].iloc[i] < lower_band.iloc[i]:
                direction.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]
            else:
                direction.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]
        else:  # Was bearish
            if df["close"].iloc[i] > upper_band.iloc[i]:
                direction.iloc[i] = 1
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                direction.iloc[i] = -1
                supertrend.iloc[i] = upper_band.iloc[i]

    return pd.DataFrame({
        "supertrend": supertrend,
        "supertrend_direction": direction,
        "supertrend_upper": upper_band,
        "supertrend_lower": lower_band,
    }, index=df.index)


def _calculate_atr_raw(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate ATR (used internally by Supertrend)."""
    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=1).mean()
    return atr


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Average Directional Index (ADX) with +DI and -DI.
    ADX > 25: trending. ADX < 20: ranging.
    """
    high = df["high"]
    low = df["low"]
    close = df["close"]

    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Directional Movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)

    plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
    minus_dm[(down_move > up_move) & (down_move > 0)] = down_move

    # Smoothed TR, +DM, -DM
    atr_s = tr.rolling(window=period, min_periods=1).sum()
    plus_dm_s = plus_dm.rolling(window=period, min_periods=1).sum()
    minus_dm_s = minus_dm.rolling(window=period, min_periods=1).sum()

    # +DI, -DI
    plus_di = 100 * (plus_dm_s / atr_s.replace(0, np.nan))
    minus_di = 100 * (minus_dm_s / atr_s.replace(0, np.nan))

    # DX
    di_sum = plus_di + minus_di
    dx = 100 * abs(plus_di - minus_di) / di_sum.replace(0, np.nan)

    # ADX
    adx = dx.rolling(window=period, min_periods=1).mean()

    return pd.DataFrame({
        "adx": adx,
        "plus_di": plus_di,
        "minus_di": minus_di,
    }, index=df.index)


def calculate_trend_indicators(df: pd.DataFrame, config: Optional[dict] = None) -> pd.DataFrame:
    """Calculate all trend indicators and add to DataFrame."""
    from config import TA_DEFAULTS as defaults
    cfg = config or defaults

    # SMAs
    for period in cfg["sma_periods"]:
        df[f"sma_{period}"] = calculate_sma(df, period)

    # EMAs
    for period in cfg["ema_periods"]:
        df[f"ema_{period}"] = calculate_ema(df, period)

    # VWAP
    df["vwap"] = calculate_vwap(df)

    # Supertrend
    st = calculate_supertrend(df, cfg["supertrend_period"], cfg["supertrend_multiplier"])
    for col in st.columns:
        df[col] = st[col]

    # ADX
    adx_df = calculate_adx(df, cfg["adx_period"])
    for col in adx_df.columns:
        df[col] = adx_df[col]

    return df
