#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para testar todos os endpoints do config-sistema-busca.yaml
Uso:
  1. Copie este arquivo e o config-sistema-busca.yaml na mesma pasta.
  2. Instale dependências: pip install pyyaml requests python-dotenv
  3. Defina variáveis de ambiente (se necessário):
     - PORTAL_TRANSPARENCIA_API_KEY
     - DADOS_GOV_API_TOKEN
  4. Execute: python test_all_endpoints.py
"""

import os
import yaml
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Valores de exemplo para placeholders e parâmetros
EXEMPLOS = {
    "id": "1",
    "codigoOrgao": "1",
    "codigoFuncional": "1",
    "cnpjCpf": "00000000000191",
    "cnpj": "00000000000191",
    "cpf": "00000000191",
    "cpfOuNis": "00000000191",
    "nis": "00000000000",
    "pagina": "1",
    "itensPorPagina": "1",
    "dataInicio": "2025-09-01",
    "dataFim": "2025-09-11",
    "mes": "09",
    "ano": "2025",
    "codigoMunicipio": "3550308",
    "codigoUg": "1",
    "modalidade": "1",
    "numero": "1",
    "idLicitacao": "1",
    "codigo": "1",
    "sigla": "SP",
    "ddd": "11",
    "cep": "01001000",
    "codigoParlamentar": "1",
    "codigoMateria": "1",
    "tipo": "COMISSAO",
    "data": datetime.now().strftime("%Y-%m-%d")
}

def load_config(path="config-sistema-busca.yaml"):
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("apis", {})

def fill_path(path):
    for key, val in EXEMPLOS.items():
        placeholder = "{" + key + "}"
        path = path.replace(placeholder, val)
    return path

def get_headers(api_key, api_cfg):
    headers = {}
    if api_cfg.get("token_required"):
        if api_key == "portal_transparencia":
            token = os.getenv("PORTAL_TRANSPARENCIA_API_KEY", "")
            if token: headers["chave-api-dados"] = token
        if api_key == "dados_gov":
            token = os.getenv("DADOS_GOV_API_TOKEN", "")
            if token: headers["Authorization"] = f"Bearer {token}"
    return headers

def test_endpoint(api_key, base_url, ep, timeout):
    url = base_url.rstrip("/") + fill_path(ep["path"])
    # Preenche parâmetros padrões
    params = {p: EXEMPLOS.get(p, "") for p in ep.get("parameters", [])}
    try:
        r = requests.request(ep["method"], url, params=params, headers=get_headers(api_key, api_cfg), timeout=timeout)
        ok = r.status_code in (200, 204)
        print(f"{api_key:20} {ep['method']:4} {ep['path']:35} → {r.status_code} {'OK' if ok else 'FAIL'}")
    except Exception as e:
        print(f"{api_key:20} {ep['method']:4} {ep['path']:35} → ERROR {e}")

if __name__ == "__main__":
    config = load_config()
    timeout = int(config.get("timeout", 30)) if isinstance(config, dict) else 30
    print("Iniciando testes de todos os endpoints...\n")
    for api_key, api_cfg in config.items():
        if not api_cfg.get("enabled", True):
            continue
        base = api_cfg.get("base_url", "")
        for ep in api_cfg.get("endpoints", []):
            test_endpoint(api_key, base, ep, timeout)
