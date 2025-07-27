# Torus - Prediction Verification System

A Python system that verifies whether predictions came true by checking real-world data from various APIs.

## What it does

Takes predictions like "Bitcoin will be above $70,000 by June 2025" and tells you if they happened by querying CoinGecko, Wikipedia, sports APIs, and economic data sources.

## Quick start

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
# Returns: {"verdict": "true", "confidence": 0.95, "justification": "...", "source": "..."}
```

## Supported prediction types

- **Crypto/Stocks**: Price thresholds using CoinGecko API
- **Politics**: Election results using Wikipedia 
- **Sports**: Match outcomes using TheSportsDB
- **Economics**: GDP, CPI data using TradingEconomics

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
python start.py
```

## Project structure

```
verifiers/
├── router.py            # Routes predictions to right verifier
├── price_verifier.py    # Checks crypto/stock prices
├── politics_verifier.py # Checks election results  
├── sports_verifier.py   # Checks match outcomes
└── economics_verifier.py # Checks economic indicators
```

The system automatically routes predictions based on context keywords, with fallback logic for edge cases. 
