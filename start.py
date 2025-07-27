import logging
from verifiers import verify

# Configure logging
logging.basicConfig(level=logging.INFO)

# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_predictions = [
        {
            "type": "binary",
            "subject": "Bitcoin",
            "predicate": ">",
            "object": 70000,
            "deadline": "2025-06-30T23:59:59Z",
            "context": "crypto"
        },
        {
            "type": "binary",
            "subject": "BTC",
            "predicate": "<",
            "object": 50000,
            "deadline": "2024-12-31T23:59:59Z",
            "context": "crypto"
        },
        {
            "type": "binary",
            "subject": "Ethereum",
            "predicate": ">",
            "object": 4000,
            "deadline": "2025-01-15T23:59:59Z",
            "context": "crypto"
        },
        {
            "type": "binary",
            "subject": "Biden",
            "predicate": "wins",
            "object": "2024 US election",
            "deadline": "2024-11-05T23:59:59Z",
            "context": "politics"
        },
        {
            "type": "binary",
            "subject": "Arsenal",
            "predicate": "beats",
            "object": "Liverpool",
            "deadline": "2025-03-03T23:59:59Z",
            "context": "sports"
        }
    ]
    
    print("Testing Modular Verifier System")
    print("=" * 50)
    
    for i, prediction in enumerate(test_predictions, 1):
        print(f"\nTest {i}:")
        print(f"Prediction: {prediction['subject']} {prediction['predicate']} {prediction['object']}")
        print(f"Context: {prediction['context']}")
        result = verify(prediction)
        print(f"Result: {result}")
