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
