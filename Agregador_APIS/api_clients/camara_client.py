# camara_client.py (versão 4.2 - Completo, Votações Otimizado e Testes Restaurados)

# Cliente dos Dados Abertos da Câmara dos Deputados com todos os endpoints implementados
# Inclui headers, rate limiting e timeout ajustados, com lógica especial para votações.

import requests
import time
from time import sleep
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"

# Headers que simulam um navegador comum para melhor compatibilidade
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Timeout mais generoso: (tempo para conectar, tempo para ler a resposta)
TIMEOUT = (15, 45)

class CamaraAPIError(Exception):
    """Exceção personalizada para erros da API da Câmara."""
    pass

def _get(url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Dict[str, Any]:
    """Função auxiliar para GET com rate limiting e lógica de repetição (retry)."""
    
    for attempt in range(max_retries):
        try:
            # Pausa preventina entre tentativas para não sobrecarregar a API
            if attempt > 0:
                sleep(5)
            
            response = requests.get(
                url, 
                headers=HEADERS, 
                params=params, 
                timeout=TIMEOUT
            )
            
            # Código 429: Too Many Requests (limite de requisições atingido)
            if response.status_code == 429:
                retry_after = int(response.headers.get('retry-after', 30))
                print(f"⏳ Rate limit atingido. Aguardando {retry_after}s...")
                sleep(retry_after)
                continue
            
            # Código 504: Gateway Timeout (servidor demorou demais para responder)
            if response.status_code == 504:
                if attempt == max_retries - 1:
                    raise CamaraAPIError(f"Gateway timeout persistente após {max_retries} tentativas em {url}")
                print(f"⏳ Gateway timeout na tentativa {attempt + 1}/{max_retries}, aguardando 10s...")
                sleep(10)
                continue
                
            response.raise_for_status()
            return response.json()
            
        except requests.Timeout:
            if attempt == max_retries - 1:
                raise CamaraAPIError(f"Timeout após {max_retries} tentativas em {url}")
            print(f"⏳ Timeout na tentativa {attempt + 1}/{max_retries}, tentando novamente...")
            
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else "N/A"
            raise CamaraAPIError(f"Erro HTTP {status} ao acessar {url}") from e
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise CamaraAPIError(f"Erro de rede ao acessar {url}: {e}") from e
            print(f"⚠️ Erro de rede na tentativa {attempt + 1}/{max_retries}, tentando novamente...")
            
        except ValueError as e: # Erro de decodificação do JSON
            raise CamaraAPIError(f"Erro ao decodificar JSON de {url}: {e}. Conteúdo: {response.text[:100]}") from e
    
    raise CamaraAPIError(f"Falha irrecuperável após {max_retries} tentativas em {url}")

def _get_limited_pages(endpoint: str, params: Optional[Dict[str, Any]] = None, max_pages: int = 3) -> List[Dict[str, Any]]:
    """Percorre um número limitado de páginas de um resultado."""
    results = []
    url = f"{BASE_URL}/{endpoint}"
    page_count = 0
    
    while url and page_count < max_pages:
        if page_count > 0:
            sleep(1.5)
            
        data = _get(url, params)
        page_data = data.get("dados", [])
        results.extend(page_data)
        
        links = data.get("links", [])
        next_link = next((l["href"] for l in links if l["rel"] == "next"), None)
        url = next_link
        params = None # Parâmetros já estão no `next_link`
        page_count += 1
    
    return results

# ==========================
# Endpoints: Deputados
# ==========================

def listar_deputados(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("deputados", params)

def obter_deputado(id_deputado: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/deputados/{id_deputado}")['dados']

def despesas_deputado(id_deputado: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"deputados/{id_deputado}/despesas", params, max_pages=2)

def discursos_deputado(id_deputado: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"deputados/{id_deputado}/discursos", params, max_pages=2)

def eventos_deputado(id_deputado: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"deputados/{id_deputado}/eventos", params)

def orgaos_deputado(id_deputado: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"deputados/{id_deputado}/orgaos")

def ocupacoes_deputado(id_deputado: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"deputados/{id_deputado}/ocupacoes")

# ==========================
# Endpoints: Partidos
# ==========================

def listar_partidos(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("partidos", params)

def obter_partido(id_partido: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/partidos/{id_partido}")['dados']

def membros_partido(id_partido: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"partidos/{id_partido}/membros", max_pages=2)

# ==========================
# Endpoints: Blocos
# ==========================

def listar_blocos(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("blocos", params)

def obter_bloco(id_bloco: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/blocos/{id_bloco}")['dados']

def membros_bloco(id_bloco: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"blocos/{id_bloco}/membros")

# ==========================
# Endpoints: Frentes
# ==========================

def listar_frentes(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("frentes", params)

def obter_frente(id_frente: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/frentes/{id_frente}")['dados']

def membros_frente(id_frente: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"frentes/{id_frente}/membros")

# ==========================
# Endpoints: Legislaturas
# ==========================

def listar_legislaturas(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("legislaturas", params)

def obter_legislatura(id_legislatura: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/legislaturas/{id_legislatura}")['dados']

def deputados_legislatura(id_legislatura: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"legislaturas/{id_legislatura}/deputados", params, max_pages=2)

def mesa_legislatura(id_legislatura: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"legislaturas/{id_legislatura}/mesa")

# ==========================
# Endpoints: Proposições
# ==========================

def listar_proposicoes(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("proposicoes", params)

def obter_proposicao(id_prop: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/proposicoes/{id_prop}")['dados']

def temas_proposicao(id_prop: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"proposicoes/{id_prop}/temas")

def autores_proposicao(id_prop: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"proposicoes/{id_prop}/autores")

def tramitacoes_proposicao(id_prop: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"proposicoes/{id_prop}/tramitacoes", max_pages=2)

def votacoes_proposicao(id_prop: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"proposicoes/{id_prop}/votacoes")

# ==========================
# Endpoints: Votações (OTIMIZADO)
# ==========================

def listar_votacoes(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Lista votações com filtros opcionais.

    IMPORTANTE: Este endpoint é muito propenso a timeouts (erro 504 Gateway Timeout)
    se não for usado com um intervalo de datas ('dataInicio' e 'dataFim').

    SOLUÇÃO: Se nenhum intervalo de data for fornecido, a função buscará
    automaticamente as votações dos ÚLTIMOS 7 DIAS para evitar o erro.

    Para buscas mais antigas, sempre forneça as datas. Exemplo:
    listar_votacoes({'dataInicio': '2023-01-01', 'dataFim': '2023-01-31'})
    """
    if params is None:
        params = {}

    # Otimização: Se não houver data, define um intervalo padrão de 7 dias.
    if 'dataInicio' not in params and 'dataFim' not in params:
        print("\n💡 Parâmetro de data não fornecido para 'listar_votacoes'. Usando os últimos 7 dias para evitar timeout.")
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=7)
        params['dataInicio'] = data_inicio.strftime('%Y-%m-%d')
        params['dataFim'] = data_fim.strftime('%Y-%m-%d')
        # Adiciona uma ordenação padrão para consistência
        params.setdefault('ordenarPor', 'dataHoraRegistro')
        params.setdefault('ordem', 'DESC')

    # Limita a busca a 2 páginas por segurança, mas o usuário pode aumentar se precisar.
    return _get_limited_pages("votacoes", params, max_pages=2)

def obter_votacao(id_votacao: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/votacoes/{id_votacao}")['dados']

def votos_votacao(id_votacao: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"votacoes/{id_votacao}/votos", max_pages=2)

# ==========================
# Endpoints: Eventos
# ==========================

def listar_eventos(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("eventos", params)

def obter_evento(id_evento: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/eventos/{id_evento}")['dados']

def deputados_evento(id_evento: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"eventos/{id_evento}/deputados")

def orgaos_evento(id_evento: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"eventos/{id_evento}/orgaos")

def pauta_evento(id_evento: int) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"eventos/{id_evento}/pauta")

# ==========================
# Endpoints: Órgãos
# ==========================

def listar_orgaos(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages("orgaos", params)

def obter_orgao(id_orgao: int) -> Dict[str, Any]:
    return _get(f"{BASE_URL}/orgaos/{id_orgao}")['dados']

def deputados_orgao(id_orgao: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"orgaos/{id_orgao}/deputados", params, max_pages=2)

def eventos_orgao(id_orgao: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"orgaos/{id_orgao}/eventos", params, max_pages=2)

def votacoes_orgao(id_orgao: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    return _get_limited_pages(f"orgaos/{id_orgao}/votacoes", params, max_pages=2)

# ==========================
# Endpoints: Referências/Tabelas Auxiliares
# ==========================

def listar_situacoes_deputado() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/situacoesDeputado")

def listar_situacoes_proposicao() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/situacoesProposicao")

def listar_tipos_proposicao() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/tiposProposicao", max_pages=99) # buscar todos

def listar_tipos_autor() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/tiposAutor")

def listar_tipos_tramitacao() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/tiposTramitacao")

def listar_tipos_orgao() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/tiposOrgao")

def listar_situacoes_orgao() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/situacoesOrgao")

def listar_tipos_evento() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/tiposEvento")

def listar_situacoes_evento() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/situacoesEvento")

def listar_uf() -> List[Dict[str, Any]]:
    return _get_limited_pages("referencias/uf")

# ==========================
# Sistema de Testes
# ==========================

class TestResult:
    def __init__(self, name: str, success: bool, message: str = "", data_summary: str = ""):
        self.name = name
        self.success = success
        self.message = message
        self.data_summary = data_summary

def _summarize_data(data: Any) -> str:
    """Cria um resumo dos dados retornados para o log de testes."""
    if isinstance(data, dict):
        if not data: return "Dict vazio"
        if 'dados' in data and isinstance(data['dados'], list):
            return f"Lista com {len(data['dados'])} itens"
        return f"Dict com chaves: {list(data.keys())}"
    elif isinstance(data, list):
        return f"Lista com {len(data)} itens"
    return f"Tipo: {type(data).__name__}"

def _test_endpoint(name: str, func, *args, **kwargs) -> TestResult:
    """Testa um endpoint e retorna um objeto TestResult."""
    try:
        print(f"  ⏳ Testando {name}...")
        result = func(*args, **kwargs)
        summary = _summarize_data(result)
        return TestResult(name, True, "OK", summary)
    except Exception as e:
        error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
        return TestResult(name, False, error_msg)

def _print_test_results(results: List[TestResult]):
    """Imprime os resultados dos testes de forma organizada."""
    success_count = sum(1 for r in results if r.success)
    total_count = len(results)
    
    print(f"\n{'='*60}")
    print(f"RESUMO DOS TESTES: {success_count}/{total_count} sucessos")
    print(f"{'='*60}")
    
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.name}")
        
        if result.success and result.data_summary:
            print(f"   📊 {result.data_summary}")
        elif not result.success:
            print(f"   ⚠️  {result.message}")
    
    print(f"{'='*60}\n")
    
def test_basic_endpoints():
    """Testa apenas os endpoints básicos (mais rápido)"""
    print("🧪 EXECUTANDO TESTES BÁSICOS DA CÂMARA...")
    
    results = []
    
    results.append(_test_endpoint("Deputados MG", listar_deputados, {"siglaUf": "MG", "itens": 5}))
    results.append(_test_endpoint("Partidos", listar_partidos, {"itens": 3}))
    results.append(_test_endpoint("Proposições 2024", listar_proposicoes, {"ano": 2024, "itens": 5}))
    results.append(_test_endpoint("Votações (últimos 7 dias)", listar_votacoes))
    results.append(_test_endpoint("Eventos", listar_eventos, {"itens": 3}))
    results.append(_test_endpoint("Órgãos", listar_orgaos, {"itens": 3}))
    
    _print_test_results(results)
    return results

def test_all_endpoints():
    """Testa os principais endpoints com a lógica de votações otimizada."""
    print("🧪 EXECUTANDO TESTES COMPLETOS DA CÂMARA (v4.2 - Completo e Otimizado)...")
    
    results = []
    
    print("\n📋 Testando Deputados...")
    results.append(_test_endpoint("Deputados", listar_deputados, {"itens": 5}))
    # Adicionando teste de um endpoint detalhado
    deputados_lista = listar_deputados({"itens": 1})
    if deputados_lista:
        id_dep = deputados_lista[0]['id']
        results.append(_test_endpoint(f"Detalhes Deputado {id_dep}", obter_deputado, id_dep))
        results.append(_test_endpoint(f"Despesas Deputado {id_dep}", despesas_deputado, id_dep))


    print("\n📋 Testando Partidos...")
    results.append(_test_endpoint("Partidos", listar_partidos, {"itens": 3}))
    
    print("\n📋 Testando Proposições...")
    results.append(_test_endpoint("Proposições", listar_proposicoes, {"itens": 5}))
    
    print("\n📋 Testando Votações (Otimizado)...")
    results.append(_test_endpoint("Votações (últimos 7 dias)", listar_votacoes))
    
    data_fim = datetime.now() - timedelta(days=120)
    data_ini = data_fim - timedelta(days=30)
    params_votacao = {
        "dataInicio": data_ini.strftime('%Y-%m-%d'), 
        "dataFim": data_fim.strftime('%Y-%m-%d'),
        "itens": 5
    }
    results.append(_test_endpoint("Votações (intervalo específico)", listar_votacoes, params_votacao))
    
    print("\n📋 Testando Outras Entidades...")
    results.append(_test_endpoint("Blocos", listar_blocos, {"itens": 3}))
    results.append(_test_endpoint("Legislaturas", listar_legislaturas))
    results.append(_test_endpoint("Eventos", listar_eventos, {"itens": 3}))
    results.append(_test_endpoint("Órgãos", listar_orgaos, {"itens": 3}))
    
    print("\n📋 Testando Referências...")
    results.append(_test_endpoint("Situações deputado", listar_situacoes_deputado))
    results.append(_test_endpoint("Tipos proposição", listar_tipos_proposicao))
    results.append(_test_endpoint("UFs", listar_uf))
    
    _print_test_results(results)

def test_connection_only():
    """Testa apenas a conectividade básica com a API."""
    print("🧪 TESTANDO CONECTIVIDADE DA CÂMARA...")
    result = _test_endpoint("Conexão básica", listar_deputados, {"itens": 1})
    
    print(f"\n{'✅ CONEXÃO OK' if result.success else '❌ FALHA NA CONEXÃO'}")
    if result.success:
        print(f"📊 {result.data_summary}")
    else:
        print(f"⚠️  {result.message}")

if __name__ == "__main__":
    print("🚀 CLIENTE API CÂMARA DOS DEPUTADOS - SISTEMA DE TESTES v4.2")
    print("=" * 70)
    print("🔧 Versão Completa - Lógica de votações otimizada e testes restaurados")
    print("💡 Prevenção de timeouts com datas padrão e tratamento de erros robusto")
    print("💡 Digite uma opção ou Enter para testes básicos.\n")
    
    print("Opções:")
    print("1 - Testes básicos (rápido)")
    print("2 - Testes completos (Otimizado)")
    print("3 - Teste de conexão (super rápido)")
    
    try:
        choice = input("\nOpção (1-3, ou Enter para básicos): ").strip()
        
        if choice == "2":
            test_all_endpoints()
        elif choice == "3":
            test_connection_only()
        else: # Padrão: "1" ou Enter
            test_basic_endpoints()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Testes interrompidos pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado durante os testes: {e}")

