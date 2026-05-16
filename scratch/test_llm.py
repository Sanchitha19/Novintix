import requests
import json
import time

# Fetch token first
token_response = requests.post("http://localhost:8000/token", json={"username": "johnd", "password": "m38mzuvjxl"})
token = token_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

queries = [
    "Where is my order ORD-5?",
    "Where is my order?",
    "I want a refund for order ORD-3",
    "I want to refund Rs.8000 for order ORD-2",
    "I could not place an order from my account",
    "What is your return policy?",
    "Tell me about the mens casual slim fit shirt",
    "This is absolutely terrible I am very angry and want to speak to a manager immediately"
]

print("Starting Verification Tests...\n")

for i, q in enumerate(queries, 1):
    payload = {
        "user_id": "user_001",
        "session_id": "test_session_123",
        "text": q
    }
    print(f"Test {i}: {q}")
    start = time.time()
    try:
        url = "http://localhost:8000/query"
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        print(f"Agent: {data[0]['agent_name']}")
        print(f"Response: {data[0]['response_text']}\n")
    except Exception as e:
        print(f"Error: {e}\n")
