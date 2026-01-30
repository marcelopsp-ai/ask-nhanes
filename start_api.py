#!/usr/bin/env python3
"""
ASK NHANES - Iniciar servidor API
"""

import os
import sys

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         🏥 ASK NHANES - REST API Server 🏥                ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERRO: GEMINI_API_KEY não configurada!")
        print("   Execute: export GEMINI_API_KEY='sua_chave'")
        sys.exit(1)
    
    print("🚀 Iniciando servidor...")
    print("📖 Swagger UI: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("🔗 API: http://localhost:8000/api/ask")
    print("")
    
    uvicorn.run(
        "api_service:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

if __name__ == "__main__":
    main()
