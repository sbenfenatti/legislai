import yaml
import requests
import csv
import os
from dotenv import load_dotenv  # Adicionar esta import

# CARREGAR VARIÁVEIS DO .env
load_dotenv()  # Esta linha carrega seu .env

def get_auth_headers(api_key, config):
    """Retorna headers de autenticação se necessário"""
    headers = {}
    
    api_config = config["apis"][api_key]
    
    if api_config.get("token_required", False):
        if api_key == "portal_transparencia":
            # Carrega do .env
            token = os.getenv('PORTAL_TRANSPARENCIA_API_KEY')
            if token:
                headers['chave-api-dados'] = token
                print(f"✅ Token carregado para {api_key}")
            else:
                print(f"❌ Token não encontrado para {api_key}")
        
        elif api_key == "dados_gov":
            token = os.getenv('DADOS_GOV_API_TOKEN')
            if token:
                headers['Authorization'] = f'Bearer {token}'
                print(f"✅ Token carregado para {api_key}")
    
    return headers

def test_api_endpoint(api_key, api_config, endpoint, headers=None):
    """Testa um endpoint específico de uma API"""
    base_url = api_config["base_url"]
    path = endpoint["path"]
    
    # Pula endpoints com placeholders
    if "{" in path:
        return "skipped"
    
    url = f"{base_url}{path}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code
    except Exception as e:
        return f"error: {str(e)}"

def main():
    """Função principal de teste"""
    print("🔧 TESTE COM TOKEN DO .env")
    print("=" * 40)
    
    # Carrega configuração
    with open("config-sistema-busca.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    results = []
    
    for api_key, api_config in config["apis"].items():
        if not api_config.get("enabled", True):
            continue
            
        print(f"\n🔍 Testando {api_config['name']}...")
        
        # Obtém headers com token do .env
        headers = get_auth_headers(api_key, config)
        
        # Testa apenas os primeiros 3 endpoints
        for endpoint in api_config.get("endpoints", [])[:3]:
            status = test_api_endpoint(api_key, api_config, endpoint, headers)
            
            results.append({
                "api": api_key,
                "path": endpoint["path"],
                "status": status
            })
            
            if isinstance(status, int) and 200 <= status < 300:
                print(f"   ✅ {endpoint['path']}: {status}")
            elif status == 401:
                print(f"   🔐 {endpoint['path']}: {status} (ainda sem acesso)")
            elif status == "skipped":
                print(f"   ⏭️  {endpoint['path']}: pulado")
            else:
                print(f"   ❌ {endpoint['path']}: {status}")
    
    # Salva resultados
    with open("validation_with_token.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["api", "path", "status"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n💾 Resultados salvos em: validation_with_token.csv")

if __name__ == "__main__":
    main()
