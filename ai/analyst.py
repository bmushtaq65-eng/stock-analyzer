"""
AI Analysis Engine.
Synthesizes all collected data into evidence-based explanations.
Does NOT invent numbers - explains what the data shows.
"""
from typing import Dict, Any, List, Optional
import math


def generate_full_analysis(
    quote: Dict,
    indicators: Dict,
    sr_data: Dict,
    price_action: Dict,
    mtf_data: Dict,
    intraday_data: Dict,
    swing_data: Dict,
    longterm_data: Dict,
    risk_data: Dict,
    tech_score: Dict,
    news: List,
    timeframe: str = "swing",
) -> Dict[str, Any]:
    """
    Generate comprehensive AI analysis from all data sources.
    Every conclusion references underlying evidence.
    """
    current_price = quote.get("current_price", 0)

    result = {
        "dashboard": _generate_dashboard(quote, indicators, tech_score, longterm_data, risk_data, mtf_data),
        "what_happening": _what_is_happening(quote, indicators, price_action, mtf_data),
        "why_happening": _why_is_happening(indicators, price_action, news, mtf_data),
        "support_resistance_summary": _sr_summary(sr_data, current_price),
        "current_trend": _current_trend_analysis(mtf_data, indicators),
        "intraday_possibilities": _intraday_possibilities(intraday_data),
        "short_term_setup": _short_term_setup(swing_data, indicators),
        "long_term_case": _long_term_case(longterm_data, quote),
        "risks": _risk_summary(risk_data),
        "invalidation": _what_invalidates(tech_score, sr_data, indicators),
        "watch_next": _what_to_watch(indicators, sr_data, quote),
        "scenarios": _generate_scenarios(current_price, sr_data, indicators, tech_score),
        "signal_confidence": _signal_confidence(tech_score, longterm_data, intraday_data, swing_data),
        "quick_view": _quick_view(quote, tech_score, mtf_data, risk_data),
    }

    return result


def _generate_dashboard(quote, indicators, tech_score, longterm_data, risk_data, mtf_data) -> Dict:
    """Generate the top-level dashboard."""
    name = quote.get("name", "N/A")
    current_price = quote.get("current_price", "N/A")
    currency = quote.get("currency", "")

    # Overall trend from MTF
    mtf_overall = mtf_data.get("overall", {})
    overall_trend = mtf_overall.get("bias", "Neutral")

    # Technical score
    tech_val = tech_score.get("score", 50)
    tech_signal = tech_score.get("signal", "Neutral")

    # Fundamental score
    quality = longterm_data.get("quality_score", {})
    fund_score = quality.get("overall", 5)

    # Momentum from indicators
    momentum = "Neutral"
    if "rsi" in indicators:
        rsi = indicators["rsi"]
        if not _isnan(rsi):
            if rsi > 60:
                momentum = "Bullish"
            elif rsi < 40:
                momentum = "Bearish"

    # Volatility
    volatility = "Moderate"
    if "atr" in indicators and "close" in indicators:
        atr_pct = indicators["atr"] / indicators["close"] * 100 if indicators["close"] > 0 else 0
        if atr_pct > 3:
            volatility = "High"
        elif atr_pct < 1:
            volatility = "Low"

    # Risk
    risk_rating = risk_data.get("overall_rating", "MODERATE")

    # Market & Sector
    market_trend = "Data unavailable"
    sector_trend = "Data unavailable"

    # Timeframe-based conclusion
    intraday_signal = _intraday_signal(indicators, tech_score)
    short_term = "NEUTRAL"
    if tech_val >= 60:
        short_term = "BULLISH"
    elif tech_val <= 40:
        short_term = "BEARISH"

    long_term = longterm_data.get("investment_thesis", {}).get("thesis", "FAIR")

    return {
        "stock": f"{name} ({quote.get('symbol', 'N/A')})",
        "exchange": quote.get("exchange", "N/A"),
        "current_price": f"{currency}{current_price}",
        "overall_trend": overall_trend,
        "technical_score": f"{tech_val:.0f}/100 ({tech_signal})",
        "fundamental_score": f"{fund_score:.1f}/10",
        "momentum": momentum,
        "volatility": volatility,
        "risk": risk_rating,
        "market_trend": market_trend,
        "sector_trend": sector_trend,
        "intraday": intraday_signal,
        "short_term": short_term,
        "long_term": long_term,
    }


def _intraday_signal(indicators, tech_score) -> str:
    """Generate intraday signal based on rules."""
    score = tech_score.get("score", 50)
    rsi = indicators.get("rsi", 50)
    adx = indicators.get("adx", 20)

    if score >= 65 and not _isnan(rsi) and rsi < 70:
        if not _isnan(adx) and adx > 20:
            return "BUY (with confirmation)"
    elif score <= 35 and not _isnan(rsi) and rsi > 30:
        if not _isnan(adx) and adx > 20:
            return "SELL (with confirmation)"
    return "WAIT"


def _what_is_happening(quote, indicators, price_action, mtf_data) -> str:
    """What is happening with the stock right now."""
    parts = []

    current = quote.get("current_price", 0)
    prev_close = quote.get("previous_close")
    if current and prev_close:
        change_pct = (current - prev_close) / prev_close * 100
        direction = "up" if change_pct > 0 else "down"
        parts.append(f"The stock is currently trading at {current} ({direction} {abs(change_pct):.2f}% from previous close).")

    # Trend structure
    structure = price_action.get("trend_structure", {})
    trend = structure.get("trend", "")
    if trend and "Insufficient" not in trend:
        parts.append(f"Price structure shows: {trend}.")

    # Current momentum
    rsi = indicators.get("rsi")
    if rsi and not _isnan(rsi):
        if rsi > 70:
            parts.append(f"RSI at {rsi:.0f} indicates overbought conditions.")
        elif rsi < 30:
            parts.append(f"RSI at {rsi:.0f} indicates oversold conditions - potential bounce zone.")
        else:
            parts.append(f"RSI at {rsi:.0f} indicates {('bullish' if rsi > 55 else 'bearish' if rsi < 45 else 'neutral')} momentum.")

    # MTF
    overall = mtf_data.get("overall", {})
    if overall.get("bias"):
        alignment = overall.get("alignment", 0)
        parts.append(f"Multi-timeframe analysis shows {overall['bias'].lower()} bias with {alignment:.0f}% alignment across timeframes.")

    return " ".join(parts) if parts else "Analyzing current market conditions..."


def _why_is_happening(indicators, price_action, news, mtf_data) -> str:
    """Why is the stock moving the way it is."""
    parts = []

    # EMA alignment
    ema_20 = indicators.get("ema_20")
    ema_50 = indicators.get("ema_50")
    sma_200 = indicators.get("sma_200")
    close = indicators.get("close")

    if ema_20 and ema_50 and close:
        if close > ema_20 > ema_50:
            parts.append("Price is above both EMA20 and EMA50, confirming short-term bullish trend.")
        elif close < ema_20 < ema_50:
            parts.append("Price is below both EMA20 and EMA50, confirming short-term bearish trend.")

    if sma_200 and close:
        if close > sma_200:
            parts.append("Trading above the 200-period SMA, suggesting long-term uptrend is intact.")
        else:
            parts.append("Trading below the 200-period SMA, suggesting long-term downtrend.")

    # Supertrend
    st_dir = indicators.get("supertrend_direction")
    if st_dir is not None:
        if st_dir == 1:
            parts.append("Supertrend indicator is in bullish territory.")
        else:
            parts.append("Supertrend indicator is in bearish territory.")

    # MACD
    macd = indicators.get("macd")
    macd_signal = indicators.get("macd_signal")
    if macd and macd_signal:
        if macd > macd_signal:
            parts.append("MACD is above its signal line, indicating positive momentum.")
        else:
            parts.append("MACD is below its signal line, indicating negative momentum.")

    # News sentiment
    if news:
        pos = sum(1 for n in news if n.get("sentiment_hint") == "Positive")
        neg = sum(1 for n in news if n.get("sentiment_hint") == "Negative")
        if pos > neg:
            parts.append(f"Recent news flow is predominantly positive ({pos} positive vs {neg} negative stories).")
        elif neg > pos:
            parts.append(f"Recent news flow shows more negative sentiment ({neg} negative vs {pos} positive stories).")
        else:
            parts.append("Recent news sentiment is mixed.")

    return " ".join(parts) if parts else "Movement driven by market factors."


def _sr_summary(sr_data, current_price) -> str:
    """Summarize support and resistance levels."""
    parts = []

    resistances = sr_data.get("resistance_levels", [])
    supports = sr_data.get("support_levels", [])

    if resistances:
        parts.append("**Resistance Levels:**")
        for i, r in enumerate(resistances[:3], 1):
            parts.append(f"  R{i} — {r['price']} — {r.get('strength', 'N/A')} ({r.get('reason', '')})")

    if supports:
        parts.append("**Support Levels:**")
        for i, s in enumerate(supports[:3], 1):
            parts.append(f"  S{i} — {s['price']} — {s.get('strength', 'N/A')} ({s.get('reason', '')})")

    # Pivot points
    pivots = sr_data.get("pivot_points", {})
    if pivots:
        parts.append(f"\nPivot Point: {pivots.get('PP', 'N/A')}")

    return "\n".join(parts)


def _current_trend_analysis(mtf_data, indicators) -> str:
    """Detailed trend analysis."""
    parts = []
    timeframes = mtf_data.get("timeframes", {})

    for tf, data in timeframes.items():
        if data.get("bias") and data.get("bias") != "Neutral":
            conf = data.get("confidence", 50)
            parts.append(f"  {tf}: {data['bias']} (confidence: {conf}%)")

    overall = mtf_data.get("overall", {})
    if overall.get("detail"):
        parts.append(f"\nOverall: {overall.get('bias', 'Neutral')}")
        parts.append(f"Breakdown: {overall.get('detail', '')}")

    return "\n".join(parts) if parts else "Trend data not available."


def _intraday_possibilities(intraday_data) -> str:
    """Summarize intraday possibilities."""
    if not intraday_data or "error" in intraday_data:
        return "Intraday analysis unavailable."

    parts = []
    key = intraday_data.get("key_levels", {})
    momentum = intraday_data.get("momentum", {})
    scenarios = intraday_data.get("scenarios", {})

    parts.append(f"Current: {key.get('current_price', 'N/A')}")
    parts.append(f"Day Open: {key.get('day_open', 'N/A')}")
    parts.append(f"Prev Day High/Low: {key.get('prev_day_high', 'N/A')} / {key.get('prev_day_low', 'N/A')}")
    parts.append(f"VWAP: {key.get('vwap', 'N/A')}")
    parts.append(f"Gap: {key.get('gap_pct', 'N/A')}%")

    bull = scenarios.get("bullish", {})
    bear = scenarios.get("bearish", {})

    if bull:
        parts.append("\n**Bullish Scenario:**")
        parts.append(f"  Entry: {bull.get('entry_zone', 'N/A')}")
        parts.append(f"  SL: {bull.get('stop_loss', 'N/A')}")
        parts.append(f"  Targets: T1={bull.get('target_1', 'N/A')}, T2={bull.get('target_2', 'N/A')}, T3={bull.get('target_3', 'N/A')}")

    if bear:
        parts.append("\n**Bearish Scenario:**")
        parts.append(f"  Entry: {bear.get('entry_zone', 'N/A')}")
        parts.append(f"  SL: {bear.get('stop_loss', 'N/A')}")
        parts.append(f"  Targets: T1={bear.get('target_1', 'N/A')}, T2={bear.get('target_2', 'N/A')}, T3={bear.get('target_3', 'N/A')}")

    return "\n".join(parts)


def _short_term_setup(swing_data, indicators) -> str:
    """Short-term trading setup summary."""
    if not swing_data or "error" in swing_data:
        return "Swing analysis unavailable."

    parts = []
    parts.append(f"Trend: {swing_data.get('trend', 'N/A')}")
    parts.append(f"Momentum: {swing_data.get('momentum', 'N/A')}")
    parts.append(f"RSI: {swing_data.get('rsi', 'N/A')}")
    parts.append(f"Support: {swing_data.get('support', 'N/A')}")
    parts.append(f"Resistance: {swing_data.get('resistance', 'N/A')}")
    parts.append(f"Stop Loss: {swing_data.get('stop_loss', 'N/A')}")
    parts.append(f"Target 1: {swing_data.get('target_1', 'N/A')}")
    parts.append(f"Target 2: {swing_data.get('target_2', 'N/A')}")
    parts.append(f"Risk/Reward: 1:{swing_data.get('risk_reward', 'N/A')}")
    parts.append(f"Confidence: {swing_data.get('confidence', 'N/A')}%")

    confirms = swing_data.get("confirmations", [])
    if confirms:
        parts.append("\nConfirmations:")
        for c in confirms:
            parts.append(f"  {c}")

    return "\n".join(parts)


def _long_term_case(longterm_data, quote) -> str:
    """Long-term investment thesis."""
    if not longterm_data or "error" in longterm_data:
        return "Long-term analysis unavailable."

    thesis = longterm_data.get("investment_thesis", {})
    quality = longterm_data.get("quality_score", {})
    valuation = longterm_data.get("valuation", {})

    parts = []
    parts.append(f"Investment Thesis: **{thesis.get('thesis', 'N/A')}**")
    parts.append(f"Quality Score: {quality.get('overall', 'N/A')}/10")
    parts.append(f"Valuation: {valuation.get('assessment', 'N/A')}")

    strengths = thesis.get("strengths", [])
    weaknesses = thesis.get("weaknesses", [])

    if strengths:
        parts.append("\nStrengths:")
        for s in strengths:
            parts.append(f"  ✅ {s}")

    if weaknesses:
        parts.append("\nWeaknesses:")
        for w in weaknesses:
            parts.append(f"  ⚠ {w}")

    # Key ratios
    parts.append("\nKey Ratios:")
    for label, val in [
        ("P/E", quote.get("pe_ratio")),
        ("P/B", quote.get("price_to_book")),
        ("ROE", quote.get("return_on_equity")),
        ("Debt/Equity", quote.get("debt_to_equity")),
        ("Dividend Yield", quote.get("dividend_yield")),
    ]:
        if val is not None:
            fmt = f"{val*100:.1f}%" if "yield" in label.lower() or "ROE" in label else f"{val:.2f}"
            parts.append(f"  {label}: {fmt}")

    return "\n".join(parts)


def _risk_summary(risk_data) -> str:
    """Summarize risk factors."""
    if not risk_data:
        return "Risk data unavailable."

    parts = []
    parts.append(f"**Overall Risk: {risk_data.get('overall_rating', 'N/A')}** (Score: {risk_data.get('overall_score', 'N/A')}/10)")
    parts.append(f"Reasoning: {risk_data.get('explanation', 'N/A')}")

    risks = risk_data.get("individual_risks", {})
    for name, risk in risks.items():
        level = risk.get("level", "N/A")
        if level in ("HIGH", "VERY HIGH"):
            parts.append(f"  🔴 {name.replace('_', ' ').title()}: {level}")
        elif level == "MODERATE":
            parts.append(f"  🟡 {name.replace('_', ' ').title()}: {level}")
        else:
            parts.append(f"  🟢 {name.replace('_', ' ').title()}: {level}")

    return "\n".join(parts)


def _what_invalidates(tech_score, sr_data, indicators) -> str:
    """What would invalidate the current thesis."""
    parts = []
    score = tech_score.get("score", 50)
    close = indicators.get("close", 0)

    supports = sr_data.get("support_levels", [])
    resistances = sr_data.get("resistance_levels", [])

    if score >= 60:  # Currently bullish
        if supports:
            parts.append(f"A close below {supports[0]['price']} would invalidate the bullish setup.")
        parts.append("A bearish MACD crossover combined with RSI dropping below 40 would signal weakening momentum.")
        parts.append("Price breaking below the Supertrend would confirm trend reversal.")
    elif score <= 40:  # Currently bearish
        if resistances:
            parts.append(f"A close above {resistances[0]['price']} with volume would invalidate the bearish setup.")
        parts.append("A bullish MACD crossover with RSI rising above 50 would signal improving momentum.")
    else:
        parts.append("Currently neutral - watch for break above nearest resistance or below nearest support for direction.")

    return "\n".join(parts) if parts else "Monitor key technical levels for thesis changes."


def _what_to_watch(indicators, sr_data, quote) -> str:
    """What should the investor watch next."""
    parts = []

    rsi = indicators.get("rsi")
    if rsi and not _isnan(rsi):
        if rsi > 70:
            parts.append("Watch for RSI divergence or bearish candlestick pattern (potential pullback).")
        elif rsi < 30:
            parts.append("Watch for bullish reversal pattern or RSI divergence (potential bounce).")
        else:
            parts.append(f"RSI at {rsi:.0f} - monitor for overbought/oversold signals.")

    macd = indicators.get("macd")
    macd_signal = indicators.get("macd_signal")
    if macd and macd_signal:
        if abs(macd - macd_signal) / max(abs(macd), 1) < 0.1:
            parts.append("MACD approaching signal line - potential crossover incoming.")

    resistances = sr_data.get("resistance_levels", [])
    supports = sr_data.get("support_levels", [])
    if resistances:
        parts.append(f"Watch resistance at {resistances[0]['price']} for breakout.")
    if supports:
        parts.append(f"Watch support at {supports[0]['price']} for breakdown.")

    parts.append("Monitor volume for confirmation of any breakout/breakdown.")

    return "\n".join(parts) if parts else "Monitor key levels."


def _generate_scenarios(current_price, sr_data, indicators, tech_score) -> Dict:
    """Generate bull/base/bear scenarios."""
    supports = sr_data.get("support_levels", [])
    resistances = sr_data.get("resistance_levels", [])

    # Determine levels
    support_price = supports[0]["price"] if supports else current_price * 0.95
    resistance_price = resistances[0]["price"] if resistances else current_price * 1.05

    range_size = resistance_price - support_price

    bull_case = {
        "trigger": f"Break above {resistance_price} with volume expansion",
        "expected_zone": f"{resistance_price} to {resistance_price + range_size * 0.5}",
        "probability": "Scenario dependent on market conditions",
        "confirmation": f"Daily close above {resistance_price}",
        "invalidation": f"Price falls back below {resistance_price * 0.99}",
    }

    base_case = {
        "trigger": "Continuation of current range",
        "expected_zone": f"{support_price} to {resistance_price}",
        "probability": "Most likely scenario given current conditions",
        "confirmation": "Price remains within current range",
        "invalidation": "Breakout in either direction",
    }

    bear_case = {
        "trigger": f"Break below {support_price} with volume",
        "expected_zone": f"{support_price - range_size * 0.5} to {support_price}",
        "probability": "Scenario dependent on market conditions",
        "confirmation": f"Daily close below {support_price}",
        "invalidation": f"Price recovers above {support_price * 1.01}",
    }

    return {
        "bull": bull_case,
        "base": base_case,
        "bear": bear_case,
    }


def _signal_confidence(tech_score, longterm_data, intraday_data, swing_data) -> Dict:
    """Calculate confidence levels for various conclusions."""
    tech_val = tech_score.get("score", 50)
    quality = longterm_data.get("quality_score", {})
    fund_score = quality.get("overall", 5)

    # Technical confidence: based on signal clarity
    tech_conf = min(90, 30 + abs(tech_val - 50) * 1.2)

    # Fundamental confidence: based on data availability
    fund_conf = min(85, 40 + fund_score * 5) if fund_score > 0 else 30

    # Intraday confidence: lower (more noisy)
    intra_conf = min(75, 40 + abs(tech_val - 50) * 0.6)

    # Swing confidence
    swing_conf = min(80, 35 + abs(tech_val - 50) * 0.8)

    return {
        "technical_trend": round(tech_conf),
        "fundamental": round(fund_conf),
        "intraday_setup": round(intra_conf),
        "swing_setup": round(swing_conf),
    }


def _quick_view(quote, tech_score, mtf_data, risk_data) -> str:
    """30-second summary."""
    parts = []
    name = quote.get("name", "N/A")
    price = quote.get("current_price", "N/A")
    tech = tech_score.get("score", 50)
    trend = mtf_data.get("overall", {}).get("bias", "Neutral")
    risk = risk_data.get("overall_rating", "MODERATE")

    parts.append(f"**{name}** @ {price}")
    parts.append(f"Trend: {trend} | Technical: {tech:.0f}/100 | Risk: {risk}")

    if tech >= 65:
        parts.append("→ Short-term bias: Bullish. Look for pullback entries near support.")
    elif tech <= 35:
        parts.append("→ Short-term bias: Bearish. Wait for bottoming signals before entry.")
    else:
        parts.append("→ Short-term bias: Neutral. Wait for clearer signal.")

    return "\n".join(parts)


def _isnan(val) -> bool:
    """Check if value is NaN."""
    try:
        if val is None:
            return True
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return True
        return False
    except (TypeError, ValueError):
        return True
