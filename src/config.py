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
