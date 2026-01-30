#!/usr/bin/env python3
"""
ASK NHANES - CLI Interface
Sistema de Q&A sobre saúde pública NHANES
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rag_pipeline import RAGPipeline


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     █████╗ ███████╗██╗  ██╗    ███╗   ██╗██╗  ██╗         ║
║    ██╔══██╗██╔════╝██║ ██╔╝    ████╗  ██║██║  ██║         ║
║    ███████║███████╗█████╔╝     ██╔██╗ ██║███████║         ║
║    ██╔══██║╚════██║██╔═██╗     ██║╚██╗██║██╔══██║         ║
║    ██║  ██║███████║██║  ██╗    ██║ ╚████║██║  ██║         ║
║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═══╝╚═╝  ╚═╝         ║
║                                                           ║
║         🏥 NHANES Health Data Q&A System 🏥               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def main():
    print_banner()
    
    # Verificar API Key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERRO: GEMINI_API_KEY não configurada!")
        print("   Execute: export GEMINI_API_KEY='sua_chave'")
        sys.exit(1)
    
    print("⏳ Inicializando pipeline...")
    
    try:
        pipeline = RAGPipeline()
        print("✅ Pipeline pronto!\n")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        sys.exit(1)
    
    # Modo interativo ou single query
    if len(sys.argv) > 1:
        # Single query mode
        question = " ".join(sys.argv[1:])
        result = pipeline.query(question)
        print(f"\n📝 Resposta:\n{result['answer']}")
        print(f"\n📚 Fontes: {', '.join(result['sources'])}")
    else:
        # Interactive mode
        print("💡 Digite suas perguntas (ou 'sair' para encerrar)")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n❓ Pergunta: ").strip()
                
                if question.lower() in ['sair', 'exit', 'quit', 'q']:
                    print("\n👋 Até logo!")
                    break
                
                if not question:
                    continue
                
                print("⏳ Buscando...")
                result = pipeline.query(question)
                
                print(f"\n📝 Resposta:\n{result['answer']}")
                print(f"\n📚 Fontes: {', '.join(result['sources'])}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()