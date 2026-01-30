# ASK NHANES - Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src/
COPY data/knowledge_base/ ./data/knowledge_base/
COPY ask_nhanes.py .
COPY start_api.py .

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["python3", "start_api.py"]
