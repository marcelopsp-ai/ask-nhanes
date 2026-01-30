"""
Vector Store - ChromaDB para armazenamento e busca
"""

from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma


class VectorStoreService:
    """Gerencia o ChromaDB vector store"""
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.vectorstore = None
    
    def create_vectorstore(self, chunks: List[Document], embeddings) -> Chroma:
        """Cria novo vector store a partir dos chunks"""
        print(f"⏳ Creating vector store with {len(chunks)} chunks...")
        
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(self.persist_dir)
        )
        
        print(f"✅ Vector store created and persisted")
        return self.vectorstore
    
    def load_vectorstore(self, embeddings) -> Chroma:
        """Carrega vector store existente"""
        print(f"⏳ Loading vector store from {self.persist_dir}...")
        
        self.vectorstore = Chroma(
            persist_directory=str(self.persist_dir),
            embedding_function=embeddings
        )
        
        print(f"✅ Vector store loaded")
        return self.vectorstore
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Busca semântica por documentos similares"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 3):
        """Busca com scores de similaridade"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results


if __name__ == "__main__":
    from document_loader import KnowledgeBaseLoader
    from text_splitter import DocumentSplitter
    from embeddings import EmbeddingService
    
    # Carregar e processar documentos
    loader = KnowledgeBaseLoader()
    docs = loader.load_documents()
    
    splitter = DocumentSplitter()
    chunks = splitter.split_documents(docs)
    
    # Criar embeddings e vector store
    emb_service = EmbeddingService()
    embeddings = emb_service.get_embeddings()
    
    vs_service = VectorStoreService()
    vs_service.create_vectorstore(chunks, embeddings)
    
    # Testar busca
    print("\n🔍 Testing search...")
    results = vs_service.similarity_search("Qual o IMC médio?", k=3)
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content: {doc.page_content[:200]}...")