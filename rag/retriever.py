import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class HybridRetriever:
    def __init__(self, docs: List[Document] = [], persist_directory: str = "./data/chroma_db"):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = persist_directory
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
        
        if docs:
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            self.bm25_retriever = BM25Retriever.from_documents(docs)
        else:
            # Load from disk if exists
            if os.path.exists(self.persist_directory):
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                # BM25 needs docs to be re-initialized as it's not easily persistent in LC community
                # In prod, we'd store these docs in a DB or pickle them
                self.bm25_retriever = None 
            else:
                self.vectorstore = None
                self.bm25_retriever = None

    def get_ensemble_retriever(self, docs: List[Document]):
        """Create an ensemble retriever with RRF scoring."""
        vector_retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = 5
        
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.5, 0.5]
        )
        return ensemble_retriever

    async def search(self, query: str, docs: List[Document] = []) -> List[Dict[str, Any]]:
        """Perform hybrid search and return results with mock scores."""
        if not self.vectorstore and not docs:
            return []
            
        retriever = self.get_ensemble_retriever(docs)
        results = retriever.invoke(query)
        
        # Format results (adding mock confidence scores for now as EnsembleRetriever 
        # doesn't always expose raw RRF scores easily in this version)
        formatted_results = []
        for i, doc in enumerate(results):
            # Simulated score based on rank
            score = 0.9 - (i * 0.05) 
            formatted_results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            })
            
        return formatted_results
