"""
LLM Service - Integração com Google Gemini (FREE)
"""

import google.generativeai as genai
from typing import List, Optional


class GeminiService:
    """Serviço de LLM usando Google Gemini"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Listar modelos disponíveis e usar o primeiro
        models = [m.name for m in genai.list_models() 
                  if 'generateContent' in m.supported_generation_methods]
        
        self.model_name = models[0] if models else "gemini-1.5-flash"
        self.model = genai.GenerativeModel(self.model_name.replace('models/', ''))
        
        print(f"✅ Gemini initialized: {self.model_name}")
    
    def generate_response(self, query: str, context: str) -> str:
        """Gera resposta usando o contexto fornecido"""
        
        prompt = f"""Você é um assistente especializado em análise de dados de saúde NHANES e estatística.

Use APENAS o contexto fornecido para responder à pergunta.
Se a informação não estiver no contexto, diga "Não encontrei essa informação na base de conhecimento."

Responda em português de forma clara e objetiva.

CONTEXTO:
{context}

PERGUNTA: {query}

RESPOSTA:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erro ao gerar resposta: {e}"
    
    def generate_response_with_sources(self, query: str, documents: List) -> dict:
        """Gera resposta e retorna com as fontes usadas"""
        
        # Montar contexto a partir dos documentos
        context_parts = []
        sources = []
        
        for i, doc in enumerate(documents):
            source = doc.metadata.get('source', 'Unknown')
            context_parts.append(f"[Fonte {i+1}]: {doc.page_content}")
            sources.append(source)
        
        context = "\n\n".join(context_parts)
        
        answer = self.generate_response(query, context)
        
        return {
            "answer": answer,
            "sources": list(set(sources)),
            "num_sources": len(documents)
        }


if __name__ == "__main__":
    import os
    
    # Testar com API key
    api_key = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
    
    service = GeminiService(api_key)
    
    # Teste simples
    response = service.generate_response(
        query="O que é IMC?",
        context="IMC (Índice de Massa Corporal) é calculado dividindo o peso em kg pela altura em metros ao quadrado."
    )
    print(f"\nResposta: {response}")