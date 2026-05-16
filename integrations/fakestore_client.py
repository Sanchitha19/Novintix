import httpx
import redis.asyncio as redis
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models.schemas import TraceContext
from monitoring.metrics import FAKESTORE_API_LATENCY, FAKESTORE_API_FAILURES
import logging

logger = logging.getLogger(__name__)

class FakeStoreClient:
    BASE_URL = "https://fakestoreapi.com"
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", cache_ttl: int = 3600):
        try:
            self.redis = redis.from_url(redis_url)
            self.redis_available = True
        except Exception:
            self.redis = None
            self.redis_available = False
            logger.warning("Redis not available, caching disabled")
        self.cache_ttl = cache_ttl
        self.timeout = httpx.Timeout(10.0)
        self.mock_mode = True # Force mock mode for this environment demo
        self.circuit_open = False
        self.failure_count = 0
        self.failure_threshold = 5
        self.last_failure_time = 0
        self.recovery_timeout = 60 # 1 minute

    async def _check_circuit(self):
        if self.circuit_open:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.circuit_open = False
                self.failure_count = 0
                logger.info("FakeStoreAPI Circuit half-open, attempting recovery")
            else:
                raise Exception("FakeStoreAPI Circuit is open")

    async def _handle_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        FAKESTORE_API_FAILURES.inc()
        if self.failure_count >= self.failure_threshold:
            self.circuit_open = True
            logger.error("FakeStoreAPI Circuit opened due to multiple failures")

    async def _request(self, method: str, endpoint: str, trace_context: TraceContext, params: Optional[Dict] = None) -> Any:
        if self.mock_mode:
            # Return realistic mock data based on endpoint
            if "products" in endpoint:
                products = [{"id": 1, "title": "Mens Casual Slim Fit", "price": 15.99, "description": "The color could be slightly different between on the screen and in practice.", "category": "men's clothing", "image": ""},
                        {"id": 15, "title": "Expensive Jacket", "price": 5600.0, "description": "Luxury item", "category": "men's clothing", "image": ""}]
                if endpoint.startswith("/products/") and len(endpoint) > 10:
                    try:
                        pid = int(endpoint.split("/")[-1])
                        return next((p for p in products if p["id"] == pid), products[0])
                    except ValueError:
                        pass
                return products
            if "carts/user" in endpoint:
                return [{"id": 1, "userId": 1, "date": "2026-05-10T12:00:00Z", "products": [{"productId": 1, "quantity": 1}]},
                        {"id": 5, "userId": 1, "date": "2026-05-12T12:00:00Z", "products": [{"productId": 1, "quantity": 2}]},
                        {"id": 15, "userId": 1, "date": "2026-05-14T12:00:00Z", "products": [{"productId": 15, "quantity": 1}]}]
            if "carts" in endpoint:
                return [{"id": 1, "userId": 1, "date": "2026-05-10T12:00:00Z", "products": [{"productId": 1, "quantity": 1}]}]
            if "users" in endpoint:
                return [{"id": 1, "email": "john@gmail.com", "name": {"firstname": "John", "lastname": "Doe"}, "address": {"city": "Delhi", "street": "Main", "number": 12}, "phone": "123-456-7890"}]
            return {}

        await self._check_circuit()
        
        cache_key = f"fakestore:{endpoint}:{json.dumps(params) if params else ''}"
        if self.redis_available:
            try:
                cached_data = await self.redis.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception:
                self.redis_available = False
                logger.warning("Redis connection lost, switching to no-cache mode")

        headers = {
            "X-Trace-Id": trace_context.trace_id,
            "X-Span-Id": trace_context.span_id
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, f"{self.BASE_URL}{endpoint}", params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Sanitize response (basic example)
                if isinstance(data, dict):
                    data = {k: v for k, v in data.items() if v is not None}
                
                if self.redis_available:
                    try:
                        await self.redis.setex(cache_key, self.cache_ttl, json.dumps(data))
                    except Exception:
                        self.redis_available = False
                
                duration = time.time() - start_time
                FAKESTORE_API_LATENCY.observe(duration)
                
                return data
        except Exception as e:
            await self._handle_failure()
            logger.error(f"FakeStoreAPI Error: {str(e)}")
            raise e

    async def get_products(self, trace_context: TraceContext) -> List[Dict[str, Any]]:
        return await self._request("GET", "/products", trace_context)

    async def get_product(self, product_id: int, trace_context: TraceContext) -> Dict[str, Any]:
        return await self._request("GET", f"/products/{product_id}", trace_context)

    async def get_users(self, trace_context: TraceContext) -> List[Dict[str, Any]]:
        return await self._request("GET", "/users", trace_context)

    async def get_user(self, user_id: int, trace_context: TraceContext) -> Dict[str, Any]:
        return await self._request("GET", f"/users/{user_id}", trace_context)

    async def get_carts(self, trace_context: TraceContext) -> List[Dict[str, Any]]:
        return await self._request("GET", "/carts", trace_context)

    async def get_user_carts(self, user_id: int, trace_context: TraceContext) -> List[Dict[str, Any]]:
        return await self._request("GET", f"/carts/user/{user_id}", trace_context)

    # --- Mapping Utilities ---
    
    def map_product_to_catalog(self, product: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": f"PROD-{product['id']}",
            "name": product["title"],
            "description": product["description"],
            "price": product["price"],
            "category": product["category"],
            "image": product["image"]
        }

    def map_user_to_customer(self, user: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": f"CUST-{user['id']}",
            "name": f"{user['name']['firstname']} {user['name']['lastname']}",
            "email": user["email"],
            "phone": user["phone"],
            "address": f"{user['address']['number']} {user['address']['street']}, {user['address']['city']}"
        }

    def map_cart_to_order(self, cart: Dict[str, Any], products_map: Dict[int, Dict]) -> Dict[str, Any]:
        items = []
        total_amount = 0
        for item in cart["products"]:
            product = products_map.get(item["productId"], {})
            price = product.get("price", 0)
            items.append({
                "id": f"PROD-{item['productId']}",
                "quantity": item["quantity"],
                "price": price,
                "title": product.get("title", "Unknown Product")
            })
            total_amount += price * item["quantity"]

        # Synthetic order status and ETA
        statuses = ["Pending", "Processing", "In Transit", "Out for Delivery", "Delivered"]
        # Use cart ID to deterministicly pick a status for demo
        if cart["id"] == 1:
            status = "Delivered"
        else:
            status_idx = cart["id"] % len(statuses)
            status = statuses[status_idx]
        
        created_at = datetime.fromisoformat(cart["date"].replace("Z", "+00:00"))
        eta = created_at + timedelta(days=5)
        
        return {
            "order_id": f"ORD-{cart['id']}",
            "user_id": f"CUST-{cart['userId']}",
            "status": status,
            "items": items,
            "total_amount": total_amount,
            "created_at": created_at.isoformat(),
            "eta": eta.isoformat(),
            "tracking_id": f"TRK-FS-{cart['id']}{int(time.time()) % 1000}",
            "payment_method": "Card" if cart["id"] % 2 == 0 else "UPI"
        }
