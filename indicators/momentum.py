"""
Momentum Indicators: RSI, MACD, Stochastic RSI, Stochastic Oscillator, ROC
"""
import pandas as pd
import numpy as np
from typing import Optional


def calculate_rsi(df: pd.DataFrame, period: int = 14, col: str = "close") -> pd.Series:
    """Relative Strength Index (RSI)."""
    delta = df[col].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    col: str = "close",
) -> pd.DataFrame:
    """MACD, Signal, and Histogram."""
    ema_fast = df[col].ewm(span=fast, adjust=False).mean()
    ema_slow = df[col].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return pd.DataFrame({
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_histogram": histogram,
    }, index=df.index)


def calculate_stochastic_rsi(
    df: pd.DataFrame, rsi_period: int = 14, stoch_period: int = 14, k: int = 3, d: int = 3
) -> pd.DataFrame:
    """Stochastic RSI: Stochastic applied to RSI values."""
    rsi = calculate_rsi(df, rsi_period)

    stoch_rsi_min = rsi.rolling(window=stoch_period, min_periods=1).min()
    stoch_rsi_max = rsi.rolling(window=stoch_period, min_periods=1).max()

    stoch_rsi = (rsi - stoch_rsi_min) / (stoch_rsi_max - stoch_rsi_min).replace(0, np.nan)

    stoch_k = stoch_rsi.rolling(window=k, min_periods=1).mean() * 100
    stoch_d = stoch_k.rolling(window=d, min_periods=1).mean()

    return pd.DataFrame({
        "stoch_rsi": stoch_rsi * 100,
        "stoch_rsi_k": stoch_k,
        "stoch_rsi_d": stoch_d,
    }, index=df.index)


def calculate_stochastic(
    df: pd.DataFrame, k_period: int = 14, d_period: int = 3, smooth: int = 3
) -> pd.DataFrame:
    """Stochastic Oscillator (%K, %D)."""
    low_min = df["low"].rolling(window=k_period, min_periods=1).min()
    high_max = df["high"].rolling(window=k_period, min_periods=1).max()

    denominator = (high_max - low_min).replace(0, np.nan)
    fast_k = ((df["close"] - low_min) / denominator) * 100
    slow_k = fast_k.rolling(window=smooth, min_periods=1).mean()
    slow_d = slow_k.rolling(window=d_period, min_periods=1).mean()

    return pd.DataFrame({
        "stoch_k": slow_k,
        "stoch_d": slow_d,
    }, index=df.index)


def calculate_roc(df: pd.DataFrame, period: int = 12, col: str = "close") -> pd.Series:
    """Rate of Change (ROC)."""
    prev = df[col].shift(period)
    roc = ((df[col] - prev) / prev.replace(0, np.nan)) * 100
    return roc


def calculate_momentum_indicators(df: pd.DataFrame, config: Optional[dict] = None) -> pd.DataFrame:
    """Calculate all momentum indicators and add to DataFrame."""
    from config import TA_DEFAULTS as defaults
    cfg = config or defaults

    # RSI
    df["rsi"] = calculate_rsi(df, cfg["rsi_period"])

    # MACD
    macd_df = calculate_macd(df, cfg["macd_fast"], cfg["macd_slow"], cfg["macd_signal"])
    for col in macd_df.columns:
        df[col] = macd_df[col]

    # Stochastic RSI
    stoch_rsi_df = calculate_stochastic_rsi(df, cfg["rsi_period"], cfg["stoch_rsi_period"])
    for col in stoch_rsi_df.columns:
        df[col] = stoch_rsi_df[col]

    # Stochastic Oscillator
    stoch_df = calculate_stochastic(df, cfg["stoch_k"], cfg["stoch_d"])
    for col in stoch_df.columns:
        df[col] = stoch_df[col]

    # ROC
    df["roc"] = calculate_roc(df, cfg["roc_period"])

    return df
