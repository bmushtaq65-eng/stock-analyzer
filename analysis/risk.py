"""
Risk Analysis Module.
Identifies: volatility, liquidity, debt, valuation, earnings, regulatory,
sector, market, concentration, and technical breakdown risks.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def risk_analysis(
    quote: Dict[str, Any],
    daily_df: Optional[pd.DataFrame] = None,
    sr_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Comprehensive risk analysis."""
    risks = {}

    # 1. Volatility Risk
    risks["volatility"] = _volatility_risk(daily_df, quote)

    # 2. Liquidity Risk
    risks["liquidity"] = _liquidity_risk(quote, daily_df)

    # 3. Debt Risk
    risks["debt"] = _debt_risk(quote)

    # 4. Valuation Risk
    risks["valuation"] = _valuation_risk(quote)

    # 5. Earnings Risk
    risks["earnings"] = _earnings_risk(quote)

    # 6. Regulatory Risk
    risks["regulatory"] = _regulatory_risk(quote)

    # 7. Sector Risk
    risks["sector"] = _sector_risk(quote)

    # 8. Market Risk
    risks["market"] = _market_risk(daily_df, quote)

    # 9. Concentration Risk
    risks["concentration"] = _concentration_risk(quote)

    # 10. Technical Breakdown Risk
    risks["technical"] = _technical_risk(daily_df, sr_data)

    # Overall risk rating
    overall = _calculate_overall_risk(risks)

    return {
        "individual_risks": risks,
        "overall_rating": overall["rating"],
        "overall_score": overall["score"],
        "explanation": overall["explanation"],
    }


def _volatility_risk(df, quote) -> Dict:
    risk_score = 5  # Moderate baseline
    details = []

    if df is not None and not df.empty and len(df) >= 20:
        returns = df["close"].pct_change().dropna()
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)
        details.append(f"Daily volatility: {daily_vol*100:.2f}%")
        details.append(f"Annualized volatility: {annual_vol*100:.1f}%")

        if annual_vol > 0.6:
            risk_score = 9
            details.append("Very high volatility")
        elif annual_vol > 0.4:
            risk_score = 7
            details.append("High volatility")
        elif annual_vol > 0.25:
            risk_score = 5
            details.append("Moderate volatility")
        elif annual_vol > 0.15:
            risk_score = 3
            details.append("Low volatility")
        else:
            risk_score = 2
            details.append("Very low volatility")

    beta = quote.get("beta")
    if beta:
        details.append(f"Beta: {beta:.2f}")
        if beta > 1.5:
            risk_score = min(10, risk_score + 1)

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _liquidity_risk(quote, df) -> Dict:
    risk_score = 5
    details = []

    volume = quote.get("volume", 0)
    avg_vol = quote.get("avg_volume", 1)
    market_cap = quote.get("market_cap", 0)

    if avg_vol and avg_vol > 0:
        ratio = volume / avg_vol
        details.append(f"Volume/Avg Volume: {ratio:.2f}x")

    if market_cap:
        if market_cap > 1e11:
            risk_score = 2
            details.append("Large cap - high liquidity")
        elif market_cap > 1e10:
            risk_score = 4
            details.append("Mid-large cap - good liquidity")
        elif market_cap > 1e9:
            risk_score = 6
            details.append("Mid cap - moderate liquidity")
        elif market_cap > 5e8:
            risk_score = 7
            details.append("Small-mid cap - lower liquidity")
        else:
            risk_score = 9
            details.append("Small cap - low liquidity")

    bid = quote.get("bid")
    ask = quote.get("ask")
    if bid and ask:
        spread = (ask - bid) / ((ask + bid) / 2) * 100
        details.append(f"Bid-ask spread: {spread:.3f}%")
        if spread > 0.5:
            risk_score = min(10, risk_score + 2)

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _debt_risk(quote) -> Dict:
    risk_score = 5
    details = []

    de = quote.get("debt_to_equity")
    if de is not None:
        details.append(f"Debt/Equity: {de:.1f}")
        if de > 200:
            risk_score = 9
            details.append("Very high leverage")
        elif de > 100:
            risk_score = 7
            details.append("High leverage")
        elif de > 50:
            risk_score = 5
            details.append("Moderate leverage")
        elif de > 20:
            risk_score = 3
            details.append("Low leverage")
        else:
            risk_score = 2
            details.append("Very low leverage")

    debt = quote.get("total_debt")
    cash = quote.get("total_cash")
    if debt and cash:
        net = cash - debt
        details.append(f"Net debt/cash: {'Net cash' if net > 0 else f'₹{abs(net)/1e7:.0f}Cr net debt'}")
        if net < 0 and abs(net) > debt * 0.8:
            risk_score = min(10, risk_score + 1)

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _valuation_risk(quote) -> Dict:
    risk_score = 5
    details = []

    pe = quote.get("pe_ratio")
    if pe:
        details.append(f"P/E: {pe:.1f}")
        if pe > 50:
            risk_score = 8
            details.append("Very high P/E - high valuation risk")
        elif pe > 35:
            risk_score = 7
            details.append("High P/E")
        elif pe < 0:
            risk_score = 9
            details.append("Negative earnings")
        elif pe < 15:
            risk_score = 3
            details.append("Low P/E - reasonable valuation")

    pb = quote.get("price_to_book")
    if pb:
        details.append(f"P/B: {pb:.1f}")
        if pb > 10:
            risk_score = min(10, risk_score + 1)

    peg = quote.get("peg_ratio")
    if peg:
        details.append(f"PEG: {peg:.2f}")
        if peg > 2:
            risk_score = min(10, risk_score + 1)

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _earnings_risk(quote) -> Dict:
    risk_score = 5
    details = []

    margins = quote.get("profit_margins")
    if margins is not None:
        details.append(f"Profit margin: {margins*100:.1f}%")
        if margins < 0:
            risk_score = 8
            details.append("Negative margins - high earnings risk")
        elif margins < 0.05:
            risk_score = 6
            details.append("Thin margins")

    rev_growth = quote.get("revenue_growth")
    if rev_growth is not None:
        details.append(f"Revenue growth: {rev_growth*100:.1f}%")
        if rev_growth < -0.1:
            risk_score = min(10, risk_score + 2)
            details.append("Declining revenue")

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _regulatory_risk(quote) -> Dict:
    risk_score = 4
    details = []

    sector = quote.get("sector", "")
    industry = quote.get("industry", "")
    country = quote.get("country", "")

    # Sector-specific regulatory risks
    if any(s in sector.lower() for s in ["bank", "financial"]):
        risk_score = 6
        details.append("Financial sector - regulatory scrutiny")
    if any(s in industry.lower() for s in ["pharma", "drug"]):
        risk_score = 5
        details.append("Pharma - FDA/regulatory risks")
    if any(s in industry.lower() for s in ["mining", "oil", "gas"]):
        risk_score = 6
        details.append("Natural resources - environmental regulations")

    if country in ("India",):
        risk_score = max(risk_score, 4)
        details.append("India - policy/regulatory changes possible")

    if not details:
        details.append("Standard regulatory environment")

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _sector_risk(quote) -> Dict:
    risk_score = 5
    details = []

    sector = quote.get("sector", "Unknown")
    details.append(f"Sector: {sector}")

    high_risk_sectors = ["energy", "mining", "real estate", "crypto", "banking"]
    if any(s in sector.lower() for s in high_risk_sectors):
        risk_score = 7
        details.append("Cyclical/volatile sector")
    else:
        risk_score = 4
        details.append("Stable sector")

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _market_risk(df, quote) -> Dict:
    risk_score = 5
    details = []

    beta = quote.get("beta")
    if beta:
        details.append(f"Beta: {beta:.2f}")
        if beta > 1.5:
            risk_score = 7
            details.append("More volatile than market")
        elif beta > 1.0:
            risk_score = 5
            details.append("Moves with market, slightly more volatile")
        elif beta < 0.5:
            risk_score = 3
            details.append("Defensive stock")
        else:
            risk_score = 4

    if df is not None and len(df) >= 20:
        returns = df["close"].tail(20).pct_change().dropna()
        recent_perf = (1 + returns).prod() - 1
        details.append(f"20-day return: {recent_perf*100:.1f}%")
        if recent_perf < -0.1:
            risk_score = min(10, risk_score + 2)

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _concentration_risk(quote) -> Dict:
    risk_score = 5
    details = []

    insider = quote.get("insider_ownership")
    inst = quote.get("institutional_ownership")

    if insider:
        details.append(f"Insider ownership: {insider*100:.1f}%")
        if insider > 0.7:
            risk_score = 7
            details.append("High insider concentration")
        elif insider > 0.5:
            risk_score = 6
        else:
            risk_score = 4

    if inst:
        details.append(f"Institutional ownership: {inst*100:.1f}%")

    if not details:
        details.append("Shareholding data unavailable")

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _technical_risk(df, sr_data) -> Dict:
    risk_score = 5
    details = []

    if df is None or df.empty or len(df) < 20:
        return {"score": 5, "level": "MODERATE", "details": ["Insufficient data"]}

    close = df["close"].iloc[-1]
    sma_200 = df["close"].rolling(min(200, len(df)), min_periods=1).mean().iloc[-1]

    if close < sma_200:
        risk_score = 7
        details.append("Price below SMA 200 - long-term downtrend")
    else:
        risk_score = 4
        details.append("Price above SMA 200")

    # Check if near support
    if sr_data and sr_data.get("support_levels"):
        nearest_support = sr_data["support_levels"][0]["price"]
        dist_to_support = (close - nearest_support) / close * 100
        details.append(f"Distance to nearest support: {dist_to_support:.1f}%")
        if dist_to_support < 2:
            risk_score = min(10, risk_score + 1)
            details.append("Very close to support - breakdown risk")

    # RSI check
    if len(df) >= 14:
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0.0).ewm(alpha=1/14, min_periods=14).mean()
        loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/14, min_periods=14).mean()
        rsi = (100 - 100 / (1 + gain / loss.replace(0, np.nan))).iloc[-1]
        if rsi > 80:
            details.append(f"RSI overbought ({rsi:.0f})")
            risk_score = min(10, risk_score + 1)
        elif rsi < 20:
            details.append(f"RSI oversold ({rsi:.0f}) - bounce possible")

    return {"score": risk_score, "level": _score_to_level(risk_score), "details": details}


def _calculate_overall_risk(risks: Dict) -> Dict:
    """Calculate overall risk from individual risk components."""
    scores = [r.get("score", 5) for r in risks.values()]
    avg_score = sum(scores) / len(scores) if scores else 5

    # Weight certain risks more heavily
    weighted = {
        "volatility": 1.5,
        "liquidity": 1.2,
        "debt": 1.3,
        "valuation": 1.0,
        "earnings": 1.0,
        "technical": 1.2,
    }
    weighted_sum = 0
    weight_total = 0
    for key, weight in weighted.items():
        if key in risks:
            weighted_sum += risks[key]["score"] * weight
            weight_total += weight

    weighted_avg = weighted_sum / weight_total if weight_total > 0 else avg_score

    if weighted_avg >= 8:
        rating = "VERY HIGH"
    elif weighted_avg >= 6:
        rating = "HIGH"
    elif weighted_avg >= 4:
        rating = "MODERATE"
    else:
        rating = "LOW"

    explanation_parts = []
    for key, risk in risks.items():
        if risk["score"] >= 7:
            explanation_parts.append(f"{key.replace('_', ' ').title()}: {risk['level']}")

    explanation = "Key risk factors: " + "; ".join(explanation_parts) if explanation_parts else "No significant risk factors identified"

    return {
        "score": round(weighted_avg, 1),
        "rating": rating,
        "explanation": explanation,
    }


def _score_to_level(score: int) -> str:
    if score >= 8:
        return "VERY HIGH"
    elif score >= 6:
        return "HIGH"
    elif score >= 4:
        return "MODERATE"
    else:
        return "LOW"
