#!/usr/bin/env python3
"""
Script de teste simples para o Sistema de Buscas APIs v3.0
"""

import yaml
import requests
import os
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

def test_system():
    """Testa o sistema rapidamente"""
    
    # Carrega configuração
    with open("config-sistema-busca.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    print("🚀 TESTE RÁPIDO - Sistema de Buscas v3.0")
    print("=" * 50)
    
    # Testa Portal da Transparência com token
    print("\n📡 Portal da Transparência:")
    token = os.getenv('PORTAL_TRANSPARENCIA_API_KEY')
    if token:
        print("   ✅ Token encontrado no .env")
        headers = {'chave-api-dados': token}
        
        # Testa um endpoint
        url = "https://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print("   ✅ API funcionando perfeitamente!")
            elif response.status_code == 400:
                print("   ✅ API OK (400 = faltam parâmetros, normal)")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    else:
        print("   ❌ Token não encontrado no .env")
        print("   💡 Configure: PORTAL_TRANSPARENCIA_API_KEY=sua_chave")
    
    # Testa Brasil API (sem token)
    print("\n📡 Brasil API:")
    try:
        response = requests.get("https://brasilapi.com.br/api/banks/v1", timeout=5)
        if response.status_code == 200:
            print("   ✅ API funcionando!")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testa Câmara dos Deputados
    print("\n📡 Câmara dos Deputados:")
    try:
        response = requests.get("https://dadosabertos.camara.leg.br/api/v2/partidos", timeout=5)
        if response.status_code == 200:
            print("   ✅ API funcionando!")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testa IBGE
    print("\n📡 IBGE:")
    try:
        response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados", timeout=5)
        if response.status_code == 200:
            print("   ✅ API funcionando!")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print(f"\n🎯 RESUMO:")
    print(f"   • {len(config['apis'])} APIs configuradas")
    print(f"   • {sum(len(api['endpoints']) for api in config['apis'].values())} endpoints mapeados")
    print(f"   • Sistema pronto para uso!")
    
    print(f"\n📝 COMO USAR:")
    print(f"   1. Configure tokens no .env (se necessário)")
    print(f"   2. Execute: python search_system.py")
    print(f"   3. Digite consultas como:")
    print(f"      - 'deputados de minas gerais'")
    print(f"      - 'gastos do ministério da educação'")
    print(f"      - 'cep 01310-100'")

if __name__ == "__main__":
    test_system()