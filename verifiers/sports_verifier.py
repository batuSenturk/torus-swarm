from typing import Dict, Any
import logging
import requests

logger = logging.getLogger(__name__)

THESPORTSDB_API_URL = "https://www.thesportsdb.com/api/v1/json/3/"


def verify_sports(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifies if one team beat another on a specific date using TheSportsDB API.
    Args:
        prediction: Structured prediction object
    Returns:
        Verification result
    """
    subject = prediction.get("subject", "")
    obj = prediction.get("object", "")
    deadline = prediction.get("deadline", "")
    if not subject or not obj or not deadline:
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": "Missing team names or date.",
            "source": None
        }
    # Parse date (YYYY-MM-DD)
    date_str = deadline[:10]
    try:
        # We'll use English Premier League as an example (id=4328)
        # In production, map teams to leagues dynamically
        url = f"{THESPORTSDB_API_URL}eventsday.php"
        params = {"d": date_str, "l": "English Premier League"}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        events = data.get("events", [])
        for event in events:
            home = event.get("strHomeTeam", "").lower()
            away = event.get("strAwayTeam", "").lower()
            if subject.lower() in [home, away] and obj.lower() in [home, away]:
                home_score = int(event.get("intHomeScore", -1))
                away_score = int(event.get("intAwayScore", -1))
                if home_score == -1 or away_score == -1:
                    continue
                if subject.lower() == home and home_score > away_score:
                    return {
                        "verdict": "true",
                        "confidence": 0.9,
                        "justification": f"{subject} beat {obj} on {date_str} ({home_score}-{away_score}).",
                        "source": event.get("strEventThumb") or None
                    }
                elif subject.lower() == away and away_score > home_score:
                    return {
                        "verdict": "true",
                        "confidence": 0.9,
                        "justification": f"{subject} beat {obj} on {date_str} ({away_score}-{home_score}).",
                        "source": event.get("strEventThumb") or None
                    }
                else:
                    return {
                        "verdict": "false",
                        "confidence": 0.8,
                        "justification": f"{subject} did not beat {obj} on {date_str} (score: {home_score}-{away_score}).",
                        "source": event.get("strEventThumb") or None
                    }
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": f"No match found for {subject} vs {obj} on {date_str}.",
            "source": None
        }
    except Exception as e:
        logger.error(f"Sports verifier failed: {e}")
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": f"Sports verifier error: {str(e)}",
            "source": None
        } 