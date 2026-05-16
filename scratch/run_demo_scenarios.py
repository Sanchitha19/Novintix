import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def run_demo():
    print("--- STEP 1: Health & Metrics ---")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            health = await client.get(f"{BASE_URL}/health")
            print(f"Health: {health.status_code} - {health.json()}")
            
            token_res = await client.post(f"{BASE_URL}/token")
            token = token_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print("\n--- STEP 3: Demo Scenarios ---")
            scenarios = [
                {"name": "Tracking - Single", "query": "Where is my order ORD-1?"},
                {"name": "Tracking - Delayed", "query": "Where is my package ORD-5?"},
                {"name": "Tracking - Multi (Recent)", "query": "I want to track my recent order"},
                {"name": "Refund - Below 5000", "query": "I want a refund for order ORD-1"},
                {"name": "Refund - Above 5000", "query": "Process a refund for ORD-15"},
                {"name": "FAQ - Product", "query": "Tell me about the Mens Casual Slim Fit shirt"},
                {"name": "FAQ - Policy", "query": "What is your return policy?"},
                {"name": "Guardrail - Loop", "query": "Hello", "repeat": 4}
            ]
            
            for s in scenarios:
                print(f"\n[Scenario: {s['name']}]")
                if s.get("repeat"):
                    for i in range(s["repeat"]):
                        res = await client.post(f"{BASE_URL}/query", json={"user_id": "user_001", "text": s["query"], "session_id": "loop_test"}, headers=headers)
                        if i == s["repeat"] - 1 or res.status_code != 200:
                            print(f"Result (Hop {i+1}): Status {res.status_code}")
                            print(f"Response: {res.text}")
                else:
                    res = await client.post(f"{BASE_URL}/query", json={"user_id": "user_001", "text": s["query"], "session_id": "demo_session"}, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        for r in data:
                            print(f"Agent [{r['agent_name']}]: {r['response_text']}")
                    else:
                        print(f"FAILED: {res.status_code} - {res.text}")

        except Exception as e:
            import traceback
            print(f"Exception: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_demo())
