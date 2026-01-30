"""
Embeddings - HuggingFace Sentence Transformers (FREE)
"""

from langchain_community.embeddings import HuggingFaceEmbeddings


class EmbeddingService:
    """Serviço de embeddings usando HuggingFace (gratuito)"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"⏳ Loading embedding model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"✅ Embedding model loaded")
    
    def get_embeddings(self):
        """Retorna o objeto de embeddings para uso no ChromaDB"""
        return self.embeddings


if __name__ == "__main__":
    service = EmbeddingService()
    embeddings = service.get_embeddings()
    
    # Testar
    test_text = "O que é IMC?"
    vector = embeddings.embed_query(test_text)
    print(f"Vector dimension: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")