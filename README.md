# Modular Verifier System

A modular system for verifying structured predictions from web content using specialist agents.

## Overview

This system takes structured prediction objects and routes them to appropriate verifiers based on context and content type. Each verifier is a standalone module that can be used independently or as part of the routing system.

## Architecture

```
verifiers/
├── __init__.py          # Package exports
├── router.py            # Main routing logic
├── price_verifier.py    # Asset price verification (CoinGecko)
├── politics_verifier.py # Election result verification
├── sports_verifier.py   # Sports match verification
└── economics_verifier.py # Economic indicator verification
```

## Usage

### Using the Router (Recommended)

```python
from verifiers import verify

prediction = {
    "type": "binary",
    "subject": "Bitcoin",
    "predicate": ">",
    "object": 70000,
    "deadline": "2025-06-30T23:59:59Z",
    "context": "crypto"
}

result = verify(prediction)
# Returns: {"verdict": "true", "confidence": 0.95, ...}
```

### Using Individual Verifiers

```python
from verifiers.price_verifier import verify_price_hit
from verifiers.politics_verifier import verify_politics

# Use price verifier directly
result = verify_price_hit(prediction)

# Use politics verifier directly
result = verify_politics(prediction)
```

## Prediction Format

All verifiers expect predictions in this structured format:

```json
{
  "type": "binary" | "numeric" | "trend" | "ranking",
  "subject": "Entity name (e.g., Bitcoin, Biden)",
  "predicate": "Comparison operator (e.g., >, <, wins, beats)",
  "object": "Target value or entity",
  "deadline": "RFC3339 timestamp",
  "context": "Domain context (e.g., crypto, politics, sports)"
}
```

## Response Format

All verifiers return results in this format:

```json
{
  "verdict": "true" | "false" | "not matured" | "unknown",
  "confidence": 0.0-1.0,
  "justification": "Human-readable explanation",
  "source": "Data source URL or null"
}
```

## Implemented Verifiers

### ✅ Price-Hit Checker
- **File**: `verifiers/price_verifier.py`
- **Function**: `verify_price_hit()`
- **Data Source**: CoinGecko API
- **Supports**: BTC, ETH, ADA, SOL, DOT and more
- **Predicates**: `>`, `<`, `>=`, `<=`

### 🔄 Politics Checker (Placeholder)
- **File**: `verifiers/politics_verifier.py`
- **Function**: `verify_politics()`
- **Data Source**: TODO - Wikipedia/election APIs
- **Supports**: Election results

### 🔄 Sports Checker (Placeholder)
- **File**: `verifiers/sports_verifier.py`
- **Function**: `verify_sports()`
- **Data Source**: TODO - API-Football/TheSportsDB
- **Supports**: Match results

### 🔄 Economics Checker (Placeholder)
- **File**: `verifiers/economics_verifier.py`
- **Function**: `verify_economics()`
- **Data Source**: TODO - TradingEconomics/gov APIs
- **Supports**: CPI, GDP, NFP data

## Routing Logic

The router uses a hierarchical approach:

1. **Context-based routing**: Check `context` field first
2. **Subject-based fallback**: Analyze `subject` field for keywords
3. **Unknown handling**: Return "unknown" verdict if no verifier matches

### Context Mappings
- `crypto`, `stocks`, `trading` → Price verifier
- `politics`, `election`, `government` → Politics verifier
- `sports`, `football`, `basketball`, `soccer` → Sports verifier
- `economics`, `cpi`, `gdp`, `employment` → Economics verifier

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
# Test the full system
python3 start.py

# Test individual verifiers
python3 test_individual_verifiers.py
```

## Adding New Verifiers

1. Create a new file in `verifiers/` (e.g., `weather_verifier.py`)
2. Implement a function with signature: `verify_weather(prediction: Dict[str, Any]) -> Dict[str, Any]`
3. Add the import to `verifiers/__init__.py`
4. Add routing logic to `verifiers/router.py`

## Dependencies

- `requests`: HTTP API calls
- `python-dateutil`: Date parsing utilities

## License

MIT License 