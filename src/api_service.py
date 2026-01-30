"""
ASK NHANES - REST API com FastAPI
"""

import os
import sys
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Adicionar src ao path
sys.path.insert(0, os.path.dirname(__file__))

from rag_pipeline import RAGPipeline

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

class QuestionRequest(BaseModel):
    """Request para pergunta"""
    question: str = Field(..., min_length=3, max_length=500, description="Pergunta do usuário")
    k: int = Field(default=3, ge=1, le=10, description="Número de documentos a recuperar")

class AnswerResponse(BaseModel):
    """Response com resposta"""
    answer: str
    sources: list[str]
    num_sources: int
    processing_time: float

class HealthResponse(BaseModel):
    """Response do health check"""
    status: str
    timestamp: str
    version: str

class StatsResponse(BaseModel):
    """Response das estatísticas"""
    total_documents: int
    total_chunks: int
    embedding_model: str
    llm_model: str

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

app = FastAPI(
    title="ASK NHANES API",
    description="""
    🏥 Sistema de Q&A sobre dados de saúde NHANES
    
    Este sistema usa RAG (Retrieval-Augmented Generation) para responder
    perguntas sobre o dataset NHANES 2015-2016 e conceitos estatísticos.
    
    ## Funcionalidades
    
    * **Perguntas sobre NHANES** - IMC, peso, altura por grupos
    * **Conceitos estatísticos** - Regressão, pressupostos, testes
    * **Metodologia** - Como o NHANES coleta dados
    
    ## Exemplos de perguntas
    
    * "Qual o IMC médio por faixa etária?"
    * "Quais são os pressupostos da regressão linear?"
    * "O que é homoscedasticidade?"
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pipeline global (inicializado no startup)
pipeline: Optional[RAGPipeline] = None

@app.on_event("startup")
async def startup_event():
    """Inicializa o pipeline no startup"""
    global pipeline
    print("⏳ Inicializando RAG Pipeline...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERRO: GEMINI_API_KEY não configurada!")
        raise ValueError("GEMINI_API_KEY não configurada")
    
    pipeline = RAGPipeline(gemini_api_key=api_key)
    print("✅ Pipeline inicializado!")

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Informações da API"""
    return {
        "name": "ASK NHANES API",
        "version": "1.0.0",
        "description": "Sistema Q&A sobre dados de saúde NHANES",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check da API"""
    return HealthResponse(
        status="healthy" if pipeline else "initializing",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/stats", response_model=StatsResponse, tags=["Info"])
async def get_stats():
    """Estatísticas do sistema"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline não inicializado")
    
    return StatsResponse(
        total_documents=23,
        total_chunks=187,
        embedding_model="all-MiniLM-L6-v2",
        llm_model=pipeline.llm_service.model_name
    )

@app.post("/api/ask", response_model=AnswerResponse, tags=["Q&A"])
async def ask_question(request: QuestionRequest):
    """
    Faz uma pergunta ao sistema
    
    - **question**: Pergunta em português
    - **k**: Número de documentos a recuperar (1-10)
    
    Retorna a resposta com as fontes utilizadas.
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline não inicializado")
    
    import time
    start = time.time()
    
    try:
        result = pipeline.query(request.question, k=request.k)
        processing_time = time.time() - start
        
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"],
            num_sources=result["num_sources"],
            processing_time=round(processing_time, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources", tags=["Info"])
async def list_sources():
    """Lista todas as fontes disponíveis na knowledge base"""
    from pathlib import Path
    
    kb_path = Path("data/knowledge_base")
    sources = []
    
    for txt_file in kb_path.rglob("*.txt"):
        sources.append({
            "file": txt_file.name,
            "category": txt_file.parent.name,
            "path": str(txt_file)
        })
    
    return {
        "total": len(sources),
        "sources": sorted(sources, key=lambda x: x["category"])
    }

@app.post("/api/rebuild", tags=["Admin"])
async def rebuild_index():
    """Reconstrói o índice vetorial (usar após adicionar novos documentos)"""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline não inicializado")
    
    try:
        pipeline.rebuild_index()
        return {"status": "success", "message": "Índice reconstruído com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
