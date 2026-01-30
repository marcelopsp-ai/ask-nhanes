"""
Embeddings usando Google Gemini API
SEM PyTorch - imagem Docker muito menor!
"""

import os
import google.generativeai as genai
from typing import List


class GeminiEmbeddings:
    """Embeddings via Gemini API (gratuito)"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada")
        
        genai.configure(api_key=api_key)
        self.model = "models/embedding-001"
        print(f"✅ Gemini Embeddings: {self.model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para documentos"""
        embeddings = []
        for text in texts:
            text = text[:2000] if len(text) > 2000 else text
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                print(f"⚠️ Embed error: {e}")
                embeddings.append([0.0] * 768)  # fallback
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Gera embedding para query"""
        text = text[:2000] if len(text) > 2000 else text
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']


class EmbeddingService:
    """Wrapper para compatibilidade"""
    
    def __init__(self, model_name: str = None):
        print("⏳ Initializing Gemini Embeddings...")
        self.embeddings = GeminiEmbeddings()
    
    def get_embeddings(self):
        return self.embeddings


if __name__ == "__main__":
    service = EmbeddingService()
    emb = service.get_embeddings()
    vec = emb.embed_query("O que é IMC?")
    print(f"Dimension: {len(vec)}")
