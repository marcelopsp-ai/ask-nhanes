# 🏥 ASK NHANES

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.20-orange.svg)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema de **Perguntas e Respostas (Q&A)** sobre dados de saúde pública usando **RAG (Retrieval-Augmented Generation)**.

## 🎯 O que é?

ASK NHANES permite fazer perguntas em linguagem natural sobre:

- 📊 **Dados NHANES 2015-2016** - IMC, peso, altura por grupos demográficos
- 📈 **Estatística** - Regressão linear, pressupostos, testes de hipótese
- 🏥 **Saúde Pública** - Obesidade, epidemiologia, metodologia NHANES

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+
- [Gemini API Key](https://aistudio.google.com/app/apikey) (gratuita)

### Instalação

```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/ask-nhanes.git
cd ask-nhanes

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar API Key
export GEMINI_API_KEY="sua_chave_aqui"
```

### Uso

**CLI Interativo:**
```bash
python3 ask_nhanes.py
```

**Single Query:**
```bash
python3 ask_nhanes.py "Qual o IMC médio por faixa etária?"
```

**REST API:**
```bash
python3 start_api.py
# Acesse: http://localhost:8000/docs
```

## 📖 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Info da API |
| GET | `/health` | Health check |
| GET | `/stats` | Estatísticas do sistema |
| GET | `/api/sources` | Lista fontes da knowledge base |
| POST | `/api/ask` | **Fazer pergunta** |
| GET | `/docs` | Swagger UI |

### Exemplo de Request

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual o IMC médio por faixa etária?", "k": 3}'
```

### Exemplo de Response

```json
{
  "answer": "De acordo com os dados do NHANES 2015-2016...",
  "sources": ["imc_por_idade.txt", "resumo_geral.txt"],
  "num_sources": 2,
  "processing_time": 2.34
}
```

## 🏗️ Arquitetura

```
User Question
     │
     ▼
┌─────────────┐
│  FastAPI    │ ◄── REST API
└─────┬───────┘
      │
      ▼
┌─────────────┐
│ RAG Pipeline│
├─────────────┤
│ 1. Embed    │ ◄── HuggingFace (FREE)
│ 2. Search   │ ◄── ChromaDB
│ 3. Generate │ ◄── Gemini (FREE)
└─────────────┘
      │
      ▼
┌─────────────┐
│  Knowledge  │ ◄── 23 documentos
│    Base     │     ~200 chunks
└─────────────┘
```

## 📁 Estrutura do Projeto

```
ask-nhanes/
├── ask_nhanes.py          # CLI interface
├── start_api.py           # API server
├── test_api.py            # API tests
├── requirements.txt       # Dependências
├── Dockerfile             # Container
├── docker-compose.yml     # Orquestração
├── data/
│   ├── knowledge_base/    # 23 documentos
│   │   ├── conceitos/     # Estatística
│   │   ├── estatisticas/  # Stats do CSV
│   │   ├── papers/        # Resumos acadêmicos
│   │   └── wikipedia/     # Artigos
│   └── chroma_db/         # Vector store
├── src/
│   ├── document_loader.py # Carrega docs
│   ├── text_splitter.py   # Divide em chunks
│   ├── embeddings.py      # HuggingFace
│   ├── vector_store.py    # ChromaDB
│   ├── llm_service.py     # Gemini
│   ├── rag_pipeline.py    # Pipeline completo
│   └── api_service.py     # FastAPI
└── scripts/
    └── build_knowledge_base.py
```

## 🐳 Docker

```bash
# Build
docker build -t ask-nhanes .

# Run
docker run -p 8000:8000 -e GEMINI_API_KEY="sua_chave" ask-nhanes

# Ou com docker-compose
docker-compose up
```

## 📊 Knowledge Base

| Categoria | Docs | Conteúdo |
|-----------|------|----------|
| Wikipedia | 11 | NHANES, IMC, Obesity, Regressão |
| Papers | 4 | Metodologia, Prevalência, Testes |
| Conceitos | 4 | Tendência central, Dispersão, Pressupostos |
| Estatísticas | 4 | IMC/idade, Peso/sexo, Correlações |
| **Total** | **23** | ~200 chunks indexados |

## 💰 Custo

| Componente | Alternativa Paga | Esta Solução | Economia |
|------------|------------------|--------------|----------|
| Embeddings | OpenAI ($0.02/1M) | HuggingFace | **FREE** |
| LLM | GPT-4 ($0.03/1K) | Gemini | **FREE** |
| Vector DB | Pinecone ($$) | ChromaDB | **FREE** |
| **Total** | ~$50-100/mês | **$0.00** | **100%** |

## 🛠️ Tecnologias

- **Python 3.12** - Linguagem
- **LangChain** - Framework RAG
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embeddings
- **Google Gemini** - LLM
- **FastAPI** - REST API
- **Docker** - Containerização

## 📝 Exemplos de Perguntas

```
❓ Qual o IMC médio por faixa etária?
❓ Quais são os pressupostos da regressão linear?
❓ O que é o NHANES?
❓ Como interpretar o R²?
❓ Qual a diferença entre média e mediana?
❓ O que é homoscedasticidade?
❓ Como detectar outliers?
```

## 🎓 Contexto

Este projeto foi desenvolvido como parte do **MBA em Data Science** da Faculdade Impacta, demonstrando:

1. **RAG Architecture** - Retrieval-Augmented Generation
2. **API Development** - REST com FastAPI
3. **Zero-Cost ML** - Soluções gratuitas para produção
4. **Health Data Analysis** - Análise de dados NHANES

## 📄 License

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 👤 Autor

**Marcelo Souza**
- GitHub: [@marcelopsp-ai](https://github.com/marcelopsp-ai)
- LinkedIn: [marcelopsp](https://linkedin.com/in/marcelopsp)

---

⭐ Se este projeto foi útil, deixe uma estrela!
