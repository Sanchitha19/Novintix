from integrations.fakestore_client import FakeStoreClient
import asyncio

async def test_circuit_breaker():
    client = FakeStoreClient()
    client.failure_threshold = 3
    client.recovery_timeout = 30
    
    # Simulate 3 failures
    for i in range(3):
        await client._handle_failure()
        print(f'Failure {i+1} recorded')

    # Check circuit is open
    assert client.circuit_open == True, 'FAIL: Circuit should be open after 3 failures'
    print('PASS: Circuit breaker opened after 3 failures')

    # Verify requests are blocked
    try:
        await client._check_circuit()
        print('FAIL: Should block requests when circuit is open')
    except Exception as e:
        if "FakeStoreAPI Circuit is open" in str(e):
            print('PASS: Circuit breaker blocking requests correctly')
        else:
            print('FAIL: Wrong exception raised')

asyncio.run(test_circuit_breaker())
