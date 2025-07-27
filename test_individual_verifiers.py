#!/usr/bin/env python3
"""
Test individual verifiers to demonstrate modular usage.
"""

from verifiers.price_verifier import verify_price_hit
from verifiers.politics_verifier import verify_politics
from verifiers.sports_verifier import verify_sports
from verifiers.economics_verifier import verify_economics
from verifiers.accuracy_scorer import update_accuracy, get_accuracy, reset_accuracy

def test_price_verifier():
    prediction = {
        "type": "binary",
        "subject": "Bitcoin",
        "predicate": ">",
        "object": 70000,
        "deadline": "2025-06-30T23:59:59Z",
        "context": "crypto"
    }
    result = verify_price_hit(prediction)
    print(f"Price verifier result: {result}")
    return result

def test_politics_verifier():
    prediction = {
        "type": "binary",
        "subject": "Joe Biden",
        "predicate": "wins",
        "object": "2020 United States presidential",
        "deadline": "2020-11-04T23:59:59Z",
        "context": "politics"
    }
    result = verify_politics(prediction)
    print(f"Politics verifier result: {result}")
    return result

def test_sports_verifier():
    prediction = {
        "type": "binary",
        "subject": "Arsenal",
        "predicate": "beats",
        "object": "Liverpool",
        "deadline": "2023-04-09T23:59:59Z",
        "context": "sports"
    }
    result = verify_sports(prediction)
    print(f"Sports verifier result: {result}")
    return result

def test_economics_verifier():
    prediction = {
        "type": "binary",
        "subject": "US GDP",
        "predicate": ">",
        "object": 20000,
        "deadline": "2022-12-31T23:59:59Z",
        "context": "economics"
    }
    result = verify_economics(prediction)
    print(f"Economics verifier result: {result}")
    return result

def test_accuracy_scorer():
    reset_accuracy()
    update_accuracy("alice", "US-politics", True)
    update_accuracy("alice", "US-politics", True)
    update_accuracy("alice", "US-politics", False)
    stats = get_accuracy("alice", "US-politics")
    print(f"Accuracy scorer result: {stats}")
    return stats

if __name__ == "__main__":
    print("Testing Individual Verifiers")
    print("=" * 40)
    print("\n1. Testing Price Verifier:")
    test_price_verifier()
    print("\n2. Testing Politics Verifier:")
    test_politics_verifier()
    print("\n3. Testing Sports Verifier:")
    test_sports_verifier()
    print("\n4. Testing Economics Verifier:")
    test_economics_verifier()
    print("\n5. Testing Accuracy Scorer:")
    test_accuracy_scorer() 