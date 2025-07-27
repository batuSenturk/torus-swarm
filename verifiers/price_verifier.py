import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def verify_price_hit(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifies if an asset crossed a threshold before a deadline.
    
    Args:
        prediction: Structured prediction object
        
    Returns:
        Verification result with verdict, confidence, justification, and source
    """
    try:
        subject = prediction.get('subject', '')
        predicate = prediction.get('predicate', '')
        target_value = prediction.get('object')
        deadline = prediction.get('deadline')
        
        if not all([subject, predicate, target_value, deadline]):
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": "Missing required fields for price verification",
                "source": None
            }
        
        # Parse deadline
        if not deadline:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": "Missing deadline",
                "source": None
            }
        
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        except:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": "Invalid deadline format",
                "source": None
            }
        
        # Check if prediction has matured
        now = datetime.now(timezone.utc)
        if now < deadline_dt:
            return {
                "verdict": "not matured",
                "confidence": 1.0,
                "justification": f"Prediction deadline {deadline} has not passed yet",
                "source": None
            }
        
        # Get asset price data from CoinGecko
        price_data = _get_asset_price_data(subject, deadline_dt)
        
        if not price_data:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": f"Could not fetch price data for {subject}",
                "source": None
            }
        
        # Check if threshold was crossed
        max_price = price_data.get('max_price', 0)
        min_price = price_data.get('min_price', float('inf'))
        
        if predicate == '>':
            hit = max_price > target_value
            comparison = f"max price {max_price} vs target {target_value}"
        elif predicate == '<':
            hit = min_price < target_value
            comparison = f"min price {min_price} vs target {target_value}"
        elif predicate == '>=':
            hit = max_price >= target_value
            comparison = f"max price {max_price} vs target {target_value}"
        elif predicate == '<=':
            hit = min_price <= target_value
            comparison = f"min price {min_price} vs target {target_value}"
        else:
            return {
                "verdict": "unknown",
                "confidence": 0.0,
                "justification": f"Unsupported predicate: {predicate}",
                "source": None
            }
        
        verdict = "true" if hit else "false"
        confidence = 0.95 if price_data.get('reliable_data') else 0.7
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "justification": f"{subject} {predicate} {target_value}: {comparison}",
            "source": price_data.get('source_url')
        }
        
    except Exception as e:
        logger.error(f"Error in price verification: {e}")
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": f"Price verification failed: {str(e)}",
            "source": None
        }


def _get_asset_price_data(subject: str, deadline: datetime) -> Optional[Dict[str, Any]]:
    """
    Fetches historical price data for an asset from CoinGecko.
    
    Args:
        subject: Asset name/symbol
        deadline: Deadline datetime
        
    Returns:
        Price data dictionary or None if failed
    """
    try:
        # Map common asset names to CoinGecko IDs
        asset_mapping = {
            'bitcoin': 'bitcoin',
            'btc': 'bitcoin',
            'ethereum': 'ethereum',
            'eth': 'ethereum',
            'cardano': 'cardano',
            'ada': 'cardano',
            'solana': 'solana',
            'sol': 'solana',
            'polkadot': 'polkadot',
            'dot': 'polkadot'
        }
        
        # Clean and map subject
        subject_clean = subject.lower().strip()
        coin_id = asset_mapping.get(subject_clean, subject_clean)
        
        # Calculate date range (30 days before deadline to deadline)
        from_date = deadline - timedelta(days=30)
        
        # CoinGecko API endpoint for historical data
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
        params = {
            'vs_currency': 'usd',
            'from': int(from_date.timestamp()),
            'to': int(deadline.timestamp())
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        prices = data.get('prices', [])
        
        if not prices:
            return None
        
        # Extract price data
        price_values = [price[1] for price in prices]
        max_price = max(price_values)
        min_price = min(price_values)
        
        return {
            'max_price': max_price,
            'min_price': min_price,
            'reliable_data': len(prices) > 10,  # Consider reliable if we have >10 data points
            'source_url': f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
        }
        
    except requests.RequestException as e:
        logger.error(f"API request failed for {subject}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching price data for {subject}: {e}")
        return None 