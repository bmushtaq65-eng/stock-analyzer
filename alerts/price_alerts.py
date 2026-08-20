"""
Price Alert System.
Checks for price crossing key support/resistance levels.
"""
from typing import Dict, Any, List


def check_price_alerts(
    current_price: float,
    sr_data: Dict,
    quote: Dict = None,
) -> List[Dict]:
    """Check if current price is near key levels."""
    alerts = []

    if not current_price or current_price <= 0:
        return alerts

    # Check resistance levels
    resistances = sr_data.get("resistance_levels", [])
    for r in resistances[:3]:
        level = r.get("price", 0)
        if level <= 0:
            continue
        dist = (level - current_price) / current_price * 100

        if dist < 0:
            alerts.append({
                "type": "Above Resistance",
                "severity": "Notable",
                "message": f"Price is above resistance at {level} — breakout zone",
                "level": level,
            })
        elif dist < 1:
            alerts.append({
                "type": "Near Resistance",
                "severity": "Watch",
                "message": f"Price is {dist:.1f}% below resistance at {level}",
                "level": level,
            })

    # Check support levels
    supports = sr_data.get("support_levels", [])
    for s in supports[:3]:
        level = s.get("price", 0)
        if level <= 0:
            continue
        dist = (current_price - level) / current_price * 100

        if dist < 0:
            alerts.append({
                "type": "Below Support",
                "severity": "Warning",
                "message": f"Price has broken below support at {level} — breakdown",
                "level": level,
            })
        elif dist < 1:
            alerts.append({
                "type": "Near Support",
                "severity": "Watch",
                "message": f"Price is {dist:.1f}% above support at {level}",
                "level": level,
            })

    # 52-week high/low
    prev_hl = sr_data.get("previous_highs_lows", {})
    if prev_hl.get("52w_high"):
        high = prev_hl["52w_high"]
        if current_price >= high * 0.98:
            alerts.append({
                "type": "Near 52-Week High",
                "severity": "Notable",
                "message": f"Trading near 52-week high of {high}",
                "level": high,
            })
    if prev_hl.get("52w_low"):
        low = prev_hl["52w_low"]
        if current_price <= low * 1.02:
            alerts.append({
                "type": "Near 52-Week Low",
                "severity": "Warning",
                "message": f"Trading near 52-week low of {low}",
                "level": low,
            })

    # Previous day high/low
    if prev_hl.get("prev_day_high"):
        pd_high = prev_hl["prev_day_high"]
        if current_price >= pd_high:
            alerts.append({
                "type": "Above Previous Day High",
                "severity": "Notable",
                "message": f"Trading above previous day high of {pd_high}",
                "level": pd_high,
            })
    if prev_hl.get("prev_day_low"):
        pd_low = prev_hl["prev_day_low"]
        if current_price <= pd_low:
            alerts.append({
                "type": "Below Previous Day Low",
                "severity": "Warning",
                "message": f"Trading below previous day low of {pd_low}",
                "level": pd_low,
            })

    return alerts
