"""
RAG Pipeline - Pipeline completo de Retrieval-Augmented Generation
"""

import os
from pathlib import Path
from typing import Optional

from document_loader import KnowledgeBaseLoader
from text_splitter import DocumentSplitter
from embeddings import EmbeddingService
from vector_store import VectorStoreService
from llm_service import GeminiService


class RAGPipeline:
    """Pipeline completo de RAG para Ask NHANES"""
    
    def __init__(
        self,
        knowledge_base_path: str = "data/knowledge_base",
        vector_store_path: str = "data/chroma_db",
        gemini_api_key: Optional[str] = None
    ):
        self.kb_path = knowledge_base_path
        self.vs_path = vector_store_path
        
        # API Key do Gemini
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não configurada!")
        
        # Inicializar serviços
        self.embedding_service = EmbeddingService()
        self.embeddings = self.embedding_service.get_embeddings()
        
        self.vector_store_service = VectorStoreService(vector_store_path)
        self.llm_service = GeminiService(self.api_key)
        
        # Carregar ou criar vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Carrega vector store existente ou cria novo"""
        chroma_path = Path(self.vs_path)
        
        if (chroma_path / "chroma.sqlite3").exists():
            print("📂 Loading existing vector store...")
            self.vector_store_service.load_vectorstore(self.embeddings)
        else:
            print("🔨 Building new vector store...")
            self._build_vector_store()
    
    def _build_vector_store(self):
        """Constrói vector store do zero"""
        # Carregar documentos
        loader = KnowledgeBaseLoader(self.kb_path)
        documents = loader.load_documents()
        
        # Dividir em chunks
        splitter = DocumentSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        
        # Criar vector store
        self.vector_store_service.create_vectorstore(chunks, self.embeddings)
    
    def rebuild_index(self):
        """Reconstrói o índice (útil após adicionar novos documentos)"""
        import shutil
        
        # Remover índice antigo
        chroma_path = Path(self.vs_path)
        if chroma_path.exists():
            shutil.rmtree(chroma_path)
        
        # Reconstruir
        self._build_vector_store()
        print("✅ Index rebuilt successfully!")
    
    def query(self, question: str, k: int = 3) -> dict:
        """
        Processa uma pergunta e retorna resposta com fontes
        
        Args:
            question: Pergunta do usuário
            k: Número de documentos a recuperar
        
        Returns:
            dict com answer, sources, e metadata
        """
        # 1. Buscar documentos relevantes
        documents = self.vector_store_service.similarity_search(question, k=k)
        
        if not documents:
            return {
                "answer": "Não encontrei documentos relevantes para sua pergunta.",
                "sources": [],
                "num_sources": 0
            }
        
        # 2. Gerar resposta com Gemini
        result = self.llm_service.generate_response_with_sources(question, documents)
        
        return result
    
    def query_with_scores(self, question: str, k: int = 3) -> dict:
        """Query com scores de similaridade"""
        results = self.vector_store_service.similarity_search_with_score(question, k=k)
        
        documents = [doc for doc, score in results]
        scores = [score for doc, score in results]
        
        response = self.llm_service.generate_response_with_sources(question, documents)
        response["scores"] = scores
        
        return response


def main():
    """Teste do pipeline"""
    print("\n" + "="*60)
    print("🚀 ASK NHANES - RAG Pipeline Test")
    print("="*60)
    
    # Inicializar pipeline
    pipeline = RAGPipeline()
    
    # Perguntas de teste
    questions = [
        "Qual o IMC médio por faixa etária?",
        "Quais são os pressupostos da regressão linear?",
        "O que é o NHANES?",
    ]
    
    for q in questions:
        print(f"\n❓ Pergunta: {q}")
        print("-" * 40)
        
        result = pipeline.query(q)
        
        print(f"📝 Resposta: {result['answer'][:500]}...")
        print(f"📚 Fontes: {result['sources']}")
        print()


if __name__ == "__main__":
    main()