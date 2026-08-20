"""
Long-Term Investment Analysis.
Fundamental analysis, valuation, quality scoring, investment thesis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def long_term_analysis(
    quote: Dict[str, Any],
    daily_df: Optional[pd.DataFrame] = None,
    financials: Optional[Dict] = None,
    holder_data: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Comprehensive long-term investment analysis.
    """
    result = {
        "fundamentals": {},
        "valuation": {},
        "quality_score": {},
        "growth_analysis": {},
        "institutional_analysis": {},
        "investment_thesis": {},
        "peers": {},
    }

    # Fundamentals
    result["fundamentals"] = _analyze_fundamentals(quote, financials)

    # Valuation
    result["valuation"] = _analyze_valuation(quote)

    # Quality Score
    result["quality_score"] = _calculate_quality_score(quote, financials)

    # Growth
    result["growth_analysis"] = _analyze_growth(quote, financials)

    # Holdings
    result["institutional_analysis"] = _analyze_holdings(quote, holder_data)

    # Investment thesis
    result["investment_thesis"] = _generate_thesis(result)

    return result


def _analyze_fundamentals(quote: Dict, financials: Optional[Dict]) -> Dict:
    """Analyze fundamental metrics."""
    fund = {}

    # Profitability
    fund["revenue"] = _fmt_value(quote.get("revenue"))
    fund["revenue_growth"] = _fmt_pct(quote.get("revenue_growth"))
    fund["profit_margins"] = _fmt_pct(quote.get("profit_margins"))
    fund["operating_margins"] = _fmt_pct(quote.get("operating_margins"))
    fund["ebitda"] = _fmt_value(quote.get("ebitda"))
    fund["ebitda_margins"] = _fmt_pct(quote.get("ebitda_margins"))
    fund["gross_margins"] = _fmt_pct(quote.get("gross_margins"))

    # Per share
    fund["eps"] = quote.get("earnings_per_share") or quote.get("trailing_eps")
    fund["book_value"] = quote.get("book_value")
    fund["revenue_per_share"] = None

    # Returns
    fund["roe"] = _fmt_pct(quote.get("return_on_equity"))
    fund["roa"] = _fmt_pct(quote.get("return_on_assets"))
    fund["roce"] = _fmt_pct(quote.get("return_on_capital"))

    # Balance sheet
    fund["total_debt"] = _fmt_value(quote.get("total_debt"))
    fund["total_cash"] = _fmt_value(quote.get("total_cash"))
    fund["debt_to_equity"] = _fmt_value(quote.get("debt_to_equity"))
    fund["current_ratio"] = _fmt_value(quote.get("current_ratio"))
    fund["quick_ratio"] = _fmt_value(quote.get("quick_ratio"))
    fund["interest_coverage"] = _fmt_value(quote.get("interest_coverage"))

    # Cash flow
    fund["free_cashflow"] = _fmt_value(quote.get("free_cashflow"))
    fund["operating_cashflow"] = _fmt_value(quote.get("operating_cashflow"))

    # Dividends
    fund["dividend_yield"] = _fmt_pct(quote.get("dividend_yield"))

    return fund


def _analyze_valuation(quote: Dict) -> Dict:
    """Analyze valuation metrics."""
    current_price = quote.get("current_price", 0)

    val = {
        "current_price": current_price,
        "market_cap": quote.get("market_cap"),
        "market_cap_formatted": _fmt_value(quote.get("market_cap")),
        "pe_ratio": quote.get("pe_ratio"),
        "forward_pe": quote.get("forward_pe"),
        "peg_ratio": quote.get("peg_ratio"),
        "price_to_book": quote.get("price_to_book"),
        "ev_to_ebitda": quote.get("ev_to_ebitda"),
        "ev_to_revenue": quote.get("ev_to_revenue"),
        "enterprise_value": quote.get("enterprise_value"),
    }

    # Valuation assessment
    assessment = "Unknown"
    reasons = []

    pe = quote.get("pe_ratio")
    if pe:
        if pe < 15:
            assessment = "Potentially Undervalued"
            reasons.append(f"P/E ({pe:.1f}) is low")
        elif pe > 35:
            assessment = "Potentially Overvalued"
            reasons.append(f"P/E ({pe:.1f}) is high")
        else:
            assessment = "Fairly Valued"
            reasons.append(f"P/E ({pe:.1f}) is in normal range")

    pb = quote.get("price_to_book")
    if pb:
        if pb < 1:
            reasons.append(f"P/B ({pb:.1f}) below 1 - potential value")
        elif pb > 10:
            reasons.append(f"P/B ({pb:.1f}) is high")

    peg = quote.get("peg_ratio")
    if peg:
        if peg < 1:
            reasons.append(f"PEG ({peg:.2f}) below 1 - growth at reasonable price")
        elif peg > 2:
            reasons.append(f"PEG ({peg:.2f}) above 2 - growth may be expensive")

    val["assessment"] = assessment
    val["reasons"] = reasons

    return val


def _calculate_quality_score(quote: Dict, financials: Optional[Dict]) -> Dict:
    """
    Calculate fundamental quality score (each category out of 10).
    Transparent scoring.
    """
    scores = {}

    # 1. Business Quality (10 pts)
    biz_score = 5  # baseline
    if quote.get("description"):
        biz_score += 1
    if quote.get("sector") and quote.get("industry"):
        biz_score += 1
    market_cap = quote.get("market_cap", 0)
    if market_cap and market_cap > 1e11:
        biz_score += 2  # Large cap
    elif market_cap and market_cap > 1e10:
        biz_score += 1
    if quote.get("employees") and quote["employees"] > 10000:
        biz_score += 1
    scores["business_quality"] = min(10, biz_score)

    # 2. Growth (10 pts)
    growth_score = 3
    rev_growth = quote.get("revenue_growth")
    if rev_growth:
        if rev_growth > 0.2:
            growth_score += 3
        elif rev_growth > 0.1:
            growth_score += 2
        elif rev_growth > 0:
            growth_score += 1
    eps = quote.get("trailing_eps")
    fwd_eps = quote.get("forward_eps")
    if eps and fwd_eps and fwd_eps > eps:
        growth_score += 2
    scores["growth"] = min(10, growth_score)

    # 3. Profitability (10 pts)
    profit_score = 3
    margins = quote.get("profit_margins")
    if margins:
        if margins > 0.2:
            profit_score += 3
        elif margins > 0.1:
            profit_score += 2
        elif margins > 0:
            profit_score += 1
    roe = quote.get("return_on_equity")
    if roe:
        if roe > 0.2:
            profit_score += 2
        elif roe > 0.1:
            profit_score += 1
    if quote.get("operating_margins") and quote["operating_margins"] > 0.15:
        profit_score += 1
    scores["profitability"] = min(10, profit_score)

    # 4. Balance Sheet (10 pts)
    bs_score = 5
    de = quote.get("debt_to_equity")
    if de is not None:
        if de < 50:
            bs_score += 2
        elif de < 100:
            bs_score += 1
        elif de > 200:
            bs_score -= 2
    cash = quote.get("total_cash")
    debt = quote.get("total_debt")
    if cash and debt:
        net = cash - debt
        if net > 0:
            bs_score += 2
        elif net > -debt * 0.1:
            bs_score += 1
    cr = quote.get("current_ratio")
    if cr:
        if cr > 1.5:
            bs_score += 1
        elif cr < 0.8:
            bs_score -= 1
    scores["balance_sheet"] = max(0, min(10, bs_score))

    # 5. Valuation (10 pts)
    val_score = 5
    pe = quote.get("pe_ratio")
    if pe:
        if pe < 15:
            val_score += 3
        elif pe < 25:
            val_score += 1
        elif pe > 50:
            val_score -= 2
    pb = quote.get("price_to_book")
    if pb:
        if pb < 2:
            val_score += 1
        elif pb > 8:
            val_score -= 1
    scores["valuation"] = max(0, min(10, val_score))

    # 6. Management / Shareholding (10 pts)
    mgmt_score = 5
    insider = quote.get("insider_ownership")
    inst = quote.get("institutional_ownership")
    if inst:
        if inst > 0.5:
            mgmt_score += 2  # Strong institutional backing
        elif inst > 0.3:
            mgmt_score += 1
    if insider:
        if insider > 0.1:
            mgmt_score += 1  # Skin in the game
    if quote.get("website"):
        mgmt_score += 1
    scores["management_shareholding"] = min(10, mgmt_score)

    # Overall score
    total = sum(scores.values())
    overall = total / 6  # Average of 6 categories

    scores["overall"] = round(overall, 1)
    scores["total"] = total
    scores["out_of"] = 60
    scores["explanation"] = _score_explanation(scores)

    return scores


def _score_explanation(scores: Dict) -> str:
    """Explain how the score was calculated."""
    lines = []
    for key, val in scores.items():
        if key in ("overall", "total", "out_of", "explanation"):
            continue
        label = key.replace("_", " ").title()
        bar = "█" * int(val) + "░" * (10 - int(val))
        lines.append(f"  {label}: {bar} {val}/10")
    lines.append(f"\n  Overall: {scores['total']}/60 = {scores['overall']}/10")
    return "\n".join(lines)


def _analyze_growth(quote: Dict, financials: Optional[Dict]) -> Dict:
    """Analyze growth metrics."""
    growth = {
        "revenue_growth": quote.get("revenue_growth"),
        "earnings_growth": None,
        "is_growing": False,
        "growth_quality": "Unknown",
    }

    rev_g = quote.get("revenue_growth")
    if rev_g is not None:
        growth["is_growing"] = rev_g > 0
        if rev_g > 0.25:
            growth["growth_quality"] = "High Growth"
        elif rev_g > 0.1:
            growth["growth_quality"] = "Moderate Growth"
        elif rev_g > 0:
            growth["growth_quality"] = "Slow Growth"
        elif rev_g > -0.1:
            growth["growth_quality"] = "Flat / Slight Decline"
        else:
            growth["growth_quality"] = "Declining"

    return growth


def _analyze_holdings(quote: Dict, holder_data: Optional[Dict]) -> Dict:
    """Analyze institutional and insider holdings."""
    holdings = {
        "insider_ownership": quote.get("insider_ownership"),
        "institutional_ownership": quote.get("institutional_ownership"),
        "assessment": "Data unavailable",
    }

    inst = quote.get("institutional_ownership")
    insider = quote.get("insider_ownership")

    if inst is not None:
        if inst > 0.7:
            holdings["assessment"] = "Strong institutional backing"
        elif inst > 0.5:
            holdings["assessment"] = "Good institutional interest"
        elif inst > 0.3:
            holdings["assessment"] = "Moderate institutional interest"
        else:
            holdings["assessment"] = "Low institutional interest"

    if insider is not None and insider > 0.2:
        holdings["assessment"] += " | Significant insider ownership"

    return holdings


def _generate_thesis(analysis: Dict) -> Dict:
    """Generate investment thesis from analysis."""
    quality = analysis.get("quality_score", {})
    valuation = analysis.get("valuation", {})
    growth = analysis.get("growth_analysis", {})

    overall_score = quality.get("overall", 5)
    val_assessment = valuation.get("assessment", "Unknown")
    growth_quality = growth.get("growth_quality", "Unknown")

    # Determine recommendation
    if overall_score >= 7:
        if "Undervalued" in val_assessment:
            thesis = "ATTRACTIVE"
            detail = "Strong fundamentals with reasonable valuation"
        elif "Overvalued" in val_assessment:
            thesis = "FAIR"
            detail = "Good fundamentals but valuation is stretched"
        else:
            thesis = "ATTRACTIVE"
            detail = "Strong overall fundamentals"
    elif overall_score >= 5:
        thesis = "FAIR"
        detail = "Average fundamentals, monitor key metrics"
    elif overall_score >= 3:
        thesis = "EXPENSIVE"
        detail = "Below average fundamentals or stretched valuation"
    else:
        thesis = "AVOID"
        detail = "Weak fundamentals or significantly overvalued"

    return {
        "thesis": thesis,
        "detail": detail,
        "strengths": _identify_strengths(analysis),
        "weaknesses": _identify_weaknesses(analysis),
    }


def _identify_strengths(analysis: Dict) -> list:
    strengths = []
    fund = analysis.get("fundamentals", {})
    quality = analysis.get("quality_score", {})

    if quality.get("profitability", 0) >= 7:
        strengths.append("Strong profitability metrics")
    if quality.get("growth", 0) >= 7:
        strengths.append("Strong growth profile")
    if quality.get("balance_sheet", 0) >= 7:
        strengths.append("Healthy balance sheet")
    if analysis.get("valuation", {}).get("assessment") == "Potentially Undervalued":
        strengths.append("Potentially undervalued")
    if quality.get("business_quality", 0) >= 7:
        strengths.append("Strong business quality")

    return strengths if strengths else ["No standout strengths identified"]


def _identify_weaknesses(analysis: Dict) -> list:
    weaknesses = []
    quality = analysis.get("quality_score", {})

    if quality.get("profitability", 10) < 5:
        weaknesses.append("Weak profitability")
    if quality.get("growth", 10) < 5:
        weaknesses.append("Weak growth profile")
    if quality.get("balance_sheet", 10) < 5:
        weaknesses.append("Weak balance sheet")
    if analysis.get("valuation", {}).get("assessment") == "Potentially Overvalued":
        weaknesses.append("Potentially overvalued")
    if analysis.get("fundamentals", {}).get("debt_to_equity"):
        de = analysis["fundamentals"]["debt_to_equity"]
        if isinstance(de, (int, float)) and de > 150:
            weaknesses.append("High debt levels")

    return weaknesses if weaknesses else ["No major weaknesses identified"]


def _fmt_value(val) -> str:
    if val is None:
        return "N/A"
    if isinstance(val, (int, float)):
        if abs(val) >= 1e12:
            return f"₹{val/1e12:.2f}T"
        elif abs(val) >= 1e9:
            return f"₹{val/1e9:.2f}B"
        elif abs(val) >= 1e7:
            return f"₹{val/1e7:.2f}Cr"
        elif abs(val) >= 1e5:
            return f"₹{val/1e5:.2f}L"
        return f"{val:,.2f}"
    return str(val)


def _fmt_pct(val) -> str:
    if val is None:
        return "N/A"
    if isinstance(val, (int, float)):
        return f"{val * 100:.2f}%"
    return str(val)
