from typing import Dict, Any
import logging
import requests

logger = logging.getLogger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def verify_politics(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifies if a named candidate/entity won a specific election using Wikipedia.
    Args:
        prediction: Structured prediction object
    Returns:
        Verification result
    """
    subject = prediction.get("subject", "")
    obj = prediction.get("object", "")
    deadline = prediction.get("deadline", "")
    if not subject or not obj:
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": "Missing candidate or election name.",
            "source": None
        }
    # Try to find the Wikipedia page for the election
    try:
        search_query = obj + " election"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "format": "json"
        }
        resp = requests.get(WIKIPEDIA_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": f"No Wikipedia page found for election: {obj}",
                "source": None
            }
        # Use the first result
        page_title = search_results[0]["title"]
        page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
        # Get the page content
        params = {
            "action": "query",
            "prop": "extracts",
            "explaintext": True,
            "titles": page_title,
            "format": "json"
        }
        resp = requests.get(WIKIPEDIA_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        extract = next(iter(pages.values())).get("extract", "")
        # Check if the subject (candidate) is mentioned as the winner
        lower_extract = extract.lower()
        if subject.lower() in lower_extract and ("won" in lower_extract or "winner" in lower_extract):
            return {
                "verdict": "true",
                "confidence": 0.9,
                "justification": f"{subject} is listed as the winner in Wikipedia for {obj}.",
                "source": page_url
            }
        else:
            return {
                "verdict": "false",
                "confidence": 0.7,
                "justification": f"{subject} is not listed as the winner in Wikipedia for {obj}.",
                "source": page_url
            }
    except Exception as e:
        logger.error(f"Politics verifier failed: {e}")
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": f"Politics verifier error: {str(e)}",
            "source": None
        } 