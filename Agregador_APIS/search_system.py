import yaml
import requests
import re

# 1. Carrega configuração YAML
with open("config-sistema-busca.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 2. Função para escolher API com base na consulta
def escolher_api(query: str):
    query = query.lower()
    for termo, apis in config["search_mapping"].items():
        if termo in query:
            return apis[0]  # retorna a primeira API mapeada
    return None

# 3. Função para construir URL e parâmetros
def construir_requisicao(api_key: str, query: str):
    api_conf = config["apis"][api_key]
    base = api_conf["base_url"]
    # usa só o primeiro endpoint para simplificar
    endpoint = api_conf["endpoints"][0]
    path = endpoint["path"]
    # extrai parâmetros de UF ou CEP da query
    params = {}
    if "{cep}" in path:
        cep = re.search(r"\d{5}-?\d{3}", query)
        if cep:
            path = path.replace("{cep}", cep.group())
    if "{cnpj}" in path:
        cnpj = re.search(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}", query)
        if cnpj:
            path = path.replace("{cnpj}", cnpj.group())
    if "siglauf" in endpoint.get("parameters", []):
        uf = re.search(r"\b[A-Za-z]{2}\b", query)
        if uf:
            params["siglaUf"] = uf.group().upper()
    url = f"{base}{path}"
    return url, params

# 4. Função para executar busca e mostrar resultado
def buscar(query: str):
    api_key = escolher_api(query)
    if not api_key:
        print("❌ Não foi possível identificar qual API usar para essa consulta.")
        return
    url, params = construir_requisicao(api_key, query)
    print(f"\n🔍 Executando busca em '{api_key}'")
    print(f"URL: {url}")
    if params:
        print(f"Parâmetros: {params}")
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print("✅ Resultado obtido:")
        # exibe até 3 itens ou campos
        if isinstance(data, list):
            for item in data[:3]:
                print(item)
        elif isinstance(data, dict):
            # mostra as 3 primeiras chaves
            for k in list(data.keys())[:3]:
                print(f"{k}: {data[k]}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

# 5. Exemplo de uso
if __name__ == "__main__":
    while True:
        consulta = input("\nDigite sua busca (ou 'sair'): ").strip()
        if consulta.lower() in ("sair", "exit"):
            break
        buscar(consulta)
