from typing import Dict, Any
import logging
import requests
import re

logger = logging.getLogger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def extract_winner_from_text(text: str):
    """
    Try to extract the winner(s) of an election from Wikipedia text using common patterns.
    Returns a list of winner names (may be empty if not found).
    """
    text = text.lower()
    # Only use the first 2 paragraphs for precision
    summary = "\n".join(text.split("\n")[:4])
    # Patterns to match
    patterns = [
        r"([a-z .'-]+?) (?:won|was elected|prevailed|defeated|beat|received the most votes|was the winner|was victorious|secured victory|was chosen as president|was chosen president)",
        r"the winner (?:was|is) ([a-z .'-]+)",
        r"([a-z .'-]+?) (?:and [a-z .'-]+)? won the election",
        r"([a-z .'-]+?) (?:and [a-z .'-]+)? (?:defeated|beat) ([a-z .'-]+)"
    ]
    winners = set()
    for pat in patterns:
        for m in re.finditer(pat, summary):
            # Add all groups except the loser in defeated/beat pattern
            if len(m.groups()) == 2 and ("defeated" in pat or "beat" in pat):
                winners.add(m.group(1).strip())
            else:
                for g in m.groups():
                    winners.add(g.strip())
    # Remove empty/short matches
    winners = {w for w in winners if len(w) > 2}
    return list(winners)

def verify_politics(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifies if a named candidate/entity won a specific election using Wikipedia.
    Args:
        prediction: Structured prediction object
    Returns:
        Verification result
    """
    subject = prediction.get("subject", "").lower()
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
        lower_extract = extract.lower()
        winners = extract_winner_from_text(lower_extract)
        # Check for withdrawal
        withdrew = False
        for sentence in lower_extract.split('.'):
            if subject in sentence and any(word in sentence for word in ["withdrew", "dropped out", "suspended"]):
                withdrew = True
                break
        if withdrew:
            return {
                "verdict": "false",
                "confidence": 0.9,
                "justification": f"{prediction.get('subject')} withdrew or did not run in {obj}.",
                "source": page_url
            }
        # Check if subject is among the winners
        for winner in winners:
            if subject in winner:
                return {
                    "verdict": "true",
                    "confidence": 0.95,
                    "justification": f"{prediction.get('subject')} is listed as the winner in Wikipedia for {obj}.",
                    "source": page_url
                }
        # If another winner is found, return false and mention them
        if winners:
            return {
                "verdict": "false",
                "confidence": 0.95,
                "justification": f"{prediction.get('subject')} is not the winner. Winner(s): {', '.join(winners)}.",
                "source": page_url
            }
        # Fallback: unknown
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": f"Could not determine winner from Wikipedia for {obj}.",
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
