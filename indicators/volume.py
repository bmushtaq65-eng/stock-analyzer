"""
Volume Indicators: Volume SMA, Relative Volume, OBV, Accumulation/Distribution
"""
import pandas as pd
import numpy as np
from typing import Optional


def calculate_volume_sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Simple Moving Average of volume."""
    if "volume" not in df.columns:
        return pd.Series(index=df.index, dtype=float)
    return df["volume"].rolling(window=period, min_periods=1).mean()


def calculate_relative_volume(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Relative Volume: current volume / average volume."""
    if "volume" not in df.columns:
        return pd.Series(index=df.index, dtype=float)
    avg_vol = calculate_volume_sma(df, period)
    return df["volume"] / avg_vol.replace(0, np.nan)


def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume (OBV)."""
    if "volume" not in df.columns or "close" not in df.columns:
        return pd.Series(index=df.index, dtype=float)

    obv = pd.Series(0.0, index=df.index)
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] + df["volume"].iloc[i]
        elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] - df["volume"].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i - 1]

    return obv


def calculate_ad_line(df: pd.DataFrame) -> pd.Series:
    """Accumulation/Distribution Line."""
    if not all(c in df.columns for c in ["high", "low", "close", "volume"]):
        return pd.Series(index=df.index, dtype=float)

    hl_range = (df["high"] - df["low"]).replace(0, np.nan)
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl_range
    ad_vol = mfm * df["volume"]
    ad_line = ad_vol.cumsum()
    return ad_line


def calculate_volume_indicators(df: pd.DataFrame, config: Optional[dict] = None) -> pd.DataFrame:
    """Calculate all volume indicators and add to DataFrame."""
    # Volume SMA
    df["volume_sma_20"] = calculate_volume_sma(df, 20)
    df["volume_sma_50"] = calculate_volume_sma(df, 50)

    # Relative Volume
    df["relative_volume"] = calculate_relative_volume(df, 20)

    # OBV
    df["obv"] = calculate_obv(df)

    # Accumulation/Distribution
    df["ad_line"] = calculate_ad_line(df)

    return df
