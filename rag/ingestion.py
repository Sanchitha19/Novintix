import os
import json
from typing import List
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class PolicyIngestor:
    def __init__(self, data_dir: str = "./data/policies"):
        self.data_dir = data_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50
        )

    def load_and_split(self) -> List[Document]:
        """Load documents from directory and split into chunks."""
        if not os.path.exists(self.data_dir):
            return []
            
        loader = DirectoryLoader(self.data_dir, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()
        
        chunks = self.text_splitter.split_documents(docs)
        print(f"DEBUG: Loaded {len(docs)} documents and created {len(chunks)} chunks.")
        return chunks

    def ingest_fakestore_products(self, products: List[dict]) -> List[Document]:
        """Convert FakeStore products into Documents for RAG ingestion."""
        docs = []
        for p in products:
            content = f"Product: {p['title']}\nCategory: {p['category']}\nDescription: {p['description']}\nPrice: ${p['price']}"
            metadata = {"source": "fakestore_api", "id": p["id"], "type": "product"}
            docs.append(Document(page_content=content, metadata=metadata))
        
        chunks = self.text_splitter.split_documents(docs)
        return chunks

    def update_delta(self, new_file_path: str):
        """Auto-versioning logic: only embed new/updated files."""
        # This would involve checking file hashes or timestamps against a registry
        # For now, we'll just re-index if called.
        pass
