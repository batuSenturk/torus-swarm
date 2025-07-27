from typing import Dict, Any
import logging
import requests
import os

logger = logging.getLogger(__name__)

TRADINGECONOMICS_API_URL = "https://api.tradingeconomics.com/historical/country/"
TRADINGECONOMICS_API_KEY = os.getenv("TRADINGECONOMICS_API_KEY", "guest:guest")  # Use demo key if not set


def verify_economics(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifies economic indicators like CPI, GDP, NFP for a country/region and time period using TradingEconomics API.
    Args:
        prediction: Structured prediction object
    Returns:
        Verification result
    """
    subject = prediction.get("subject", "")
    predicate = prediction.get("predicate", "")
    target_value = prediction.get("object", None)
    deadline = prediction.get("deadline", "")
    if not subject or not predicate or target_value is None or not deadline:
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": "Missing required fields for economics verification.",
            "source": None
        }
    # Parse country and indicator
    # Example: subject = "UK CPI" or "US GDP"
    try:
        parts = subject.split()
        if len(parts) < 2:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": "Subject should be in format '<Country> <Indicator>'",
                "source": None
            }
        country = parts[0]
        indicator = parts[1]
        # Map indicator to TradingEconomics format
        indicator_map = {"CPI": "consumer price index cpi", "GDP": "gdp", "NFP": "non farm payrolls"}
        indicator_query = indicator_map.get(indicator.upper(), indicator.lower())
        # Query TradingEconomics
        url = f"{TRADINGECONOMICS_API_URL}{country}/{indicator_query}"
        params = {"c": TRADINGECONOMICS_API_KEY}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": f"No data found for {subject}.",
                "source": None
            }
        # Find the latest value before the deadline
        from datetime import datetime
        deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        best = None
        for entry in data:
            try:
                date_dt = datetime.fromisoformat(entry["DateTime"][:19])
                if date_dt <= deadline_dt:
                    if best is None or date_dt > best["date_dt"]:
                        best = {"value": entry["Value"], "date_dt": date_dt, "date": entry["DateTime"]}
            except Exception:
                continue
        if not best:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": f"No data before deadline for {subject}.",
                "source": url
            }
        # Compare value
        value = best["value"]
        if predicate == ">":
            hit = value > target_value
        elif predicate == "<":
            hit = value < target_value
        elif predicate == ">=":
            hit = value >= target_value
        elif predicate == "<=":
            hit = value <= target_value
        else:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": f"Unsupported predicate: {predicate}",
                "source": url
            }
        verdict = "true" if hit else "false"
        return {
            "verdict": verdict,
            "confidence": 0.9,
            "justification": f"{subject} {predicate} {target_value}: value was {value} on {best['date']}",
            "source": url
        }
    except Exception as e:
        logger.error(f"Economics verifier failed: {e}")
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": f"Economics verifier error: {str(e)}",
            "source": None
        } 