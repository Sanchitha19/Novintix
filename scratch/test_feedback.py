import requests
import json

# Fetch token
token_response = requests.post("http://localhost:8000/token", json={"username": "johnd", "password": "m38mzuvjxl"})
token = token_response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
  "query_id": "test-trace-001",
  "rating": 1,
  "comment": "Wrong response given"
}

print("Testing Feedback Endpoint...")
response = requests.post("http://localhost:8000/feedback", headers=headers, json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("PASS: Feedback endpoint returned 200 OK")
else:
    print("FAIL: Feedback endpoint failed")
