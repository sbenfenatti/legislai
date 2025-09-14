#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script corrigido para testar APIs com token do Portal da Transparência
CORREÇÃO: Agora lê corretamente o arquivo .env

ANTES DE EXECUTAR:
1. Crie arquivo .env na mesma pasta com:
   PORTAL_TRANSPARENCIA_API_KEY=seu_token_aqui
2. pip install pyyaml requests python-dotenv colorama
3. python teste_apis_governo_corrigido.py
"""

import os
import yaml
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from colorama import init, Fore, Style
import time

# Inicializa cores no terminal
init()

# CORREÇÃO: Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Valores de teste mais realistas
VALORES_TESTE = {
    "id": "204554",  # ID real de deputado
    "codigoOrgao": "20000",  # Presidência da República
    "codigoFuncional": "01",
    "cnpjCpf": "00000000000191",  # CNPJ da União
    "cnpj": "00000000000191",
    "cpf": "00000000191",
    "cpfOuNis": "00000000191",
    "nis": "12345678901",
    "pagina": "1",
    "itensPorPagina": "10",
    "dataInicio": "2024-01-01",
    "dataFim": "2024-01-31",  # Período menor para garantir dados
    "mes": "01",
    "ano": "2024",
    "codigoMunicipio": "3550308",  # São Paulo
    "codigoUg": "20001",
    "modalidade": "1",
    "numero": "1",
    "idLicitacao": "1",
    "codigo": "1",
    "sigla": "PL",  # Sigla válida
    "uf": "SP",
    "ddd": "11",
    "cep": "01001000",  # CEP válido
    "codigoParlamentar": "5300",  # Código real do Senado
    "codigoMateria": "141549",  # Código real de matéria
    "tipo": "PERMANENTE",
    "data": "2024-09-01",
    "isbn": "9788520929582",
    "nome": "JOSE",
    "q": "educacao",
    "numero": "2021",  # Número válido para proposições
    "chave": "35200114200166000187550010000000046840000001"  # Chave válida de NF-e
}

def carregar_configuracao(arquivo="config-sistema-busca.yaml"):
    """Carrega o arquivo de configuração YAML"""
    try:
        with open(arquivo, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("apis", {})
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Arquivo {arquivo} não encontrado!{Style.RESET_ALL}")
        return {}
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao carregar config: {e}{Style.RESET_ALL}")
        return {}

def preencher_url(caminho):
    """Substitui placeholders na URL pelos valores de teste"""
    for chave, valor in VALORES_TESTE.items():
        placeholder = "{" + chave + "}"
        caminho = caminho.replace(placeholder, valor)
    return caminho

def obter_headers(nome_api, config_api):
    """CORRIGIDO: Configura headers de autenticação para cada API"""
    headers = {
        'User-Agent': 'Sistema-Busca-Governo-BR/1.0',
        'Accept': 'application/json'
    }
    
    # CORREÇÃO PRINCIPAL: Lê token do Portal da Transparência do .env
    if nome_api == "portal_transparencia" and config_api.get("token_required"):
        token = os.getenv("PORTAL_TRANSPARENCIA_API_KEY", "").strip()
        if token:
            headers["chave-api-dados"] = token
            print(f"{Fore.GREEN}🔑 Token do Portal da Transparência carregado: {token[:10]}...{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Token PORTAL_TRANSPARENCIA_API_KEY não encontrado no .env{Style.RESET_ALL}")
            
    elif nome_api == "dados_gov" and config_api.get("token_required"):
        token = os.getenv("DADOS_GOV_API_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            print(f"{Fore.YELLOW}⚠️  Token DADOS_GOV_API_TOKEN não encontrado no .env{Style.RESET_ALL}")
    
    return headers

def testar_endpoint(nome_api, config_api, url_base, endpoint, timeout=15):
    """CORRIGIDO: Testa endpoint com headers corretos"""
    url_completa = url_base.rstrip("/") + preencher_url(endpoint["path"])
    
    # Prepara parâmetros se existirem
    parametros = {}
    if "parameters" in endpoint:
        for param in endpoint["parameters"]:
            if param in VALORES_TESTE:
                parametros[param] = VALORES_TESTE[param]
    
    metodo = endpoint.get("method", "GET")
    descricao = endpoint.get("description", "Sem descrição")
    
    try:
        # CORREÇÃO: Passa config_api para obter_headers
        headers = obter_headers(nome_api, config_api)
        
        # Faz a requisição
        response = requests.request(
            method=metodo,
            url=url_completa,
            params=parametros,
            headers=headers,
            timeout=timeout,
            verify=True
        )
        
        status = response.status_code
        
        if status == 200:
            cor = Fore.GREEN
            resultado = "✅ FUNCIONANDO"
            try:
                dados = response.json()
                tamanho = len(str(dados))
                # Verifica se retornou dados úteis
                if isinstance(dados, dict) and dados:
                    detalhes = f"({tamanho} chars, {len(dados)} campos)"
                elif isinstance(dados, list) and dados:
                    detalhes = f"({len(dados)} itens)"
                else:
                    detalhes = "(Resposta vazia)"
            except:
                detalhes = "(HTML/Texto)"
                
        elif status == 401:
            cor = Fore.YELLOW
            resultado = "🔐 PRECISA TOKEN"
            detalhes = "(Autenticação necessária)"
            
        elif status == 400:
            cor = Fore.ORANGE if hasattr(Fore, 'ORANGE') else Fore.RED
            resultado = "⚠️ PARÂMETROS ERRADOS"
            detalhes = "(Bad Request - revisar parâmetros)"
            
        elif status == 404:
            cor = Fore.RED
            resultado = "❌ NÃO ENCONTRADO"
            detalhes = "(Endpoint inválido)"
            
        elif status == 405:
            cor = Fore.RED
            resultado = "❌ MÉTODO ERRADO"
            detalhes = "(Method Not Allowed)"
            
        elif status == 429:
            cor = Fore.MAGENTA
            resultado = "⏳ LIMITE ATINGIDO"
            detalhes = "(Muitas requisições)"
            
        elif status == 500:
            cor = Fore.RED
            resultado = "💥 ERRO SERVIDOR"
            detalhes = "(Internal Server Error)"
            
        else:
            cor = Fore.RED
            resultado = f"❌ ERRO {status}"
            detalhes = f"({response.reason})"
        
        return {
            "status": status,
            "funcionando": status == 200,
            "precisa_token": status == 401,
            "parametros_errados": status == 400,
            "metodo_errado": status == 405,
            "url": url_completa,
            "resultado": resultado,
            "detalhes": detalhes,
            "cor": cor,
            "endpoint": endpoint
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": 0,
            "funcionando": False,
            "erro": "Timeout",
            "resultado": "⏰ TIMEOUT",
            "detalhes": "(Muito lento)",
            "cor": Fore.RED,
            "endpoint": endpoint
        }
        
    except requests.exceptions.ConnectionError:
        return {
            "status": 0,
            "funcionando": False,
            "erro": "Conexão",
            "resultado": "🔌 SEM CONEXÃO",
            "detalhes": "(API offline)",
            "cor": Fore.RED,
            "endpoint": endpoint
        }
        
    except Exception as e:
        return {
            "status": 0,
            "funcionando": False,
            "erro": str(e),
            "resultado": "💥 ERRO",
            "detalhes": f"({str(e)[:30]}...)",
            "cor": Fore.RED,
            "endpoint": endpoint
        }

def main():
    """Função principal corrigida"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"🏛️  TESTADOR DE APIs DO GOVERNO BRASILEIRO - VERSÃO CORRIGIDA")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Verifica se arquivo .env existe
    if not os.path.exists('.env'):
        print(f"{Fore.YELLOW}⚠️  Arquivo .env não encontrado. Crie um com:")
        print(f"   PORTAL_TRANSPARENCIA_API_KEY=seu_token_aqui{Style.RESET_ALL}\n")
    
    # Carrega configuração
    apis = carregar_configuracao()
    if not apis:
        print(f"{Fore.RED}❌ Não foi possível carregar as configurações!{Style.RESET_ALL}")
        return
    
    # Estatísticas gerais
    total_apis = len(apis)
    total_endpoints = sum(len(api.get("endpoints", [])) for api in apis.values())
    
    print(f"📊 {total_apis} APIs configuradas")
    print(f"🎯 {total_endpoints} endpoints para testar\n")
    
    # Armazena todos os resultados para análise final
    todos_resultados = {}
    
    for nome_api, config_api in apis.items():
        if not config_api.get("enabled", True):
            print(f"{Fore.YELLOW}⏭️  {nome_api} - DESABILITADA{Style.RESET_ALL}")
            continue
            
        print(f"\n{Fore.BLUE}🔍 Testando: {config_api.get('name', nome_api)}{Style.RESET_ALL}")
        print(f"🌐 URL base: {config_api.get('base_url', 'N/A')}")
        
        url_base = config_api.get("base_url", "")
        endpoints = config_api.get("endpoints", [])
        
        resultados_endpoints = []
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"\n  {i:2d}/{len(endpoints)} ", end="")
            
            resultado = testar_endpoint(nome_api, config_api, url_base, endpoint)
            resultados_endpoints.append(resultado)
            
            # Mostra resultado colorido
            print(f"{resultado['cor']}{resultado['resultado']:<25}{Style.RESET_ALL} ", end="")
            print(f"{endpoint.get('path', 'N/A'):<40} {resultado['detalhes']}")
            
            # Pausa pequena para não sobrecarregar
            time.sleep(0.1)
        
        # Estatísticas da API
        funcionando = sum(1 for r in resultados_endpoints if r.get("funcionando"))
        precisa_token = sum(1 for r in resultados_endpoints if r.get("precisa_token"))
        parametros_errados = sum(1 for r in resultados_endpoints if r.get("parametros_errados"))
        metodo_errado = sum(1 for r in resultados_endpoints if r.get("metodo_errado"))
        
        todos_resultados[nome_api] = {
            "config": config_api,
            "resultados": resultados_endpoints,
            "stats": {
                "total": len(endpoints),
                "funcionando": funcionando,
                "precisa_token": precisa_token,
                "parametros_errados": parametros_errados,
                "metodo_errado": metodo_errado
            }
        }
        
        print(f"\n  📈 Resumo: {funcionando}/{len(endpoints)} OK, {precisa_token} token, {parametros_errados} param, {metodo_errado} método")
    
    # RESUMO FINAL MELHORADO
    print(f"\n\n{Fore.CYAN}{'='*80}")
    print(f"📋 RESUMO FINAL DETALHADO")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    for nome_api, dados in todos_resultados.items():
        stats = dados["stats"]
        funcionando = stats["funcionando"]
        total = stats["total"]
        
        if funcionando > total * 0.8:  # 80%+ funcionando
            cor = Fore.GREEN
            status = "✅ EXCELENTE"
        elif funcionando > total * 0.5:  # 50%+ funcionando
            cor = Fore.YELLOW
            status = "⚠️ PARCIAL"
        elif stats["precisa_token"] > total * 0.8:  # 80%+ precisa token
            cor = Fore.BLUE
            status = "🔐 PRECISA CONFIG"
        else:
            cor = Fore.RED
            status = "❌ PROBLEMAS"
        
        print(f"{cor}{status:<18}{Style.RESET_ALL} {nome_api:<25} {funcionando:2d}/{total:2d} OK")
        
        # Detalhes dos problemas
        if stats["parametros_errados"] > 0:
            print(f"{'':20} ⚠️ {stats['parametros_errados']} com parâmetros errados")
        if stats["metodo_errado"] > 0:
            print(f"{'':20} ❌ {stats['metodo_errado']} com método errado")
    
    print(f"\n{Fore.GREEN}✅ Teste detalhado concluído!{Style.RESET_ALL}")
    
    # Salva relatório detalhado
    salvar_relatorio_problemas(todos_resultados)

def salvar_relatorio_problemas(resultados):
    """Salva relatório detalhado dos problemas encontrados"""
    with open("relatorio_problemas_apis.md", "w", encoding="utf-8") as f:
        f.write("# 🔧 RELATÓRIO DE PROBLEMAS - APIs GOVERNO BRASILEIRO\n\n")
        f.write("Gerado automaticamente em: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n\n")
        
        for nome_api, dados in resultados.items():
            stats = dados["stats"]
            f.write(f"## 📊 {nome_api.upper()}\n\n")
            f.write(f"- **Total endpoints**: {stats['total']}\n")
            f.write(f"- **Funcionando**: {stats['funcionando']}\n")
            f.write(f"- **Precisa token**: {stats['precisa_token']}\n")
            f.write(f"- **Parâmetros errados**: {stats['parametros_errados']}\n")
            f.write(f"- **Método errado**: {stats['metodo_errado']}\n\n")
            
            # Lista problemas específicos
            problemas = [r for r in dados["resultados"] if not r.get("funcionando")]
            if problemas:
                f.write("### ❌ Endpoints com Problemas:\n\n")
                for problema in problemas:
                    f.write(f"- `{problema['endpoint']['path']}`: {problema['resultado']} - {problema['detalhes']}\n")
                f.write("\n")
        
    print(f"{Fore.GREEN}📄 Relatório salvo em: relatorio_problemas_apis.md{Style.RESET_ALL}")

if __name__ == "__main__":
    main()