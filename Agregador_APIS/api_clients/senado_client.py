# senado_client.py - VERSÃO FINAL CORRIGIDA

import requests
import time
from time import sleep
from typing import Any, Dict, Optional, Tuple, Union, List
from datetime import datetime, timedelta
import json

BASE_URL = "https://legis.senado.leg.br/dadosabertos"
HEADERS = {"User-Agent": "ProjetoBuscaOficiais/1.0"}
TIMEOUT = (10, 30)

class SenadoAPIError(Exception):
    pass

_session = requests.Session()
_session.headers.update(HEADERS)

def _build_url(path: str, fmt: str = "json") -> str:
    """Constrói URL com tratamento correto de formato"""
    path = path.strip("/")
    
    # Tratamento especial para iCal
    if "iCal" in path:
        return f"{BASE_URL}/{path}"
    
    # Adiciona extensão apenas se não existir e formato for json/xml
    if fmt in ("json", "xml"):
        if not (path.endswith(".json") or path.endswith(".xml")):
            path = f"{path}.{fmt}"
    
    final_url = f"{BASE_URL}/{path}"
    return final_url

def _request(path: str, params: Optional[Dict[str, Any]] = None, fmt: str = "json", max_retries: int = 3) -> Union[Dict[str, Any], str]:
    """Função de requisição com rate limiting e retry logic"""
    url = _build_url(path, fmt=fmt)
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                sleep(2)
            
            resp = _session.get(url, params=params, timeout=TIMEOUT)
            
            if resp.status_code == 429:
                retry_after = int(resp.headers.get('retry-after', 30))
                print(f"⏳ Rate limit atingido. Aguardando {retry_after}s...")
                sleep(retry_after)
                continue
                
            resp.raise_for_status()
            
            if fmt == "json":
                return resp.json()
            return resp.text
            
        except requests.Timeout:
            if attempt == max_retries - 1:
                raise SenadoAPIError(f"Timeout após {max_retries} tentativas em {url}")
            print(f"⏳ Timeout na tentativa {attempt + 1}/{max_retries}, tentando novamente...")
            
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            raise SenadoAPIError(f"HTTP {status} ao acessar {url}") from e
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise SenadoAPIError(f"Erro de rede ao acessar {url}: {e}") from e
            print(f"⚠️ Erro de rede na tentativa {attempt + 1}/{max_retries}, tentando novamente...")
            
        except ValueError as e:
            raise SenadoAPIError(f"Erro ao decodificar JSON em {url}: {e}") from e
    
    raise SenadoAPIError(f"Falha após {max_retries} tentativas em {url}")

# --------------------------
# Utilitários de navegação
# --------------------------

def _iter_dicts_in(obj: Any) -> List[Dict[str, Any]]:
    """
    Varre o objeto e retorna a primeira lista de dicts encontrada (profundidade arbitrária).
    Ajuda quando chaves internas variam (ex.: 'Comissoes' vs 'Colegiados').
    """
    result: List[Dict[str, Any]] = []

    def dfs(node: Any):
        nonlocal result
        if result:
            return
        if isinstance(node, list):
            # Caso liste de listas, achamos o primeiro nível com dict
            flat = []
            for item in node:
                if isinstance(item, dict):
                    flat.append(item)
                elif isinstance(item, list):
                    for sub in item:
                        if isinstance(sub, dict):
                            flat.append(sub)
            if flat:
                result = flat
                return
            for item in node:
                dfs(item)
        elif isinstance(node, dict):
            for v in node.values():
                if result:
                    return
                dfs(v)

    dfs(obj)
    return result

def _peek_any_list(obj: Any, label: str = "Lista"):
    """
    Imprime o tamanho e um exemplo da primeira lista de dicts encontrada.
    """
    lst = _iter_dicts_in(obj)
    print(f"{label} - itens: {len(lst)} | Exemplo:", lst[0] if lst else None)

# ==========================
# Senadores
# ==========================

def listar_senadores_em_exercicio() -> Dict[str, Any]:
    """Lista senadores em exercício"""
    return _request("senador/lista/atual")

def detalhar_senador_por_codigo(codigo_senador: int) -> Dict[str, Any]:
    return _request(f"senador/{codigo_senador}")

def votos_senador(
    codigo_senador: int,
    *,
    sigla: Optional[str] = None,
    tramitando: Optional[str] = None,  # 's' ou 'n'
    tipo: Optional[str] = None,
    tipo_sessao: Optional[str] = None,
    ano: Optional[int] = None,
    primeiro: Optional[str] = None  # 'S' ou 'N'
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if sigla: params["sigla"] = sigla
    if tramitando: params["tramitando"] = tramitando
    if tipo: params["tipo"] = tipo
    if tipo_sessao: params["tipoSessao"] = tipo_sessao
    if ano: params["ano"] = ano
    if primeiro: params["primeiro"] = primeiro
    return _request(f"senador/{codigo_senador}/votacoes", params=params)

# ==========================
# Matérias
# ==========================

def obter_materia_por_codigo(codigo_materia: int) -> Dict[str, Any]:
    return _request(f"materia/{codigo_materia}")

def listar_materias_atualizadas(
    numdias: int = 15,
    *,
    sigla: Optional[str] = None,
    numero: Optional[int] = None,
    ano: Optional[int] = None,
    codigo: Optional[int] = None,
    codAssuntoGeral: Optional[int] = None,
    codAssuntoEspecifico: Optional[int] = None,
    alteracao: Optional[str] = None
) -> Dict[str, Any]:
    params: Dict[str, Any] = {"numdias": numdias}
    if sigla: params["sigla"] = sigla
    if numero: params["numero"] = numero
    if ano: params["ano"] = ano
    if codigo: params["codigo"] = codigo
    if codAssuntoGeral: params["codAssuntoGeral"] = codAssuntoGeral
    if codAssuntoEspecifico: params["codAssuntoEspecifico"] = codAssuntoEspecifico
    if alteracao: params["alteracao"] = alteracao
    return _request("materia/atualizadas", params=params)

def listar_tramitacao_por_tipo(
    *,
    sigla: str,
    situacao: Optional[str] = None,
    ano: Optional[int] = None,
    comissao: Optional[str] = None
) -> Dict[str, Any]:
    params: Dict[str, Any] = {"sigla": sigla}
    if situacao: params["situacao"] = situacao
    if ano: params["ano"] = ano
    if comissao: params["comissao"] = comissao
    return _request("materia/lista/tramitacao", params=params)

# ==========================
# Comissões
# ==========================

def listar_comissoes(tipo: str = "permanente") -> Dict[str, Any]:
    tipo = tipo.strip().lower()
    if tipo not in {"permanente", "temporaria", "cpi"}:
        raise ValueError("tipo deve ser 'permanente', 'temporaria' ou 'cpi'")
    return _request(f"comissao/lista/{tipo}")

def documentos_da_comissao(
    sigla: str,
    *,
    data_inicio_yyyymmdd: Optional[str] = None,
    data_fim_yyyymmdd: Optional[str] = None
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if data_inicio_yyyymmdd:
        if not (len(data_inicio_yyyymmdd) == 8 and data_inicio_yyyymmdd.isdigit()):
            raise ValueError("data_inicio_yyyymmdd deve ser AAAAMMDD")
        params["dataInicio"] = data_inicio_yyyymmdd
    if data_fim_yyyymmdd:
        if not (len(data_fim_yyyymmdd) == 8 and data_fim_yyyymmdd.isdigit()):
            raise ValueError("data_fim_yyyymmdd deve ser AAAAMMDD")
        params["dataFim"] = data_fim_yyyymmdd
    sigla = sigla.strip().upper()
    return _request(f"comissao/{sigla}/documentos", params=params)

# ==========================
# Agenda (Comissões)
# ==========================

def agenda_reunioes_por_data(data_yyyymmdd: str) -> Dict[str, Any]:
    if not (len(data_yyyymmdd) == 8 and data_yyyymmdd.isdigit()):
        raise ValueError("data_yyyymmdd deve estar no formato AAAAMMDD")
    return _request(f"agendareuniao/{data_yyyymmdd}")

def agenda_reunioes_atual_ical() -> str:
    return _request("agendareuniao/atual/iCal", fmt="txt")

# ==========================
# Plenário — votações (CORRIGIDO COM URL REAL!)
# ==========================

def votacoes_plenario_por_data(data_yyyymmdd: str) -> Dict[str, Any]:
    """
    ✅ CORRIGIDO: URL real descoberta através de testes!
    URL correta: /plenario/lista/votacao/{data}
    """
    if not (len(data_yyyymmdd) == 8 and data_yyyymmdd.isdigit()):
        raise ValueError("data_yyyymmdd deve estar no formato AAAAMMDD")
    
    # ✅ URL CORRETA descoberta via teste automatizado
    return _request(f"plenario/lista/votacao/{data_yyyymmdd}")

# ==========================
# Tabelas auxiliares (XML)
# ==========================

def listar_assuntos_materia_xml() -> str:
    return _request("dados/ListaAssuntos", fmt="xml")

def listar_classificacoes_materia_xml() -> str:
    return _request("dados/ListaClassificacoesMateria", fmt="xml")

def listar_tipos_emenda_xml() -> str:
    return _request("dados/ListaTiposEmenda", fmt="xml")

def listar_tipos_natureza_xml() -> str:
    return _request("dados/ListaTiposNatureza", fmt="xml")

def listar_tipos_decisao_xml() -> str:
    return _request("dados/ListaTiposDecisao", fmt="xml")

def listar_destinos_xml() -> str:
    return _request("dados/ListaDestinos", fmt="xml")

def baixar_termos_legislacao_xml() -> str:
    return _request("legislacao/termos", fmt="xml")

# ==========================
# Sistema de Testes Melhorado
# ==========================

class TestResult:
    def __init__(self, name: str, success: bool, message: str = "", data_summary: str = ""):
        self.name = name
        self.success = success
        self.message = message
        self.data_summary = data_summary

def _summarize_data(data: Any, max_items: int = 3) -> str:
    """Cria um resumo limpo dos dados retornados"""
    if isinstance(data, dict):
        if not data:
            return "Dict vazio"
        
        # Tenta encontrar listas de dados
        lists = _iter_dicts_in(data)
        if lists:
            return f"Lista com {len(lists)} itens"
        
        # Se não tem listas, mostra as chaves principais
        keys = list(data.keys())[:max_items]
        more = f" (+{len(data.keys()) - max_items} chaves)" if len(data.keys()) > max_items else ""
        return f"Dict com chaves: {keys}{more}"
    
    elif isinstance(data, str):
        lines = data.split('\n')
        return f"Texto com {len(lines)} linhas, {len(data)} chars"
    
    elif isinstance(data, list):
        return f"Lista com {len(data)} itens"
    
    return f"Tipo: {type(data).__name__}"

def _test_endpoint(name: str, func, *args, **kwargs) -> TestResult:
    """Testa um endpoint e retorna resultado resumido"""
    try:
        print(f"  ⏳ Testando {name}...")
        result = func(*args, **kwargs)
        summary = _summarize_data(result)
        return TestResult(name, True, "OK", summary)
    except Exception as e:
        error_msg = str(e)[:80] + "..." if len(str(e)) > 80 else str(e)
        return TestResult(name, False, error_msg)

def _print_test_results(results: List[TestResult]):
    """Imprime resultados dos testes de forma organizada"""
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
    print("🧪 EXECUTANDO TESTES BÁSICOS DO SENADO...")
    
    results = []
    
    # Senadores
    results.append(_test_endpoint("Senadores em exercício", listar_senadores_em_exercicio))
    
    # Matérias
    results.append(_test_endpoint("Matéria por código", obter_materia_por_codigo, 143611))
    results.append(_test_endpoint("Matérias atualizadas", listar_materias_atualizadas, 7))
    
    # Comissões
    results.append(_test_endpoint("Comissões permanentes", listar_comissoes, "permanente"))
    
    # Agenda
    hoje = datetime.now().strftime("%Y%m%d")
    results.append(_test_endpoint("Agenda hoje", agenda_reunioes_por_data, hoje))
    
    # Votações plenárias (CORRIGIDO!)
    results.append(_test_endpoint("Votações plenárias hoje", votacoes_plenario_por_data, hoje))
    
    _print_test_results(results)
    return results

def test_connection_only():
    """Testa apenas conectividade básica"""
    print("🧪 TESTANDO CONECTIVIDADE DO SENADO...")
    
    result = _test_endpoint("Conexão básica", listar_senadores_em_exercicio)
    
    print(f"\n{'✅ CONEXÃO OK' if result.success else '❌ FALHA NA CONEXÃO'}")
    if result.success:
        print(f"📊 {result.data_summary}")
    else:
        print(f"⚠️  {result.message}")
    
    return [result]

def test_all_endpoints():
    """Testa todos os endpoints (mais completo, com correção de votações)"""
    print("🧪 EXECUTANDO TESTES COMPLETOS DO SENADO (URL de votações corrigida)...")
    
    results = []
    
    # 1. Senadores
    print("📋 Testando Senadores...")
    results.append(_test_endpoint("Senadores em exercício", listar_senadores_em_exercicio))
    
    # Tenta pegar um código de senador para testes dependentes
    codigo_senador = None
    try:
        sen_data = listar_senadores_em_exercicio()
        lst = _iter_dicts_in(sen_data)
        if lst:
            for item in lst[:3]:
                ident = item.get("IdentificacaoParlamentar", item)
                cod = ident.get("CodigoParlamentar")
                if cod and str(cod).isdigit():
                    codigo_senador = int(cod)
                    break
    except:
        pass
    
    if codigo_senador:
        results.append(_test_endpoint("Detalhes do senador", detalhar_senador_por_codigo, codigo_senador))
        results.append(_test_endpoint("Votos do senador", votos_senador, codigo_senador, sigla="PLS"))
    
    # 2. Matérias
    print("📋 Testando Matérias...")
    results.append(_test_endpoint("Matéria por código", obter_materia_por_codigo, 143611))
    results.append(_test_endpoint("Matérias atualizadas", listar_materias_atualizadas, 7))
    results.append(_test_endpoint("Tramitação PL", listar_tramitacao_por_tipo, sigla="PL"))
    
    # 3. Comissões
    print("📋 Testando Comissões...")
    for tipo in ["permanente", "temporaria", "cpi"]:
        results.append(_test_endpoint(f"Comissões {tipo}", listar_comissoes, tipo))
    
    # Documentos de uma comissão conhecida (com rate limiting)
    sleep(1)
    fim = datetime.now().date()
    ini = fim - timedelta(days=30)
    results.append(_test_endpoint(
        "Docs comissão CCJ", 
        documentos_da_comissao, 
        "CCJ",
        data_inicio_yyyymmdd=ini.strftime("%Y%m%d"),
        data_fim_yyyymmdd=fim.strftime("%Y%m%d")
    ))
    
    # 4. Agenda
    print("📋 Testando Agenda...")
    for d in range(3):
        sleep(0.5)
        data = (datetime.now() + timedelta(days=d)).strftime("%Y%m%d")
        results.append(_test_endpoint(f"Agenda {data}", agenda_reunioes_por_data, data))
    
    results.append(_test_endpoint("Agenda iCal", agenda_reunioes_atual_ical))
    
    # 5. Plenário (CORRIGIDO - agora com URL real!)
    print("📋 Testando Plenário (URL corrigida)...")
    for d in range(5):
        sleep(0.5)
        data = (datetime.now() - timedelta(days=d)).strftime("%Y%m%d")
        results.append(_test_endpoint(f"Votações {data}", votacoes_plenario_por_data, data))
    
    # 6. Tabelas auxiliares (com pausas)
    print("📋 Testando Tabelas XML...")
    xml_endpoints = [
        ("Assuntos XML", listar_assuntos_materia_xml),
        ("Classificações XML", listar_classificacoes_materia_xml),
        ("Tipos Emenda XML", listar_tipos_emenda_xml),
        ("Tipos Natureza XML", listar_tipos_natureza_xml),
        ("Tipos Decisão XML", listar_tipos_decisao_xml),
        ("Destinos XML", listar_destinos_xml),
        ("Termos Legislação XML", baixar_termos_legislacao_xml),
    ]
    
    for name, func in xml_endpoints:
        sleep(0.5)
        results.append(_test_endpoint(name, func))
    
    _print_test_results(results)
    return results

# ==========================
# Executar Testes
# ==========================

if __name__ == "__main__":
    print("🚀 CLIENTE API SENADO - SISTEMA DE TESTES v4.0 FINAL")
    print("=" * 60)
    print("🔧 Versão FINAL - URL de votações descoberta e corrigida!")
    print("💡 Digite uma opção ou Enter para testes básicos.\n")
    
    print("Opções:")
    print("1 - Testes básicos (rápido)")
    print("2 - Testes completos (com URL de votações corrigida)")
    print("3 - Apenas verificar conexão")
    
    try:
        choice = input("\nOpção (1-3, ou Enter para básico): ").strip()
        
        if choice == "3":
            test_connection_only()
        elif choice == "2":
            test_all_endpoints()
        else:  # Padrão: testes básicos
            test_basic_endpoints()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
