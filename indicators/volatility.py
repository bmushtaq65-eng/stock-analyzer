"""
Volatility Indicators: ATR, Bollinger Bands, Bollinger Band Width, Historical Volatility
"""
import pandas as pd
import numpy as np
from typing import Optional


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range (ATR)."""
    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=period, min_periods=1).mean()
    return atr


def calculate_bollinger_bands(
    df: pd.DataFrame, period: int = 20, std_dev: float = 2.0, col: str = "close"
) -> pd.DataFrame:
    """Bollinger Bands: middle, upper, lower, width, %B."""
    sma = df[col].rolling(window=period, min_periods=1).mean()
    rolling_std = df[col].rolling(window=period, min_periods=1).std()

    upper = sma + (std_dev * rolling_std)
    lower = sma - (std_dev * rolling_std)

    # Band Width
    width = (upper - lower) / sma.replace(0, np.nan)

    # %B (position within bands: 0 = lower, 1 = upper)
    band_range = (upper - lower).replace(0, np.nan)
    pct_b = (df[col] - lower) / band_range

    return pd.DataFrame({
        "bb_middle": sma,
        "bb_upper": upper,
        "bb_lower": lower,
        "bb_width": width,
        "bb_pct_b": pct_b,
    }, index=df.index)


def calculate_historical_volatility(
    df: pd.DataFrame, period: int = 20, col: str = "close"
) -> pd.Series:
    """Historical Volatility (annualized)."""
    log_returns = np.log(df[col] / df[col].shift(1))
    hv = log_returns.rolling(window=period, min_periods=1).std() * np.sqrt(252)
    return hv


def calculate_volatility_indicators(df: pd.DataFrame, config: Optional[dict] = None) -> pd.DataFrame:
    """Calculate all volatility indicators and add to DataFrame."""
    from config import TA_DEFAULTS as defaults
    cfg = config or defaults

    # ATR
    df["atr"] = calculate_atr(df, cfg["atr_period"])

    # Bollinger Bands
    bb_df = calculate_bollinger_bands(df, cfg["bb_period"], cfg["bb_std"])
    for col in bb_df.columns:
        df[col] = bb_df[col]

    # Historical Volatility
    df["historical_volatility"] = calculate_historical_volatility(df)

    return df
