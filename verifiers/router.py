from typing import Dict, Any
import logging
from .price_verifier import verify_price_hit
from .politics_verifier import verify_politics
from .sports_verifier import verify_sports
from .economics_verifier import verify_economics
import os
import openai
import json

logger = logging.getLogger(__name__)


def llm_fallback_verifier(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses OpenAI GPT-4o to check the prediction and return a verdict in the required format.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"""
You are a fact-checking assistant. Given the following structured prediction, check if it is correct using your knowledge and reasoning. Return ONLY a JSON object with the following keys:
- verdict: "true", "false", "not matured", or "unknown"
- confidence: a float between 0 and 1
- justification: a short explanation
- source: a URL or null

Prediction:
{json.dumps(prediction, indent=2)}

Return only the JSON object, nothing else.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful, precise fact-checking agent."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.2,
        )
        llm_output = response.choices[0].message.content.strip()
        # Try to extract JSON from the LLM output
        try:
            # If the LLM returns extra text, extract the first JSON object
            start = llm_output.find('{')
            end = llm_output.rfind('}') + 1
            json_str = llm_output[start:end]
            result = json.loads(json_str)
            # Validate keys
            for key in ["verdict", "confidence", "justification", "source"]:
                if key not in result:
                    raise ValueError(f"Missing key: {key}")
            # Type checks
            if result["verdict"] not in ["true", "false", "not matured", "unknown"]:
                result["verdict"] = "unknown"
            if not (0.0 <= float(result["confidence"]) <= 1.0):
                result["confidence"] = 0.5
            if not isinstance(result["justification"], str):
                result["justification"] = "LLM justification unavailable."
            if not (isinstance(result["source"], str) or result["source"] is None):
                result["source"] = None
            return result
        except Exception as parse_err:
            logger.error(f"Failed to parse LLM output: {llm_output}\nError: {parse_err}")
            return {
                "verdict": "unknown",
                "confidence": 0.5,
                "justification": "LLM fallback used, but output could not be parsed.",
                "source": "llm://gpt-4o"
            }
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return {
            "verdict": "unknown",
            "confidence": 0.5,
            "justification": f"LLM fallback failed: {str(e)}",
            "source": "llm://gpt-4o"
        }


def verify(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main router that dispatches predictions to the correct verifier.
    
    Args:
        prediction: Structured prediction object
        
    Returns:
        Verification result with verdict, confidence, justification, and source
    """
    try:
        context = prediction.get('context', '').lower()
        pred_type = prediction.get('type', '')
        
        # Route based on context
        if context in ['crypto', 'stocks', 'trading']:
            return verify_price_hit(prediction)
        elif context in ['politics', 'election', 'government']:
            return verify_politics(prediction)
        elif context in ['sports', 'football', 'basketball', 'soccer']:
            return verify_sports(prediction)
        elif context in ['economics', 'cpi', 'gdp', 'employment']:
            return verify_economics(prediction)
        else:
            # Fallback based on subject/predicate patterns
            subject = prediction.get('subject', '').lower()
            if any(asset in subject for asset in ['btc', 'bitcoin', 'eth', 'ethereum', 'stock', 'price']):
                return verify_price_hit(prediction)
            elif any(pol in subject for pol in ['biden', 'trump', 'election', 'president']):
                return verify_politics(prediction)
            elif any(sport in subject for sport in ['arsenal', 'liverpool', 'team', 'match']):
                return verify_sports(prediction)
            else:
                # Final fallback: LLM API
                return llm_fallback_verifier(prediction)
                
    except Exception as e:
        logger.error(f"Error in verification router: {e}")
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "justification": f"Verification failed: {str(e)}",
            "source": None
        } 