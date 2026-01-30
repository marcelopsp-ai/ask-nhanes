#!/usr/bin/env python3
"""
ASK NHANES - Testar API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Testar health check"""
    print("🔍 Testing /health...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    return r.status_code == 200

def test_stats():
    """Testar stats"""
    print("\n🔍 Testing /stats...")
    r = requests.get(f"{BASE_URL}/stats")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    return r.status_code == 200

def test_sources():
    """Testar sources"""
    print("\n🔍 Testing /api/sources...")
    r = requests.get(f"{BASE_URL}/api/sources")
    print(f"   Status: {r.status_code}")
    print(f"   Total sources: {r.json()['total']}")
    return r.status_code == 200

def test_ask():
    """Testar pergunta"""
    print("\n🔍 Testing /api/ask...")
    
    questions = [
        "Qual o IMC médio por faixa etária?",
        "O que é o NHANES?",
        "Quais são os pressupostos da regressão linear?"
    ]
    
    for q in questions:
        print(f"\n   ❓ {q}")
        r = requests.post(
            f"{BASE_URL}/api/ask",
            json={"question": q, "k": 3}
        )
        if r.status_code == 200:
            data = r.json()
            print(f"   📝 {data['answer'][:200]}...")
            print(f"   📚 Fontes: {data['sources']}")
            print(f"   ⏱️ Tempo: {data['processing_time']}s")
        else:
            print(f"   ❌ Erro: {r.status_code}")
    
    return True

def main():
    print("="*50)
    print("🧪 ASK NHANES - API Tests")
    print("="*50)
    
    try:
        test_health()
        test_stats()
        test_sources()
        test_ask()
        
        print("\n" + "="*50)
        print("✅ Todos os testes passaram!")
        print("="*50)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: API não está rodando!")
        print("   Execute primeiro: python3 start_api.py")

if __name__ == "__main__":
    main()
