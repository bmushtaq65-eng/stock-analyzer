"""
Technical Indicators Package.
"""
from .trend import calculate_trend_indicators
from .momentum import calculate_momentum_indicators
from .volatility import calculate_volatility_indicators
from .volume import calculate_volume_indicators


def calculate_all_indicators(df, config=None):
    """Calculate all technical indicators on a DataFrame with OHLCV data."""
    if df is None or df.empty:
        return df

    df = calculate_trend_indicators(df, config)
    df = calculate_momentum_indicators(df, config)
    df = calculate_volatility_indicators(df, config)
    df = calculate_volume_indicators(df, config)
    return df
