from rag.ingestion import PolicyIngestor
from rag.retriever import HybridRetriever

# Test ingestion
print('Testing RAG ingestion...')
ingestor = PolicyIngestor()
docs = ingestor.load_and_split()
print(f'PASS: Documents ingested. Loaded {len(docs)} chunks.')

# Test retrieval
retriever = HybridRetriever(docs=docs)

queries = [
    'cannot place order',
    'refund policy',
    'return items',
    'account suspended',
    'payment declined'
]

import asyncio

async def test_retrieval():
    for q in queries:
        results = await retriever.search(q)
        if len(results) == 0:
            print(f'FAIL: No results for query: {q}')
        else:
            top_score = results[0]["score"]
            print(f'PASS: \"{q}\" — top score: {top_score:.2f}, docs: {len(results)}')
            if top_score < 0.72:
                print(f'WARN: Score below threshold (0.72) — will escalate instead of answering')

asyncio.run(test_retrieval())
