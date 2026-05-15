import pytest
import time
from recovery.circuit_breaker import CircuitBreaker

def test_circuit_breaker_open_circuit():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    
    def failing_func():
        raise Exception("API Down")

    # 3 failures
    for _ in range(3):
        with pytest.raises(Exception):
            cb.call(failing_func)
    
    assert cb.state == "OPEN"
    
    # 4th call should fail fast
    with pytest.raises(Exception) as excinfo:
        cb.call(failing_func)
    assert "Circuit breaker is OPEN" in str(excinfo.value)
    
    # Wait for recovery timeout
    time.sleep(1.1)
    
    # Should be HALF_OPEN
    def success_func():
        return "Success"
        
    result = cb.call(success_func)
    assert result == "Success"
    assert cb.state == "CLOSED"
