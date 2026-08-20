"""
News data provider for stock analysis.
Fetches news from yfinance and web sources.
"""
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class NewsProvider:
    """Provides news data for stocks."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_news(self, ticker: str, exchange: str = "NSE") -> List[Dict[str, Any]]:
        """
        Fetch news for a stock from multiple sources.
        Returns list of news items with title, source, date, sentiment hint, category.
        """
        all_news = []

        # 1. yfinance news
        yf_news = self._get_yfinance_news(ticker)
        all_news.extend(yf_news)

        # 2. Google News via scraping (fallback)
        google_news = self._get_google_news(ticker, exchange)
        all_news.extend(google_news)

        # Deduplicate by title similarity
        all_news = self._deduplicate(all_news)

        # Categorize and add sentiment hints
        for item in all_news:
            item["category"] = self._categorize_news(item.get("title", "") + " " + item.get("summary", ""))
            item["sentiment_hint"] = self._sentiment_hint(item.get("title", "") + " " + item.get("summary", ""))

        return all_news

    def _get_yfinance_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch news from yfinance."""
        try:
            stock = yf.Ticker(ticker)
            news_items = []
            yf_news = stock.news or []

            for item in yf_news:
                content = item.get("content", {})
                if isinstance(content, dict):
                    title = content.get("title", "")
                    summary = content.get("summary", "")
                    provider = content.get("provider", {})
                    source = provider.get("displayName", "Unknown") if isinstance(provider, dict) else "Unknown"
                    pub_date = content.get("pubDate", "")
                    thumb = content.get("thumbnail", {})
                    resolutions = thumb.get("resolutions", []) if isinstance(thumb, dict) else []
                    image = resolutions[0].get("url", "") if resolutions else ""
                else:
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                    source = item.get("publisher", "Unknown")
                    pub_date = item.get("providerPublishTime", "")
                    image = ""

                if title:
                    news_items.append({
                        "title": title,
                        "summary": summary if isinstance(summary, str) else str(summary),
                        "source": source,
                        "date": self._parse_date(pub_date),
                        "url": item.get("link", ""),
                        "image": image,
                        "provider": "yfinance",
                    })

            return news_items
        except Exception as e:
            logger.warning(f"Error fetching yfinance news for {ticker}: {e}")
            return []

    def _get_google_news(self, ticker: str, exchange: str = "NSE") -> List[Dict[str, Any]]:
        """Fetch news from Google News RSS."""
        try:
            query = f"{ticker} stock {exchange} news"
            url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
            resp = self.session.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item")

            news_items = []
            for item in items[:15]:  # Limit to 15
                title = item.find("title")
                source = item.find("source")
                pub_date = item.find("pubDate")
                link = item.find("link")

                if title:
                    news_items.append({
                        "title": title.get_text(strip=True),
                        "summary": "",
                        "source": source.get_text(strip=True) if source else "Google News",
                        "date": self._parse_date(pub_date.get_text(strip=True) if pub_date else ""),
                        "url": link.get_text(strip=True) if link else "",
                        "image": "",
                        "provider": "google_news",
                    })

            return news_items
        except Exception as e:
            logger.warning(f"Error fetching Google News for {ticker}: {e}")
            return []

    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats into ISO format."""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # If it's already a timestamp
        if isinstance(date_str, (int, float)):
            try:
                return datetime.fromtimestamp(date_str).strftime("%Y-%m-%d")
            except Exception:
                return datetime.now().strftime("%Y-%m-%d")

        # Common date formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
        ]:
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                continue

        return datetime.now().strftime("%Y-%m-%d")

    def _deduplicate(self, news: List[Dict]) -> List[Dict]:
        """Remove duplicate news items based on title similarity."""
        seen_titles = set()
        unique = []
        for item in news:
            # Simple dedup: normalize title and check
            normalized = re.sub(r'[^a-z0-9]', '', item["title"].lower())[:50]
            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique.append(item)
        return unique

    def _categorize_news(self, text: str) -> str:
        """Categorize news based on keywords."""
        text_lower = text.lower()
        categories = {
            "Earnings": ["earnings", "revenue", "profit", "quarterly results", "net profit", "eps", "quarter"],
            "Orders": ["order", "contract", "deal", "win", "bagged"],
            "Management Changes": ["ceo", "cfo", "managing director", "chairman", "resign", "appoint", "leadership"],
            "Regulatory Issues": ["regulatory", "sebi", "rbi", "compliance", "penalty", "fine", "notice"],
            "Litigation": ["lawsuit", "litigation", "court", "legal", "dispute", "case"],
            "Debt": ["debt", "borrowing", "loan", "credit", "leverage", "repay"],
            "Expansion": ["expand", "new plant", "capacity", "investment", "capex", "growth"],
            "M&A": ["acquisition", "merger", "takeover", "buyout", "stake"],
            "Government Policy": ["policy", "budget", "tax", "tariff", "government", "minister"],
            "Sector Developments": ["sector", "industry", "market share", "competitive"],
        }

        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                return category
        return "General"

    def _sentiment_hint(self, text: str) -> str:
        """Provide a basic sentiment hint based on keyword analysis."""
        text_lower = text.lower()
        positive_words = [
            "surge", "gain", "rise", "profit", "growth", "bull", "upgrade",
            "buy", "outperform", "beat", "strong", "record", "high", "boost",
            "rally", "positive", "innovation", "expansion", "partnership",
            "revenue up", "good", "excellent", "recovery", "dividend",
        ]
        negative_words = [
            "fall", "drop", "loss", "decline", "bear", "downgrade", "sell",
            "underperform", "miss", "weak", "low", "crash", "concern",
            "negative", "debt", "lawsuit", "penalty", "risk", "warning",
            "fraud", "scam", "investigation", "bankruptcy", "default",
        ]

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count + 1:
            return "Positive"
        elif neg_count > pos_count + 1:
            return "Negative"
        return "Neutral"
