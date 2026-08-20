"""
Market Data Provider - Fetches real-time and historical market data via yfinance.

Design: Provider interface pattern so we can swap in other APIs later.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EXCHANGES, TIMEFRAMES

logger = logging.getLogger(__name__)


class MarketDataProvider:
    """
    Abstract interface for market data providers.
    Current implementation: yfinance.
    """

    def __init__(self, exchange: str = "NSE"):
        self.exchange = exchange
        self.exchange_config = EXCHANGES.get(exchange, EXCHANGES["NSE"])

    def _symbol(self, ticker: str) -> str:
        """Convert user ticker to yfinance-compatible symbol."""
        ticker = ticker.strip().upper()
        suffix = self.exchange_config["suffix"]
        # If the ticker already has the suffix or is for US exchanges
        if not suffix or ticker.endswith(suffix):
            return ticker
        # For Indian stocks, try .NS first (NSE), then .BO (BSE)
        if self.exchange == "NSE" and not ticker.endswith(".NS"):
            return f"{ticker}{suffix}"
        if self.exchange == "BSE" and not ticker.endswith(".BO"):
            return f"{ticker}{suffix}"
        return ticker

    def _try_alternative_symbols(self, ticker: str) -> Optional[str]:
        """Try alternative symbol formats if primary fails."""
        ticker = ticker.strip().upper()
        alternatives = []
        if self.exchange in ("NSE", "BSE"):
            alternatives = [f"{ticker}.NS", f"{ticker}.BO", ticker]
        elif self.exchange in ("NYSE", "NASDAQ"):
            alternatives = [ticker, ticker.replace(".", "-")]
        else:
            alternatives = [f"{ticker}{self.exchange_config['suffix']}", ticker]

        for sym in alternatives:
            try:
                stock = yf.Ticker(sym)
                info = stock.info
                if info and info.get("regularMarketPrice"):
                    return sym
                if info and info.get("symbol"):
                    return sym
            except Exception:
                continue
        return None

    def get_stock(self, ticker: str) -> Tuple[Optional[yf.Ticker], str]:
        """Get a yf.Ticker object, trying alternatives if needed."""
        symbol = self._symbol(ticker)
        try:
            stock = yf.Ticker(symbol)
            info = stock.info or {}
            # Check if we got valid data
            if info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose"):
                return stock, symbol
        except Exception as e:
            logger.warning(f"Failed to get data for {symbol}: {e}")

        # Try alternatives
        alt = self._try_alternative_symbols(ticker)
        if alt:
            try:
                return yf.Ticker(alt), alt
            except Exception:
                pass

        return None, symbol

    def get_quote(self, ticker: str) -> Dict[str, Any]:
        """Get real-time quote data for a stock."""
        stock, symbol = self.get_stock(ticker)
        if not stock:
            return {"error": f"Could not retrieve data for {ticker}", "symbol": ticker}

        try:
            info = stock.info or {}
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return {"error": str(e), "symbol": ticker}

        currency = self.exchange_config.get("currency", "")

        # Extract available fields
        quote = {
            "symbol": ticker.upper(),
            "exchange": self.exchange,
            "currency": currency,
            "name": info.get("longName") or info.get("shortName") or ticker.upper(),
            "current_price": info.get("regularMarketPrice") or info.get("currentPrice"),
            "previous_close": info.get("previousClose") or info.get("regularMarketPreviousClose"),
            "open": info.get("regularMarketOpen") or info.get("open"),
            "day_high": info.get("regularMarketDayHigh") or info.get("dayHigh"),
            "day_low": info.get("regularMarketDayLow") or info.get("dayLow"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "volume": info.get("regularMarketVolume") or info.get("volume"),
            "avg_volume": info.get("averageVolume") or info.get("averageVolume10days"),
            "market_cap": info.get("marketCap"),
            "float_shares": info.get("floatShares"),
            "bid": info.get("bid"),
            "ask": info.get("ask"),
            "bid_size": info.get("bidSize"),
            "ask_size": info.get("askSize"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "beta": info.get("beta"),
            "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "trailing_eps": info.get("trailingEps"),
            "forward_eps": info.get("forwardEps"),
            "book_value": info.get("bookValue"),
            "earnings_per_share": info.get("trailingEps"),
            "revenue": info.get("totalRevenue"),
            "revenue_growth": info.get("revenueGrowth"),
            "profit_margins": info.get("profitMargins"),
            "operating_margins": info.get("operatingMargins"),
            "gross_margins": info.get("grossMargins"),
            "ebitda": info.get("ebitda"),
            "ebitda_margins": info.get("ebitdaMargins"),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash"),
            "debt_to_equity": info.get("debtToEquity"),
            "free_cashflow": info.get("freeCashflow"),
            "operating_cashflow": info.get("operatingCashflow"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
            "return_on_capital": info.get("returnOnCapital"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "interest_coverage": info.get("interestCoverage"),
            "enterprise_value": info.get("enterpriseValue"),
            "ev_to_ebitda": info.get("enterpriseToEbitda"),
            "ev_to_revenue": info.get("enterpriseToRevenue"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "employees": info.get("fullTimeEmployees"),
            "website": info.get("website"),
            "description": info.get("longBusinessSummary"),
            "exchange_timezone": info.get("exchangeTimezoneName"),
            "market_state": info.get("marketState"),
            "last_updated": datetime.now().isoformat(),
        }

        # Promoter / institutional holdings (if available)
        quote["insider_ownership"] = info.get("heldPercentInsiders")
        quote["institutional_ownership"] = info.get("heldPercentInstitutions")
        quote["fund_ownership"] = info.get("heldPercentFundHolders")
        quote["minority_interest"] = info.get("minorityInterest")

        # Remove None values for cleanliness
        quote = {k: v for k, v in quote.items() if v is not None}

        return quote

    def get_history(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """Get historical OHLCV data."""
        stock, symbol = self.get_stock(ticker)
        if stock is None:
            return pd.DataFrame()

        try:
            if start and end:
                df = stock.history(start=start, end=end, interval=interval)
            else:
                df = stock.history(period=period, interval=interval)

            if df.empty:
                return df

            # Standardize column names
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            df.index.name = "date"
            df.index = pd.to_datetime(df.index)
            # Remove timezone info for consistency
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            return df
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return pd.DataFrame()

    def get_intraday(
        self, ticker: str, interval: str = "5m", period: str = "5d"
    ) -> pd.DataFrame:
        """Get intraday OHLCV data."""
        return self.get_history(ticker, period=period, interval=interval)

    def get_corporate_actions(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """Get corporate actions (dividends, splits, etc.)."""
        stock, symbol = self.get_stock(ticker)
        if stock is None:
            return {}

        result = {}
        try:
            dividends = stock.dividends
            if dividends is not None and not dividends.empty:
                result["dividends"] = dividends.to_frame("dividend")
        except Exception as e:
            logger.warning(f"No dividend data for {symbol}: {e}")

        try:
            splits = stock.splits
            if splits is not None and not splits.empty:
                result["splits"] = splits.to_frame("split_ratio")
        except Exception as e:
            logger.warning(f"No split data for {symbol}: {e}")

        try:
            actions = stock.actions
            if actions is not None and not actions.empty:
                result["actions"] = actions
        except Exception as e:
            logger.warning(f"No actions data for {symbol}: {e}")

        return result

    def get_financials(self, ticker: str) -> Dict[str, Any]:
        """Get detailed financial statements."""
        stock, symbol = self.get_stock(ticker)
        if stock is None:
            return {}

        result = {}
        try:
            result["income_stmt"] = stock.income_stmt
        except Exception:
            pass
        try:
            result["balance_sheet"] = stock.balance_sheet
        except Exception:
            pass
        try:
            result["cashflow"] = stock.cashflow
        except Exception:
            pass
        try:
            result["quarterly_income"] = stock.quarterly_income_stmt
        except Exception:
            pass
        try:
            result["quarterly_balance"] = stock.quarterly_balance_sheet
        except Exception:
            pass
        try:
            result["quarterly_cashflow"] = stock.quarterly_cashflow
        except Exception:
            pass

        return result

    def get_recommendations(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get analyst recommendations."""
        stock, symbol = self.get_stock(ticker)
        if stock is None:
            return None
        try:
            recs = stock.recommendations
            return recs if recs is not None and not recs.empty else None
        except Exception:
            return None

    def get_earnings(self, ticker: str) -> Dict[str, Any]:
        """Get earnings data."""
        stock, symbol = self.get_stock(ticker)
        if stock is None:
            return {}
        result = {}
        try:
            result["earnings"] = stock.earnings
        except Exception:
            pass
        try:
            result["earnings_history"] = stock.earnings_history
        except Exception:
            pass
        try:
            result["earnings_dates"] = stock.earnings_dates
        except Exception:
            pass
        try:
            result["quarterly_earnings"] = stock.quarterly_earnings
        except Exception:
            pass
        return result

    def get_holder_data(self, ticker: str) -> Dict[str, Any]:
        """Get major and institutional holder data."""
        stock, symbol = self.get_stock(ticker)
        if stock is None:
            return {}
        result = {}
        try:
            result["major_holders"] = stock.major_holders
        except Exception:
            pass
        try:
            result["institutional_holders"] = stock.institutional_holders
        except Exception:
            pass
        return result

    def get_peer_comparison(self, ticker: str) -> Optional[List[str]]:
        """Get sector peers (if available from yfinance)."""
        stock, symbol = self.get_stock(ticker)
        if stock is None:
            return None
        try:
            info = stock.info or {}
            # yfinance doesn't directly provide peers, but we can get sector
            return None  # Will implement sector-based peer lookup
        except Exception:
            return None
