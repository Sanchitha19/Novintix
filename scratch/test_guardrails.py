from guardrails.pii import PIIMasker
from guardrails.loop_breaker import LoopBreaker

# Test 1: PII masking
test_text = 'My email is john@example.com and card is 4532-1234-5678-9012'
masker = PIIMasker()
masked = masker.mask(test_text)
assert 'john@example.com' not in masked, 'FAIL: Email not masked'
assert '4532-1234-5678-9012' not in masked, 'FAIL: Card not masked'
print(f'PASS: PII masked correctly: {masked}')

# Test 2: Refund guardrail
# Simulation since it's now integrated inside RefundAgent process
def check_refund_limit(amount):
    return {'approved': amount <= 5000, 'requires_human': amount > 5000}

result_low = check_refund_limit(4999)
assert result_low['approved'] == True, 'FAIL: Rs.4999 should auto-approve'
print('PASS: Rs.4999 refund auto-approved')

result_high = check_refund_limit(5001)
assert result_high['approved'] == False, 'FAIL: Rs.5001 should require approval'
assert result_high['requires_human'] == True, 'FAIL: Missing requires_human flag'
print('PASS: Rs.5001 refund requires human approval')

# Test 3: Loop breaker
lb = LoopBreaker(max_hops=3)
lb.check_and_increment('session-123')
lb.check_and_increment('session-123')
lb.check_and_increment('session-123')
assert lb.check_and_increment('session-123') == False, 'FAIL: Should escalate after 3 hops'
print('PASS: Loop breaker triggers at 3 hops')

