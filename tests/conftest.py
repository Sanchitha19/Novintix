import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

@pytest.fixture(autouse=True)
def mock_external_apis():
    with patch("agents.tracking_agent.FakeStoreClient") as mock_tracking, \
         patch("agents.refund_agent.FakeStoreClient") as mock_refund, \
         patch("agents.faq_agent.FakeStoreClient") as mock_faq, \
         patch("agents.faq_agent.HybridRetriever") as mock_retriever, \
         patch("rag.retriever.HuggingFaceEmbeddings") as mock_hf, \
         patch("rag.retriever.Chroma") as mock_chroma, \
         patch("rag.retriever.BM25Retriever") as mock_bm25:
        
        # Mock HF Embeddings
        mock_hf.return_value.embed_query = MagicMock(return_value=[0.1]*384)
        mock_hf.return_value.embed_documents = MagicMock(return_value=[[0.1]*384])
        
        # Setup common mock behavior
        inst_tracking = mock_tracking.return_value
        inst_refund = mock_refund.return_value
        inst_faq = mock_faq.return_value
        
        # Tracking Agent Mocks
        inst_tracking.get_user_carts = AsyncMock(return_value=[
            {"id": 123, "userId": 1, "date": "2026-05-10T12:00:00Z", "products": []},
            {"id": 1, "userId": 1, "date": "2026-05-10T12:00:00Z", "products": []},
            {"id": 5, "userId": 1, "date": "2026-05-10T12:00:00Z", "products": []}
        ])
        inst_tracking.get_products = AsyncMock(return_value=[])
        inst_tracking.map_cart_to_order = MagicMock(side_effect=lambda c, p: {
            "order_id": f"ORD-{c['id']}", 
            "status": "In Transit" if c['id'] != 123 else "Delivered", 
            "eta": datetime.utcnow() + timedelta(days=2), 
            "created_at": datetime.utcnow() - timedelta(days=2), 
            "total_amount": 2000 if c['id'] != 456 else 6000,
            "payment_method": "UPI"
        })

        # Refund Agent Mocks
        inst_refund.get_user_carts = AsyncMock(return_value=[
            {"id": 123, "userId": 1, "date": "2026-05-10T12:00:00Z", "products": []},
            {"id": 456, "userId": 1, "date": "2026-05-10T12:00:00Z", "products": []}
        ])
        inst_refund.get_products = AsyncMock(return_value=[])
        inst_refund.map_cart_to_order = MagicMock(side_effect=lambda c, p: {
            "order_id": f"ORD-{c['id']}", 
            "status": "Delivered", 
            "total_amount": 2000 if c['id'] == 123 else 6000, 
            "payment_method": "Card", 
            "created_at": datetime.utcnow() - timedelta(days=2),
            "eta": datetime.utcnow()
        })

        # Mock FAQ/RAG
        inst_retriever = mock_retriever.return_value
        inst_retriever.search = AsyncMock(return_value=[{"text": "Our return policy allows returns within 30 days.", "score": 0.9}])

        yield
