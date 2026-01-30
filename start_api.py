#!/usr/bin/env python3
"""
ASK NHANES - Iniciar servidor API (DEV/PROD aware)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn

def main():
    # Carregar configurações
    env = os.getenv("ENVIRONMENT", "dev").lower()
    is_prod = env == "prod"
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║         🏥 ASK NHANES - REST API Server 🏥                ║
║                                                           ║
║   Environment: {env.upper():^10}                              ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ ERRO: GEMINI_API_KEY não configurada!")
        print("   Execute: export GEMINI_API_KEY='sua_chave'")
        sys.exit(1)
    
    # Configurações por ambiente
    config = {
        "dev": {
            "host": "0.0.0.0",
            "port": 8000,
            "reload": True,
            "workers": 1,
            "log_level": "debug",
        },
        "prod": {
            "host": "0.0.0.0",
            "port": 8000,
            "reload": False,
            "workers": 4,
            "log_level": "warning",
        }
    }
    
    cfg = config.get(env, config["dev"])
    
    print(f"🚀 Starting server...")
    print(f"   Host: {cfg['host']}:{cfg['port']}")
    print(f"   Workers: {cfg['workers']}")
    print(f"   Reload: {cfg['reload']}")
    print(f"   Log Level: {cfg['log_level']}")
    print("")
    print(f"📖 Swagger UI: http://localhost:{cfg['port']}/docs")
    print(f"📖 ReDoc: http://localhost:{cfg['port']}/redoc")
    print("")
    
    uvicorn.run(
        "api_service:app",
        host=cfg["host"],
        port=cfg["port"],
        reload=cfg["reload"],
        workers=cfg["workers"] if not cfg["reload"] else 1,
        log_level=cfg["log_level"],
    )

if __name__ == "__main__":
    main()
