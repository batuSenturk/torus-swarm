from typing import Dict, Any
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# In-memory stats: {predictor: {domain: [correct, total]}}
_accuracy_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))


def update_accuracy(predictor: str, domain: str, correct: bool):
    """
    Update the rolling stats for a predictor in a domain.
    """
    stats = _accuracy_stats[predictor][domain]
    stats[1] += 1
    if correct:
        stats[0] += 1


def get_accuracy(predictor: str, domain: str) -> Dict[str, Any]:
    """
    Get the rolling accuracy stats for a predictor in a domain.
    """
    stats = _accuracy_stats[predictor][domain]
    correct, total = stats
    percent = (correct / total) * 100 if total > 0 else 0.0
    return {
        "predictor": predictor,
        "domain": domain,
        "correct": correct,
        "total": total,
        "percent": percent,
        "justification": f"{correct} / {total} correct in {domain}" if total > 0 else "No predictions yet."
    }


def reset_accuracy():
    """
    Reset all accuracy stats (for testing/demo).
    """
    _accuracy_stats.clear() 