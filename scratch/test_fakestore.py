import asyncio
from integrations.fakestore_client import FakeStoreClient
from models.schemas import TraceContext

async def test():
    client = FakeStoreClient()
    dummy_trace = TraceContext()
    
    # Test 1: Get all products
    products = await client.get_products(dummy_trace)
    print(f'Products fetched: {len(products)}')
    assert len(products) > 0, 'FAIL: No products returned'
    print('PASS: Products API working')
    
    # Test 2: Get single product
    product = await client.get_product(1, dummy_trace)
    print(f'Product 1: {product["title"]}')
    assert product['id'] == 1, 'FAIL: Wrong product returned'
    print('PASS: Single product API working')
    
    # Test 3: Get all carts
    carts = await client.get_carts(dummy_trace)
    print(f'Carts fetched: {len(carts)}')
    assert len(carts) > 0, 'FAIL: No carts returned'
    print('PASS: Carts API working')
    
    # Test 4: Get user carts
    user_carts = await client.get_user_carts(1, dummy_trace)
    print(f'User 1 carts: {len(user_carts)}')
    print('PASS: User carts API working')
    
    # Test 5: Get all users
    users = await client.get_users(dummy_trace)

    print(f'Users fetched: {len(users)}')
    assert len(users) > 0, 'FAIL: No users returned'
    print('PASS: Users API working')

asyncio.run(test())
