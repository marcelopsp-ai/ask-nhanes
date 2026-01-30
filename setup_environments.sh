#!/bin/bash
# ASK NHANES - Setup Ambientes DEV e PROD
# Execute com: bash setup_environments.sh

echo "🚀 ASK NHANES - Setup DEV & PROD Environments"
echo "=============================================="

cd ~/ask-nhanes

# ============================================
# ARQUIVO: src/config.py
# ============================================
cat > src/config.py << 'ENDFILE'
"""
ASK NHANES - Configurações por Ambiente
"""

import os
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Ambiente
    ENVIRONMENT: Environment = Environment.DEV
    DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_WORKERS: int = 1
    
    # Gemini
    GEMINI_API_KEY: str = ""
    
    # RAG
    KNOWLEDGE_BASE_PATH: str = "data/knowledge_base"
    VECTOR_STORE_PATH: str = "data/chroma_db"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    RETRIEVAL_K: int = 3
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevSettings(Settings):
    """Configurações de Desenvolvimento"""
    ENVIRONMENT: Environment = Environment.DEV
    DEBUG: bool = True
    API_RELOAD: bool = True
    API_WORKERS: int = 1
    LOG_LEVEL: str = "DEBUG"


class ProdSettings(Settings):
    """Configurações de Produção"""
    ENVIRONMENT: Environment = Environment.PROD
    DEBUG: bool = False
    API_RELOAD: bool = False
    API_WORKERS: int = 4
    LOG_LEVEL: str = "WARNING"


class TestSettings(Settings):
    """Configurações de Teste"""
    ENVIRONMENT: Environment = Environment.TEST
    DEBUG: bool = True
    VECTOR_STORE_PATH: str = "data/chroma_db_test"
    LOG_LEVEL: str = "DEBUG"


@lru_cache()
def get_settings() -> Settings:
    """Retorna settings baseado no ambiente"""
    env = os.getenv("ENVIRONMENT", "dev").lower()
    
    settings_map = {
        "dev": DevSettings,
        "prod": ProdSettings,
        "test": TestSettings,
    }
    
    settings_class = settings_map.get(env, DevSettings)
    return settings_class()


# Instância global
settings = get_settings()


if __name__ == "__main__":
    s = get_settings()
    print(f"Environment: {s.ENVIRONMENT}")
    print(f"Debug: {s.DEBUG}")
    print(f"API Workers: {s.API_WORKERS}")
    print(f"Log Level: {s.LOG_LEVEL}")
ENDFILE
echo "✅ Created: src/config.py"

# ============================================
# ARQUIVO: .env.example
# ============================================
cat > .env.example << 'ENDFILE'
# ===========================================
# ASK NHANES - Environment Variables
# ===========================================
# Copie para .env e configure seus valores

# Ambiente: dev, prod, test
ENVIRONMENT=dev

# API Key do Gemini (obrigatório)
# Obtenha em: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_K=3

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Logging
LOG_LEVEL=INFO
ENDFILE
echo "✅ Created: .env.example"

# ============================================
# ARQUIVO: .env.dev
# ============================================
cat > .env.dev << 'ENDFILE'
# DEV Environment
ENVIRONMENT=dev
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_WORKERS=1
LOG_LEVEL=DEBUG
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_K=3
EMBEDDING_MODEL=all-MiniLM-L6-v2
# GEMINI_API_KEY=  # Set via export or .env
ENDFILE
echo "✅ Created: .env.dev"

# ============================================
# ARQUIVO: .env.prod
# ============================================
cat > .env.prod << 'ENDFILE'
# PROD Environment
ENVIRONMENT=prod
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_WORKERS=4
LOG_LEVEL=WARNING
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVAL_K=3
EMBEDDING_MODEL=all-MiniLM-L6-v2
# GEMINI_API_KEY=  # Set via secrets manager
ENDFILE
echo "✅ Created: .env.prod"

# ============================================
# ARQUIVO: docker-compose.dev.yml
# ============================================
cat > docker-compose.dev.yml << 'ENDFILE'
# Docker Compose - DEV Environment
version: '3.8'

services:
  ask-nhanes-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: ask-nhanes-dev
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=dev
      - DEBUG=true
      - API_RELOAD=true
      - LOG_LEVEL=DEBUG
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      # Hot reload - monta código local
      - ./src:/app/src
      - ./data/knowledge_base:/app/data/knowledge_base
      - ./data/chroma_db:/app/data/chroma_db
      - ./ask_nhanes.py:/app/ask_nhanes.py
      - ./start_api.py:/app/start_api.py
    restart: unless-stopped
    
  # Opcional: Adminer para debug
  # adminer:
  #   image: adminer
  #   ports:
  #     - "8080:8080"
ENDFILE
echo "✅ Created: docker-compose.dev.yml"

# ============================================
# ARQUIVO: docker-compose.prod.yml
# ============================================
cat > docker-compose.prod.yml << 'ENDFILE'
# Docker Compose - PROD Environment
version: '3.8'

services:
  ask-nhanes-prod:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: ask-nhanes-prod
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
      - DEBUG=false
      - API_RELOAD=false
      - API_WORKERS=4
      - LOG_LEVEL=WARNING
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      # Apenas dados persistentes
      - chroma_data:/app/data/chroma_db
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

volumes:
  chroma_data:
ENDFILE
echo "✅ Created: docker-compose.prod.yml"

# ============================================
# ARQUIVO: Dockerfile.dev
# ============================================
cat > Dockerfile.dev << 'ENDFILE'
# ASK NHANES - Dockerfile DEV
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código (será sobrescrito pelo volume em dev)
COPY src/ ./src/
COPY data/knowledge_base/ ./data/knowledge_base/
COPY ask_nhanes.py .
COPY start_api.py .

# Expor porta
EXPOSE 8000

# DEV: Com reload
CMD ["uvicorn", "src.api_service:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
ENDFILE
echo "✅ Created: Dockerfile.dev"

# ============================================
# ARQUIVO: Dockerfile.prod
# ============================================
cat > Dockerfile.prod << 'ENDFILE'
# ASK NHANES - Dockerfile PROD
FROM python:3.12-slim

WORKDIR /app

# Criar usuário não-root
RUN useradd -m -u 1000 appuser

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser data/knowledge_base/ ./data/knowledge_base/
COPY --chown=appuser:appuser ask_nhanes.py .
COPY --chown=appuser:appuser start_api.py .

# Criar diretório para chroma_db
RUN mkdir -p data/chroma_db && chown -R appuser:appuser data/

# Mudar para usuário não-root
USER appuser

# Expor porta
EXPOSE 8000

# PROD: Múltiplos workers, sem reload
CMD ["uvicorn", "src.api_service:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
ENDFILE
echo "✅ Created: Dockerfile.prod"

# ============================================
# ARQUIVO: Makefile
# ============================================
cat > Makefile << 'ENDFILE'
# ASK NHANES - Makefile
# Comandos úteis para DEV e PROD

.PHONY: help install dev prod test clean docker-dev docker-prod

# Cores
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help: ## Mostra esta ajuda
	@echo ''
	@echo '${GREEN}ASK NHANES - Comandos Disponíveis${RESET}'
	@echo ''
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-15s${RESET} %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ''

# ==================== LOCAL ====================

install: ## Instalar dependências
	pip install -r requirements.txt

dev: ## Rodar em modo DEV (local)
	@echo "🚀 Starting DEV server..."
	ENVIRONMENT=dev python3 start_api.py

prod-local: ## Rodar em modo PROD (local)
	@echo "🚀 Starting PROD server (local)..."
	ENVIRONMENT=prod uvicorn src.api_service:app --host 0.0.0.0 --port 8000 --workers 4

cli: ## Rodar CLI interativo
	python3 ask_nhanes.py

test: ## Rodar testes da API
	python3 test_api.py

# ==================== DOCKER ====================

docker-build-dev: ## Build imagem DEV
	docker build -f Dockerfile.dev -t ask-nhanes:dev .

docker-build-prod: ## Build imagem PROD
	docker build -f Dockerfile.prod -t ask-nhanes:prod .

docker-dev: ## Rodar container DEV
	docker-compose -f docker-compose.dev.yml up --build

docker-prod: ## Rodar container PROD
	docker-compose -f docker-compose.prod.yml up --build -d

docker-stop: ## Parar containers
	docker-compose -f docker-compose.dev.yml down
	docker-compose -f docker-compose.prod.yml down

docker-logs: ## Ver logs do container
	docker-compose -f docker-compose.prod.yml logs -f

# ==================== UTILS ====================

rebuild-index: ## Reconstruir índice vetorial
	@echo "🔨 Rebuilding vector index..."
	python3 -c "import sys; sys.path.insert(0,'src'); from rag_pipeline import RAGPipeline; p=RAGPipeline(); p.rebuild_index()"

build-kb: ## Reconstruir Knowledge Base
	python3 scripts/build_knowledge_base.py

clean: ## Limpar arquivos temporários
	rm -rf __pycache__ src/__pycache__
	rm -rf data/chroma_db
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete

status: ## Verificar status do sistema
	@echo "📊 ASK NHANES Status"
	@echo "===================="
	@echo "Environment: $${ENVIRONMENT:-dev}"
	@echo "Knowledge Base: $$(find data/knowledge_base -name '*.txt' | wc -l) docs"
	@echo "Vector Store: $$(du -sh data/chroma_db 2>/dev/null || echo 'Not built')"
	@echo "API Key: $$(if [ -n \"$$GEMINI_API_KEY\" ]; then echo 'Configured ✓'; else echo 'Not set ✗'; fi)"
ENDFILE
echo "✅ Created: Makefile"

# ============================================
# ARQUIVO: start_api.py (ATUALIZADO)
# ============================================
cat > start_api.py << 'ENDFILE'
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
ENDFILE
echo "✅ Updated: start_api.py"

# ============================================
# Instalar pydantic-settings
# ============================================
echo ""
echo "📦 Instalando pydantic-settings..."
pip install pydantic-settings --break-system-packages 2>/dev/null || pip install pydantic-settings

echo ""
echo "=============================================="
echo "✅ SETUP AMBIENTES COMPLETO!"
echo "=============================================="
echo ""
echo "📁 Arquivos criados:"
echo "   ✓ src/config.py (configurações)"
echo "   ✓ .env.example"
echo "   ✓ .env.dev"
echo "   ✓ .env.prod"
echo "   ✓ Dockerfile.dev"
echo "   ✓ Dockerfile.prod"
echo "   ✓ docker-compose.dev.yml"
echo "   ✓ docker-compose.prod.yml"
echo "   ✓ Makefile"
echo ""
echo "=============================================="
echo "🚀 COMO USAR"
echo "=============================================="
echo ""
echo "LOCAL DEV:"
echo "  export GEMINI_API_KEY='sua_chave'"
echo "  make dev"
echo ""
echo "LOCAL PROD:"
echo "  export GEMINI_API_KEY='sua_chave'"
echo "  make prod-local"
echo ""
echo "DOCKER DEV:"
echo "  export GEMINI_API_KEY='sua_chave'"
echo "  make docker-dev"
echo ""
echo "DOCKER PROD:"
echo "  export GEMINI_API_KEY='sua_chave'"
echo "  make docker-prod"
echo ""
echo "OUTROS COMANDOS:"
echo "  make help        # Ver todos os comandos"
echo "  make status      # Ver status do sistema"
echo "  make test        # Rodar testes"
echo "  make clean       # Limpar temporários"
echo ""
echo "=============================================="
echo "📊 DIFERENÇAS DEV vs PROD"
echo "=============================================="
echo ""
echo "| Aspecto      | DEV          | PROD         |"
echo "|--------------|--------------|--------------|"
echo "| Debug        | true         | false        |"
echo "| Reload       | true         | false        |"
echo "| Workers      | 1            | 4            |"
echo "| Log Level    | DEBUG        | WARNING      |"
echo "| Volume       | Hot reload   | Apenas dados |"
echo "| User         | root         | non-root     |"
echo "| Healthcheck  | Não          | Sim          |"
echo ""
