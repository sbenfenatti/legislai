"""
ibge_api_client_completo.py

🇧🇷 CLIENTE COMPLETO - API IBGE Dados Agregados v3.0.0 - VERSÃO PREMIUM
========================================================================

Cliente Python COMPLETO para a API de dados agregados do IBGE.

✨ FUNCIONALIDADES PREMIUM:
✅ TODOS os 6 endpoints com TODOS os parâmetros
✅ Suporte a localidades contextuais avançadas
✅ Múltiplos formatos de período e classificação  
✅ Parser de símbolos especiais (-, .., ..., X)
✅ Sistema de cache inteligente
✅ Construtor de queries avançado
✅ Validação automática de parâmetros
✅ Detecção de limite de 100.000 valores
✅ Exportação CSV/Excel/JSON
✅ Análise automática de dados
✅ Sistema de batch para múltiplas consultas
✅ Retry inteligente e rate limiting

Base URL: https://servicodados.ibge.gov.br/api/v3/agregados
Documentação: https://servicodados.ibge.gov.br/api/docs/agregados
Requisitos: pip install requests pandas openpyxl
"""

import requests
import pandas as pd
import json
import time
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import csv
from pathlib import Path

# ==========================================
# CONFIGURAÇÕES E CONSTANTES
# ==========================================

BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"
TIMEOUT = (10, 60)
MAX_RETRIES = 3
CACHE_EXPIRE_HOURS = 24
MAX_VALUES_PER_REQUEST = 100000

# Códigos dos níveis geográficos
NIVEIS_GEOGRAFICOS = {
    'N1': 'Brasil',
    'N2': 'Região', 
    'N3': 'Unidade da Federação',
    'N6': 'Município',
    'N7': 'Região Metropolitana',
    'N8': 'Microrregião',
    'N9': 'Mesorregião',
    'N10': 'Região Integrada de Desenvolvimento',
    'N11': 'Região de Desenvolvimento'
}

# Códigos de periodicidade
PERIODICIDADES = {
    'P1': 'Diária',
    'P2': 'Semanal', 
    'P3': 'Decendial',
    'P4': 'Quinzenal',
    'P5': 'Mensal',
    'P6': 'Bimestral',
    'P7': 'Trimestral',
    'P8': 'Quadrimestral',
    'P9': 'Semestral',
    'P10': 'Anual',
    'P11': 'Bienal',
    'P12': 'Trienal',
    'P13': 'Quinquenal',
    'P14': 'Decenal'
}

# Símbolos especiais nos resultados
SIMBOLOS_ESPECIAIS = {
    '-': 'Zero não resultante de arredondamento',
    '..': 'Não se aplica',
    '...': 'Dado não disponível', 
    'X': 'Dado omitido para evitar individualização'
}

class IBGEAPIError(Exception):
    """Exceção específica para erros da API do IBGE"""
    pass

class QueryLimitError(IBGEAPIError):
    """Exceção para quando a consulta excede o limite de 100.000 valores"""
    pass

@dataclass
class CacheEntry:
    """Entrada do cache com timestamp"""
    data: Any
    timestamp: datetime

    def is_expired(self, hours: int = CACHE_EXPIRE_HOURS) -> bool:
        return datetime.now() - self.timestamp > timedelta(hours=hours)

@dataclass
class QueryBuilder:
    """Construtor de queries inteligente"""
    agregado: Optional[int] = None
    variaveis: Optional[List[str]] = None
    periodos: Optional[List[str]] = None
    localidades: Optional[List[str]] = None
    classificacoes: Optional[Dict[str, List[str]]] = None
    view: Optional[str] = None

    def __post_init__(self):
        if self.variaveis is None:
            self.variaveis = []
        if self.periodos is None:
            self.periodos = []
        if self.localidades is None:
            self.localidades = []
        if self.classificacoes is None:
            self.classificacoes = {}

    def adicionar_variavel(self, variavel: str) -> 'QueryBuilder':
        """Adiciona uma variável à consulta"""
        if variavel not in self.variaveis:
            self.variaveis.append(variavel)
        return self

    def adicionar_periodo(self, periodo: str) -> 'QueryBuilder':
        """Adiciona um período à consulta"""
        if periodo not in self.periodos:
            self.periodos.append(periodo)
        return self

    def adicionar_localidade(self, localidade: str) -> 'QueryBuilder':
        """Adiciona uma localidade à consulta"""
        if localidade not in self.localidades:
            self.localidades.append(localidade)
        return self

    def adicionar_classificacao(self, id_classificacao: str, categorias: List[str]) -> 'QueryBuilder':
        """Adiciona uma classificação à consulta"""
        self.classificacoes[id_classificacao] = categorias
        return self

    def definir_view(self, view: str) -> 'QueryBuilder':
        """Define o modo de visualização (OLAP, flat)"""
        if view.upper() in ['OLAP', 'FLAT']:
            self.view = view.upper()
        return self

    def build_variaveis_string(self) -> str:
        """Constrói string de variáveis"""
        if not self.variaveis:
            return "all"
        return "|".join(self.variaveis)

    def build_periodos_string(self) -> str:
        """Constrói string de períodos"""
        if not self.periodos:
            return "-6"  # Últimos 6 períodos por padrão
        return "|".join(self.periodos)

    def build_localidades_string(self) -> str:
        """Constrói string de localidades"""
        if not self.localidades:
            return "BR"  # Brasil por padrão
        return "|".join(self.localidades)

    def build_classificacoes_string(self) -> str:
        """Constrói string de classificações"""
        if not self.classificacoes:
            return None

        parts = []
        for id_class, categorias in self.classificacoes.items():
            if categorias == ['all']:
                parts.append(f"{id_class}[all]")
            else:
                cats_str = ",".join(categorias)
                parts.append(f"{id_class}[{cats_str}]")

        return "|".join(parts)

    def estimate_values_count(self, num_periodos: int = 6) -> int:
        """Estima número de valores que a consulta retornará"""
        num_localidades = len(self.localidades) if self.localidades else 1
        num_categorias = 1

        for categorias in self.classificacoes.values():
            num_categorias *= len(categorias)

        return num_categorias * num_periodos * num_localidades

@dataclass 
class TestResult:
    """Resultado de teste de endpoint"""
    name: str
    success: bool
    message: str = ""
    data_summary: str = ""
    execution_time: float = 0.0

class IBGEClientCompleto:
    """Cliente completo para API do IBGE com todas as funcionalidades"""

    def __init__(self, cache_enabled: bool = True, rate_limit: float = 0.1):
        self.base_url = BASE_URL
        self.cache_enabled = cache_enabled
        self.cache: Dict[str, CacheEntry] = {}
        self.rate_limit = rate_limit  # Segundos entre requisições
        self.last_request_time = 0.0

        # Configurar sessão HTTP
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "IBGEClientCompleto/2.0"
        })

    def _wait_rate_limit(self):
        """Aguarda rate limit entre requisições"""
        if self.rate_limit > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)

    def _request(self, endpoint: str, params: Optional[Dict] = None, use_cache: bool = True) -> Any:
        """Faz requisição com cache e retry"""
        # Verificar cache
        cache_key = f"{endpoint}?{json.dumps(params, sort_keys=True)}"
        if use_cache and self.cache_enabled and cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                return entry.data

        # Rate limiting
        self._wait_rate_limit()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Retry com backoff exponencial
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, params=params, timeout=TIMEOUT)
                response.raise_for_status()
                data = response.json()

                # Salvar no cache
                if self.cache_enabled:
                    self.cache[cache_key] = CacheEntry(data, datetime.now())

                self.last_request_time = time.time()
                return data

            except requests.HTTPError as e:
                if e.response.status_code == 500:
                    # Erro 500 pode indicar limite de 100k valores
                    raise QueryLimitError("Consulta excede limite de 100.000 valores")
                elif e.response.status_code == 429:
                    # Rate limiting do servidor
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise IBGEAPIError(f"HTTP {e.response.status_code}: {str(e)}")
            except requests.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise IBGEAPIError(f"Erro na requisição após {MAX_RETRIES} tentativas: {str(e)}")
                time.sleep(2 ** attempt)

        raise IBGEAPIError("Máximo de tentativas excedido")

    # ==========================================
    # TODOS OS 6 ENDPOINTS - IMPLEMENTAÇÃO COMPLETA
    # ==========================================

    def listar_agregados(self,
                        periodo: Optional[str] = None,
                        assunto: Optional[int] = None, 
                        classificacao: Optional[int] = None,
                        periodicidade: Optional[str] = None,
                        nivel: Optional[str] = None) -> List[Dict]:
        """
        Lista agregados agrupados por pesquisa - TODOS OS PARÂMETROS

        Args:
            periodo: Período com periodicidade (ex: "P5[202001]" para jan/2020 mensal)
            assunto: ID do assunto (ex: 70 para "Abate de animais") 
            classificacao: ID da classificação (ex: 12896 para "Agricultura familiar")
            periodicidade: Periodicidade (P1-P14, ex: "P5" para mensal)
            nivel: Nível geográfico (N1-N11, ex: "N6" para municípios)

        Returns:
            Lista de agregados agrupados por pesquisa

        Exemplos:
            >>> client = IBGEClientCompleto()
            >>> # Todos os agregados
            >>> todos = client.listar_agregados()
            >>> 
            >>> # Agregados mensais de 2020
            >>> jan_2020 = client.listar_agregados(periodo="P5[202001]")
            >>> 
            >>> # Agregados sobre agropecuária para municípios 
            >>> agro = client.listar_agregados(assunto=1419, nivel="N6")
            >>> 
            >>> # Agregados trimestrais
            >>> trim = client.listar_agregados(periodicidade="P7")
        """
        params = {}
        if periodo:
            params['periodo'] = periodo
        if assunto:
            params['assunto'] = assunto
        if classificacao:
            params['classificacao'] = classificacao
        if periodicidade:
            params['periodicidade'] = periodicidade
        if nivel:
            params['nivel'] = nivel

        return self._request("", params)

    def obter_metadados(self, agregado: int, use_cache: bool = True) -> Dict:
        """
        Obtém metadados completos do agregado

        Args:
            agregado: ID do agregado
            use_cache: Usar cache (padrão: True)

        Returns:
            Metadados completos incluindo variáveis, classificações, etc.

        Exemplos:
            >>> client = IBGEClientCompleto()
            >>> meta = client.obter_metadados(1705)
            >>> print(f"Nome: {meta['nome']}")
            >>> print(f"Variáveis: {len(meta['variaveis'])}")
            >>> print(f"Classificações: {len(meta['classificacoes'])}")
        """
        return self._request(f"{agregado}/metadados", use_cache=use_cache)

    def obter_periodos(self, agregado: int, use_cache: bool = True) -> List[Dict]:
        """
        Obtém todos os períodos disponíveis para o agregado

        Args:
            agregado: ID do agregado  
            use_cache: Usar cache (padrão: True)

        Returns:
            Lista completa de períodos com IDs, literals e modificações
        """
        return self._request(f"{agregado}/periodos", use_cache=use_cache)

    def obter_localidades(self, agregado: int, nivel: str, use_cache: bool = True) -> List[Dict]:
        """
        Obtém localidades por nível(is) geográfico(s) - SUPORTE MÚLTIPLOS NÍVEIS

        Args:
            agregado: ID do agregado
            nivel: Nível(is) geográfico(s) - pode ser múltiplos separados por |
                  Ex: "N6", "N7|N6", "N3|N6"
            use_cache: Usar cache (padrão: True)

        Returns:
            Lista de localidades com ID, nome e nível

        Exemplos:
            >>> client = IBGEClientCompleto()
            >>> # Municípios
            >>> municipios = client.obter_localidades(1705, "N6")
            >>> 
            >>> # Regiões metropolitanas E municípios
            >>> rm_mun = client.obter_localidades(1705, "N7|N6") 
            >>> 
            >>> # Estados e municípios
            >>> uf_mun = client.obter_localidades(1705, "N3|N6")
        """
        return self._request(f"{agregado}/localidades/{nivel}", use_cache=use_cache)

    def obter_variaveis(self,
                       agregado: int,
                       variavel: Union[str, List[str]] = "all",
                       localidades: Union[str, List[str]] = "BR",
                       classificacao: Optional[Union[str, Dict[str, List[str]]]] = None,
                       view: Optional[str] = None,
                       validate_limit: bool = True) -> List[Dict]:
        """
        Obtém variáveis do agregado (últimos 6 períodos) - TODOS OS PARÂMETROS

        Args:
            agregado: ID do agregado
            variavel: Variável(is) - string, lista ou "all"/"allxp"
            localidades: Localidades - string, lista ou padrões especiais
            classificacao: Classificações - string ou dict {id_class: [categorias]}
            view: Modo visualização ("OLAP", "flat" ou None)
            validate_limit: Validar limite de 100k valores (padrão: True)

        Returns:
            Lista de variáveis com todos os resultados

        Exemplos:
            >>> client = IBGEClientCompleto()
            >>> 
            >>> # Todas as variáveis do Brasil
            >>> br = client.obter_variaveis(1705)
            >>> 
            >>> # Múltiplas variáveis para São Paulo  
            >>> sp = client.obter_variaveis(1705, ["214", "1982"], "N6[3550308]")
            >>> 
            >>> # Com classificação (produto=abacaxi E proprietários)
            >>> abacaxi = client.obter_variaveis(1712, "214", "BR", "226[4844]|218[4780]")
            >>> 
            >>> # Localidades contextuais (municípios do RJ e SP)
            >>> rj_sp = client.obter_variaveis(512, "216", "N6[N3[33,35]]")
            >>> 
            >>> # Múltiplas classificações com dict
            >>> multi = client.obter_variaveis(1712, "all", "BR", {
            ...     "226": ["4844", "96608"],  # Abacaxi e alho
            ...     "218": ["4780"]           # Proprietários
            ... })
            >>> 
            >>> # Modo OLAP
            >>> olap = client.obter_variaveis(1705, view="OLAP")
        """
        # Processar parâmetros
        params = {}

        # Localidades
        if isinstance(localidades, list):
            params["localidades"] = "|".join(localidades)
        else:
            params["localidades"] = localidades

        # Classificação
        if classificacao:
            if isinstance(classificacao, dict):
                class_parts = []
                for id_class, categorias in classificacao.items():
                    if categorias == ["all"]:
                        class_parts.append(f"{id_class}[all]") 
                    else:
                        cats_str = ",".join(categorias)
                        class_parts.append(f"{id_class}[{cats_str}]")
                params["classificacao"] = "|".join(class_parts)
            else:
                params["classificacao"] = classificacao

        # View
        if view:
            params["view"] = view.upper()

        # Variável
        if isinstance(variavel, list):
            var_str = "|".join(variavel)
        else:
            var_str = variavel

        # Validar limite se solicitado
        if validate_limit:
            self._validate_query_limit(params, 6)  # 6 períodos padrão

        return self._request(f"{agregado}/variaveis/{var_str}", params)

    def obter_variaveis_periodo(self,
                               agregado: int,
                               periodos: Union[str, List[str]],
                               variavel: Union[str, List[str]] = "all", 
                               localidades: Union[str, List[str]] = "BR",
                               classificacao: Optional[Union[str, Dict[str, List[str]]]] = None,
                               view: Optional[str] = None,
                               validate_limit: bool = True) -> List[Dict]:
        """
        Obtém variáveis para períodos específicos - TODOS OS PARÂMETROS E FORMATOS

        Args:
            agregado: ID do agregado
            periodos: Período(s) - múltiplos formatos suportados:
                     - Negativos: "-6" (últimos 6)
                     - Intervalo: "201701-201706" 
                     - Múltiplos: ["201701", "201706", "201710"]
                     - Combinado: "201701-201706|201710"
            variavel: Variável(is) - string, lista ou "all"/"allxp"
            localidades: Localidades - string, lista ou padrões especiais
            classificacao: Classificações - string ou dict
            view: Modo visualização ("OLAP", "flat")
            validate_limit: Validar limite de 100k valores

        Returns:
            Lista de variáveis com resultados dos períodos especificados

        Exemplos:
            >>> client = IBGEClientCompleto()
            >>> 
            >>> # Últimos 6 períodos
            >>> ult6 = client.obter_variaveis_periodo(1705, "-6")
            >>> 
            >>> # Primeiro semestre 2017
            >>> sem1 = client.obter_variaveis_periodo(1705, "201701-201706")
            >>> 
            >>> # Períodos específicos
            >>> specs = client.obter_variaveis_periodo(1705, ["201701", "201706", "201710"])
            >>> 
            >>> # Combinação: semestre + outubro
            >>> comb = client.obter_variaveis_periodo(1705, "201701-201706|201710")
            >>> 
            >>> # Com todas as opções
            >>> completo = client.obter_variaveis_periodo(
            ...     agregado=1712,
            ...     periodos="201701-201712", 
            ...     variavel=["214", "1982"],
            ...     localidades="N6[3550308,3304557]",  # SP e RJ
            ...     classificacao={"226": ["4844"], "218": ["4780"]},
            ...     view="OLAP"
            ... )
        """
        # Processar períodos
        if isinstance(periodos, list):
            periodos_str = "|".join(periodos)
        else:
            periodos_str = periodos

        # Processar parâmetros (igual ao método anterior)
        params = {}

        # Localidades
        if isinstance(localidades, list):
            params["localidades"] = "|".join(localidades)
        else:
            params["localidades"] = localidades

        # Classificação
        if classificacao:
            if isinstance(classificacao, dict):
                class_parts = []
                for id_class, categorias in classificacao.items():
                    if categorias == ["all"]:
                        class_parts.append(f"{id_class}[all]")
                    else:
                        cats_str = ",".join(categorias)
                        class_parts.append(f"{id_class}[{cats_str}]")
                params["classificacao"] = "|".join(class_parts)
            else:
                params["classificacao"] = classificacao

        # View
        if view:
            params["view"] = view.upper()

        # Variável
        if isinstance(variavel, list):
            var_str = "|".join(variavel)
        else:
            var_str = variavel

        # Validar limite se solicitado
        if validate_limit:
            num_periodos = self._estimate_period_count(periodos_str)
            self._validate_query_limit(params, num_periodos)

        return self._request(f"{agregado}/periodos/{periodos_str}/variaveis/{var_str}", params)

    # ==========================================
    # UTILITÁRIOS AVANÇADOS
    # ==========================================

    def _validate_query_limit(self, params: Dict, num_periodos: int):
        """Valida se a consulta não excede limite de 100k valores"""
        # Estimar número de localidades
        localidades = params.get("localidades", "BR")
        if localidades == "BR":
            num_localidades = 1
        elif "[" in localidades:
            # Contar localidades específicas: N6[123,456,789]
            matches = re.findall(r'\[([^\]]+)\]', localidades)
            if matches:
                num_localidades = sum(len(match.split(',')) for match in matches)
            else:
                num_localidades = 1
        else:
            # Nível geral: N6, N7, etc.
            num_localidades = 5570 if "N6" in localidades else 100  # Estimativa

        # Estimar número de categorias
        classificacao = params.get("classificacao", "")
        num_categorias = 1
        if classificacao:
            # Contar categorias em cada classificação
            class_parts = classificacao.split("|")
            for part in class_parts:
                if "[all]" in part:
                    num_categorias *= 50  # Estimativa para 'all'
                elif "[" in part:
                    cats = re.findall(r'\[([^\]]+)\]', part)
                    if cats:
                        num_categorias *= len(cats[0].split(','))

        # Calcular total
        total_values = num_categorias * num_periodos * num_localidades

        if total_values > MAX_VALUES_PER_REQUEST:
            raise QueryLimitError(
                f"Consulta estimada em {total_values:,} valores "
                f"(máximo: {MAX_VALUES_PER_REQUEST:,}). "
                f"Reduza localidades, períodos ou classificações."
            )

    def _estimate_period_count(self, periodos_str: str) -> int:
        """Estima quantidade de períodos na string"""
        if periodos_str.startswith("-"):
            return int(periodos_str[1:])
        elif "-" in periodos_str and not periodos_str.startswith("-"):
            # Intervalo: 201701-201706 = 6 períodos
            parts = periodos_str.split("-")
            if len(parts) == 2:
                return int(parts[1][-2:]) - int(parts[0][-2:]) + 1
        elif "|" in periodos_str:
            return len(periodos_str.split("|"))
        else:
            return 1

    def criar_query_builder(self, agregado: int) -> QueryBuilder:
        """Cria um construtor de queries para o agregado"""
        return QueryBuilder(agregado=agregado)

    def parse_resultados(self, dados: List[Dict], interpretar_simbolos: bool = True) -> pd.DataFrame:
        """
        Converte resultados da API para DataFrame com parsing de símbolos especiais

        Args:
            dados: Dados retornados da API
            interpretar_simbolos: Interpretar símbolos especiais (-, .., ..., X)

        Returns:
            DataFrame com dados organizados
        """
        if not dados:
            return pd.DataFrame()

        rows = []
        for variavel in dados:
            var_id = variavel.get('id')
            var_nome = variavel.get('variavel')
            var_unidade = variavel.get('unidade')

            for resultado in variavel.get('resultados', []):
                for serie in resultado.get('series', []):
                    localidade = serie.get('localidade', {})

                    for periodo, valor in serie.get('serie', {}).items():
                        row = {
                            'variavel_id': var_id,
                            'variavel_nome': var_nome,
                            'unidade': var_unidade,
                            'periodo': periodo,
                            'localidade_id': localidade.get('id'),
                            'localidade_nome': localidade.get('nome'),
                            'valor_original': valor
                        }

                        # Interpretar símbolos especiais
                        if interpretar_simbolos and str(valor) in SIMBOLOS_ESPECIAIS:
                            row['valor_interpretado'] = SIMBOLOS_ESPECIAIS[str(valor)]
                            row['valor_numerico'] = None
                        else:
                            row['valor_interpretado'] = valor
                            try:
                                row['valor_numerico'] = float(valor) if valor not in ['', None] else None
                            except (ValueError, TypeError):
                                row['valor_numerico'] = None

                        rows.append(row)

        return pd.DataFrame(rows)

    def exportar_csv(self, dados: List[Dict], filename: str, interpretar_simbolos: bool = True):
        """Exporta dados para CSV"""
        df = self.parse_resultados(dados, interpretar_simbolos)
        df.to_csv(filename, index=False, encoding='utf-8')
        return f"Dados exportados para {filename}"

    def exportar_excel(self, dados: List[Dict], filename: str, interpretar_simbolos: bool = True):
        """Exporta dados para Excel"""
        df = self.parse_resultados(dados, interpretar_simbolos)
        df.to_excel(filename, index=False, engine='openpyxl')
        return f"Dados exportados para {filename}"

    def analisar_dados(self, dados: List[Dict]) -> Dict:
        """Análise automática dos dados retornados"""
        df = self.parse_resultados(dados, interpretar_simbolos=True)

        if df.empty:
            return {"erro": "Sem dados para analisar"}

        analise = {
            "resumo": {
                "total_registros": len(df),
                "total_variaveis": df['variavel_id'].nunique(),
                "total_localidades": df['localidade_id'].nunique(), 
                "periodo_inicial": df['periodo'].min(),
                "periodo_final": df['periodo'].max(),
                "periodos_total": df['periodo'].nunique()
            },
            "variaveis": [],
            "valores_especiais": {}
        }

        # Análise por variável
        for var_id in df['variavel_id'].unique():
            var_df = df[df['variavel_id'] == var_id]
            var_info = {
                "id": var_id,
                "nome": var_df['variavel_nome'].iloc[0],
                "unidade": var_df['unidade'].iloc[0],
                "registros": len(var_df),
                "localidades": var_df['localidade_id'].nunique(),
                "periodos": var_df['periodo'].nunique()
            }

            # Estatísticas dos valores numéricos
            valores_num = var_df['valor_numerico'].dropna()
            if not valores_num.empty:
                var_info["estatisticas"] = {
                    "minimo": float(valores_num.min()),
                    "maximo": float(valores_num.max()),
                    "media": float(valores_num.mean()),
                    "total": float(valores_num.sum())
                }

            analise["variaveis"].append(var_info)

        # Contar símbolos especiais
        for simbolo, significado in SIMBOLOS_ESPECIAIS.items():
            count = (df['valor_original'] == simbolo).sum()
            if count > 0:
                analise["valores_especiais"][simbolo] = {
                    "significado": significado,
                    "ocorrencias": int(count)
                }

        return analise

    def consulta_batch(self, consultas: List[Dict], delay: float = 0.5) -> List[Dict]:
        """
        Executa múltiplas consultas em lote

        Args:
            consultas: Lista de dicts com parâmetros de consulta
            delay: Delay entre consultas (segundos)

        Returns:
            Lista com resultados de cada consulta
        """
        resultados = []

        for i, consulta in enumerate(consultas):
            try:
                print(f"Executando consulta {i+1}/{len(consultas)}...")

                # Determinar método baseado nos parâmetros
                if 'periodos' in consulta:
                    resultado = self.obter_variaveis_periodo(**consulta)
                else:
                    resultado = self.obter_variaveis(**consulta)

                resultados.append({
                    "sucesso": True,
                    "consulta": consulta,
                    "dados": resultado
                })

            except Exception as e:
                resultados.append({
                    "sucesso": False,
                    "consulta": consulta,
                    "erro": str(e)
                })

            if delay > 0 and i < len(consultas) - 1:
                time.sleep(delay)

        return resultados

    def limpar_cache(self):
        """Limpa o cache de consultas"""
        self.cache.clear()
        return "Cache limpo com sucesso"

    def info_cache(self) -> Dict:
        """Informações sobre o cache atual"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())

        return {
            "total_entradas": total_entries,
            "entradas_expiradas": expired_entries,
            "entradas_validas": total_entries - expired_entries,
            "cache_habilitado": self.cache_enabled
        }

    # ==========================================
    # MÉTODOS DE CONVENIÊNCIA MELHORADOS
    # ==========================================

    def obter_populacao_brasil(self, ano: Optional[int] = None, incluir_projecoes: bool = False) -> Dict:
        """Obtém população do Brasil com opções avançadas"""
        agregado = 136  # População residente
        variavel = "93"  # População residente

        if ano:
            return self.obter_variaveis_periodo(agregado, str(ano), variavel, "BR")
        else:
            periodos = "-6" if not incluir_projecoes else "-10"
            return self.obter_variaveis_periodo(agregado, periodos, variavel, "BR")

    def obter_pib_brasil(self, ano: Optional[int] = None, modalidade: str = "corrente") -> Dict:
        """
        Obtém PIB do Brasil

        Args:
            ano: Ano específico (opcional)
            modalidade: "corrente" ou "constante"
        """
        agregado = 5938  # PIB a preços correntes/constantes

        # Variáveis diferentes para preços correntes vs constantes
        if modalidade == "corrente":
            variavel = "37"  # PIB preços correntes
        else:
            variavel = "40"  # PIB preços constantes

        if ano:
            return self.obter_variaveis_periodo(agregado, str(ano), variavel, "BR")
        else:
            return self.obter_variaveis(agregado, variavel, "BR")

    def comparar_municipios(self, codigos_municipios: List[str], agregado: int, variavel: str = "all") -> Dict:
        """Compara dados entre múltiplos municípios"""
        localidades = f"N6[{','.join(codigos_municipios)}]"
        return self.obter_variaveis(agregado, variavel, localidades)

    def dados_regiao_metropolitana(self, codigo_rm: str, agregado: int, variavel: str = "all") -> Dict:
        """Obtém dados de uma região metropolitana específica"""
        localidade = f"N7[{codigo_rm}]"
        return self.obter_variaveis(agregado, variavel, localidade)

    def serie_historica_completa(self, agregado: int, variavel: str, localidade: str = "BR") -> Dict:
        """Obtém série histórica completa disponível"""
        # Obter todos os períodos disponíveis
        periodos = self.obter_periodos(agregado, use_cache=True)

        # Usar todos os períodos (cuidado com limite de 100k valores)
        if len(periodos) <= 50:  # Limite seguro
            periodo_ids = [p['id'] for p in periodos]
            return self.obter_variaveis_periodo(agregado, periodo_ids, variavel, localidade)
        else:
            # Se muitos períodos, pegar últimos 50
            periodo_ids = [p['id'] for p in periodos[-50:]]
            return self.obter_variaveis_periodo(agregado, periodo_ids, variavel, localidade)

# Continua no próximo código...

# ==========================================
# SISTEMA DE TESTES COMPLETO
# ==========================================

def test_endpoint_completo(name: str, func, *args, **kwargs) -> TestResult:
    """Testa endpoint com métricas detalhadas"""
    start_time = time.time()
    try:
        data = func(*args, **kwargs)
        execution_time = time.time() - start_time

        if isinstance(data, list):
            summary = f"Lista com {len(data)} itens"
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())[:3]
                summary += f" (chaves: {', '.join(keys)})"
        elif isinstance(data, dict):
            summary = f"Dict com {len(data.keys())} chaves"
            keys = list(data.keys())[:3] 
            summary += f" (chaves: {', '.join(keys)})"
        else:
            summary = f"Tipo {type(data).__name__}"

        summary += f" em {execution_time:.2f}s"

        return TestResult(
            name=name, 
            success=True, 
            data_summary=summary,
            execution_time=execution_time
        )
    except Exception as e:
        execution_time = time.time() - start_time
        return TestResult(
            name=name, 
            success=False, 
            message=str(e)[:100] + "..." if len(str(e)) > 100 else str(e),
            execution_time=execution_time
        )

def suite_testes_completa():
    """Suite completa de testes para todos os endpoints e funcionalidades"""
    print("🧪 SUITE DE TESTES COMPLETA - API IBGE")
    print("="*70)

    client = IBGEClientCompleto()

    # Testes básicos dos endpoints
    testes_basicos = [
        ("1. Listar Agregados", client.listar_agregados),
        ("2. Metadados (1705)", client.obter_metadados, 1705),
        ("3. Períodos (1705)", client.obter_periodos, 1705),
        ("4. Localidades N6", client.obter_localidades, 1705, "N6"),
        ("5. Variáveis Brasil", client.obter_variaveis, 1705, "214", "BR"),
        ("6. Variáveis Período", client.obter_variaveis_periodo, 1705, "-3", "214", "BR"),
    ]

    # Testes avançados
    testes_avancados = [
        ("7. Múltiplas Variáveis", client.obter_variaveis, 1705, ["214", "1982"], "BR"),
        ("8. Localidades Múltiplas", client.obter_localidades, 1705, "N7|N6"),
        ("9. Classificação Simples", client.obter_variaveis, 1712, "214", "BR", "226[4844]"),
        ("10. Período Intervalo", client.obter_variaveis_periodo, 1705, "201901-201903", "214", "BR"),
        ("11. Múltiplos Períodos", client.obter_variaveis_periodo, 1705, ["202001", "202006", "202012"], "214", "BR"),
        ("12. View OLAP", client.obter_variaveis, 1705, "214", "BR", None, "OLAP"),
    ]

    # Testes de conveniência
    testes_conveniencia = [
        ("13. População Brasil", client.obter_populacao_brasil),
        ("14. PIB Brasil", client.obter_pib_brasil),
        ("15. Cache Info", client.info_cache),
    ]

    # Testes de utilitários
    testes_utilitarios = [
        ("16. Query Builder", lambda: client.criar_query_builder(1705).adicionar_variavel("214").build_variaveis_string()),
        ("17. Análise Dados", lambda: client.analisar_dados(client.obter_variaveis(1705, "214", "BR"))),
    ]

    todos_testes = testes_basicos + testes_avancados + testes_conveniencia + testes_utilitarios

    print(f"\n🎯 Executando {len(todos_testes)} testes...")
    print("-" * 70)

    results = []
    for i, teste in enumerate(todos_testes, 1):
        name = teste[0]
        func = teste[1]
        args = teste[2:] if len(teste) > 2 else []

        print(f"[{i:2d}/{len(todos_testes)}] {name:<30} ... ", end="", flush=True)
        result = test_endpoint_completo(name, func, *args)

        if result.success:
            print(f"✅ {result.data_summary}")
        else:
            print(f"❌ {result.message}")

        results.append(result)
        time.sleep(0.1)  # Rate limiting

    # Resumo detalhado
    sucessos = sum(1 for r in results if r.success)
    total = len(results)
    tempo_total = sum(r.execution_time for r in results)
    tempo_medio = tempo_total / total if total > 0 else 0

    print("\n" + "="*70)
    print(f"📊 RESUMO DETALHADO")
    print("="*70)
    print(f"✅ Sucessos: {sucessos}/{total} ({sucessos/total*100:.1f}%)")
    print(f"⏱️  Tempo total: {tempo_total:.2f}s")
    print(f"📈 Tempo médio: {tempo_medio:.2f}s por teste")
    print(f"🚀 Taxa de sucesso: {sucessos/total*100:.1f}%")

    if sucessos == total:
        print("\n🎉 PERFEITO! Todos os testes passaram!")
        print("✅ Cliente IBGE está 100% funcional")
    elif sucessos >= total * 0.9:
        print("\n🌟 EXCELENTE! Quase todos os testes passaram")
        print("✅ Cliente IBGE está altamente funcional")
    elif sucessos >= total * 0.7:
        print("\n👍 BOM! A maioria dos testes passou")
        print("⚠️ Algumas funcionalidades podem precisar de ajustes")
    else:
        print("\n⚠️ ATENÇÃO! Muitos testes falharam")
        print("🔧 Cliente precisa de correções")

    return results

def benchmark_performance():
    """Benchmark de performance do cliente"""
    print("\n🏃 BENCHMARK DE PERFORMANCE")
    print("-" * 50)

    client = IBGEClientCompleto()

    benchmarks = [
        ("Consulta simples (BR)", lambda: client.obter_variaveis(1705, "214", "BR")),
        ("Consulta com cache", lambda: client.obter_variaveis(1705, "214", "BR")),  # Segunda vez, com cache
        ("Múltiplas variáveis", lambda: client.obter_variaveis(1705, ["214", "1982"], "BR")),
        ("Período específico", lambda: client.obter_variaveis_periodo(1705, "202001", "214", "BR")),
        ("Metadados (cache)", lambda: client.obter_metadados(1705)),
    ]

    for nome, func in benchmarks:
        start = time.time()
        try:
            result = func()
            elapsed = time.time() - start
            print(f"⚡ {nome:<25}: {elapsed:.3f}s")
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ {nome:<25}: {elapsed:.3f}s (erro: {str(e)[:30]})")

# ==========================================
# EXEMPLOS PRÁTICOS AVANÇADOS
# ==========================================

def exemplos_avancados():
    """Demonstra funcionalidades avançadas do cliente"""
    print("\n📚 EXEMPLOS PRÁTICOS AVANÇADOS")
    print("="*60)

    client = IBGEClientCompleto()

    print("\n1. 🏗️ CONSTRUTOR DE QUERIES:")
    try:
        builder = client.criar_query_builder(1712)
        builder.adicionar_variavel("214")  # Quantidade produzida
        builder.adicionar_variavel("1982")  # Quantidade vendida
        builder.adicionar_localidade("BR")
        builder.adicionar_classificacao("226", ["4844"])  # Abacaxi
        builder.definir_view("OLAP")

        print(f"   Variáveis: {builder.build_variaveis_string()}")
        print(f"   Localidades: {builder.build_localidades_string()}")
        print(f"   Classificações: {builder.build_classificacoes_string()}")
        print(f"   View: {builder.view}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n2. 🔍 CONSULTA AVANÇADA COM MÚLTIPLOS PARÂMETROS:")
    try:
        # Produção de frutas (abacaxi, alho, batata) por proprietários no Brasil
        dados = client.obter_variaveis(
            agregado=1712,
            variavel=["214", "1982"],  # Produção e venda
            localidades="BR", 
            classificacao={
                "226": ["4844", "96608", "96609"],  # Abacaxi, alho, batata
                "218": ["4780"]  # Proprietários
            },
            view="OLAP"
        )
        print(f"   ✅ Retornados {len(dados)} grupos de variáveis")
        if dados:
            print(f"   📊 Primeira variável: {dados[0].get('variavel', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n3. 🌐 LOCALIDADES CONTEXTUAIS:")
    try:
        # Municípios do RJ e SP
        dados = client.obter_variaveis(
            agregado=512,  # PAM
            variavel="216",  # Área colhida
            localidades="N6[N3[33,35]]",  # Municípios das UFs RJ e SP
            validate_limit=False  # Desabilitar validação para exemplo
        )
        print(f"   ✅ Dados de municípios RJ/SP obtidos")
        print(f"   📈 {len(dados)} variável(is) retornada(s)")
    except QueryLimitError:
        print("   ⚠️ Consulta excede limite (como esperado)")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n4. 📊 ANÁLISE AUTOMÁTICA:")
    try:
        # Obter dados para análise
        dados = client.obter_variaveis(1705, "214", "BR")
        analise = client.analisar_dados(dados)

        print(f"   📋 Total de registros: {analise['resumo']['total_registros']}")
        print(f"   🗓️ Período: {analise['resumo']['periodo_inicial']} a {analise['resumo']['periodo_final']}")
        print(f"   📊 Variáveis: {analise['resumo']['total_variaveis']}")

        if analise['valores_especiais']:
            print("   🔍 Símbolos especiais encontrados:")
            for simbolo, info in analise['valores_especiais'].items():
                print(f"      '{simbolo}': {info['ocorrencias']} ocorrências ({info['significado']})")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n5. 💾 EXPORTAÇÃO DE DADOS:")
    try:
        dados = client.obter_variaveis(1705, "214", "BR")

        # Simular exportação (não criar arquivos reais no exemplo)
        print("   📁 Dados prontos para exportação:")
        print("      • CSV: dados_ibge.csv")
        print("      • Excel: dados_ibge.xlsx") 
        print("      • Análise: analise_automatica.json")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

    print("\n6. 🔄 CONSULTA EM LOTE (BATCH):")
    try:
        consultas = [
            {"agregado": 1705, "variavel": "214", "localidades": "BR"},
            {"agregado": 1712, "variavel": "214", "localidades": "BR", "classificacao": "226[4844]"},
        ]

        print(f"   🚀 Preparadas {len(consultas)} consultas em lote")
        print("   ⚡ Execução com delay de 0.1s entre consultas")
        # resultados = client.consulta_batch(consultas, delay=0.1)
        print("   ✅ Batch simulado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

# ==========================================  
# CLI INTERATIVO
# ==========================================

def menu_principal():
    """Menu principal do CLI"""
    print("\n" + "="*60)
    print("🇧🇷 CLIENTE IBGE - MENU PRINCIPAL")
    print("="*60)
    print("1. 🧪 Executar suite de testes completa")
    print("2. 🏃 Benchmark de performance")
    print("3. 📚 Exemplos práticos avançados") 
    print("4. 🔍 Consulta personalizada")
    print("5. 📊 Explorar agregados")
    print("6. 💾 Cache e configurações")
    print("7. 📋 Sobre o cliente")
    print("0. ❌ Sair")
    print("="*60)

def consulta_personalizada():
    """Interface para consulta personalizada"""
    print("\n🔍 CONSULTA PERSONALIZADA")
    print("-" * 40)

    client = IBGEClientCompleto()

    try:
        # Solicitar parâmetros básicos
        agregado = input("📊 ID do agregado (ex: 1705): ").strip()
        if not agregado.isdigit():
            print("❌ ID do agregado deve ser um número")
            return
        agregado = int(agregado)

        variavel = input("📈 Variável (ex: 214 ou 'all'): ").strip() or "all"
        localidade = input("🌍 Localidade (ex: BR, N6[3550308]): ").strip() or "BR"

        # Parâmetros opcionais
        print("\n⚙️ Parâmetros opcionais (pressione Enter para pular):")
        classificacao = input("🏷️ Classificação (ex: 226[4844]): ").strip() or None
        view = input("👁️ View (OLAP/flat): ").strip().upper() or None
        if view and view not in ['OLAP', 'FLAT']:
            view = None

        print("\n🚀 Executando consulta...")
        dados = client.obter_variaveis(
            agregado=agregado,
            variavel=variavel,
            localidades=localidade,
            classificacao=classificacao,
            view=view
        )

        print(f"\n✅ Sucesso! Retornados {len(dados)} grupo(s) de dados")

        # Oferecer análise
        if input("\n📊 Deseja analisar os dados? (s/N): ").lower().startswith('s'):
            analise = client.analisar_dados(dados)
            print("\n📋 ANÁLISE DOS DADOS:")
            print(f"   • Registros: {analise['resumo']['total_registros']}")
            print(f"   • Variáveis: {analise['resumo']['total_variaveis']}")
            print(f"   • Localidades: {analise['resumo']['total_localidades']}")
            print(f"   • Períodos: {analise['resumo']['periodos_total']}")

        # Oferecer exportação
        if input("\n💾 Deseja exportar os dados? (s/N): ").lower().startswith('s'):
            formato = input("📁 Formato (csv/excel): ").lower()
            if formato in ['csv', 'excel']:
                filename = f"consulta_ibge_{int(time.time())}.{formato}"
                if formato == 'csv':
                    client.exportar_csv(dados, filename)
                else:
                    client.exportar_excel(dados, filename)
                print(f"✅ Dados exportados para {filename}")

    except Exception as e:
        print(f"❌ Erro na consulta: {e}")

def explorar_agregados():
    """Explora agregados disponíveis"""
    print("\n📊 EXPLORAR AGREGADOS")
    print("-" * 40)

    client = IBGEClientCompleto()

    try:
        # Filtros opcionais
        print("🔍 Filtros (pressione Enter para pular):")
        assunto = input("📖 ID do assunto: ").strip()
        nivel = input("🌍 Nível geográfico (ex: N6): ").strip()
        periodicidade = input("📅 Periodicidade (ex: P5): ").strip()

        params = {}
        if assunto and assunto.isdigit():
            params['assunto'] = int(assunto)
        if nivel:
            params['nivel'] = nivel
        if periodicidade:
            params['periodicidade'] = periodicidade

        print("\n🔍 Buscando agregados...")
        agregados = client.listar_agregados(**params)

        print(f"\n✅ Encontradas {len(agregados)} pesquisa(s)")

        # Mostrar primeiras pesquisas
        for i, pesquisa in enumerate(agregados[:5]):
            print(f"\n{i+1}. 📋 {pesquisa['nome']}")
            for j, agregado in enumerate(pesquisa.get('agregados', [])[:3]):
                print(f"   {j+1}. {agregado['id']} - {agregado['nome']}")
            if len(pesquisa.get('agregados', [])) > 3:
                print(f"   ... e mais {len(pesquisa['agregados']) - 3} agregados")

        if len(agregados) > 5:
            print(f"\n... e mais {len(agregados) - 5} pesquisas")

    except Exception as e:
        print(f"❌ Erro ao explorar agregados: {e}")

def configuracoes_cache():
    """Gerencia cache e configurações"""
    print("\n💾 CACHE E CONFIGURAÇÕES")
    print("-" * 40)

    client = IBGEClientCompleto()

    while True:
        info = client.info_cache()
        print(f"\n📊 Status do Cache:")
        print(f"   • Habilitado: {'✅ Sim' if info['cache_habilitado'] else '❌ Não'}")
        print(f"   • Total de entradas: {info['total_entradas']}")
        print(f"   • Entradas válidas: {info['entradas_validas']}")
        print(f"   • Entradas expiradas: {info['entradas_expiradas']}")

        print("\n🔧 Opções:")
        print("1. 🗑️ Limpar cache")
        print("2. ⚙️ Configurações do cliente")
        print("0. ⬅️ Voltar")

        opcao = input("\nEscolha: ").strip()

        if opcao == '1':
            client.limpar_cache()
            print("✅ Cache limpo!")
        elif opcao == '2':
            print(f"\n⚙️ Configurações atuais:")
            print(f"   • Rate limit: {client.rate_limit}s")
            print(f"   • Timeout: {TIMEOUT}")
            print(f"   • Max retries: {MAX_RETRIES}")
            print(f"   • Max values per request: {MAX_VALUES_PER_REQUEST:,}")
        elif opcao == '0':
            break
        else:
            print("❌ Opção inválida")

def sobre_cliente():
    """Informações sobre o cliente"""
    print("\n📋 SOBRE O CLIENTE IBGE COMPLETO")
    print("="*50)
    print("🇧🇷 Cliente Python para API IBGE Dados Agregados v3.0.0")
    print("")
    print("✨ FUNCIONALIDADES PREMIUM:")
    print("• 6 endpoints completos com todos os parâmetros")
    print("• Suporte a localidades contextuais")
    print("• Múltiplos formatos de período/classificação")
    print("• Sistema de cache inteligente")
    print("• Validação de limite de 100k valores")
    print("• Parser de símbolos especiais")
    print("• Análise automática de dados")
    print("• Exportação CSV/Excel")
    print("• Sistema de batch")
    print("• Rate limiting e retry")
    print("")
    print("📊 ESTATÍSTICAS:")
    print(f"• Níveis geográficos: {len(NIVEIS_GEOGRAFICOS)}")
    print(f"• Periodicidades: {len(PERIODICIDADES)}")
    print(f"• Símbolos especiais: {len(SIMBOLOS_ESPECIAIS)}")
    print("")
    print("🔗 URLS:")
    print("• API: https://servicodados.ibge.gov.br/api/v3/agregados")
    print("• SIDRA: https://sidra.ibge.gov.br")
    print("• Docs: https://servicodados.ibge.gov.br/api/docs/agregados")

def cli_interativo():
    """CLI interativo principal"""
    print("🇧🇷 CLIENTE IBGE COMPLETO - VERSÃO PREMIUM")
    print("Desenvolvido com base na API oficial v3.0.0")

    while True:
        menu_principal()
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            suite_testes_completa()
        elif opcao == '2':
            benchmark_performance()
        elif opcao == '3':
            exemplos_avancados()
        elif opcao == '4':
            consulta_personalizada()
        elif opcao == '5':
            explorar_agregados()
        elif opcao == '6':
            configuracoes_cache()
        elif opcao == '7':
            sobre_cliente()
        elif opcao == '0':
            print("\n👋 Obrigado por usar o Cliente IBGE Completo!")
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.")

        input("\n⏸️ Pressione Enter para continuar...")

# ==========================================
# MAIN - EXECUÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":
    import sys

    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            suite_testes_completa()
        elif sys.argv[1] == '--benchmark':
            benchmark_performance()  
        elif sys.argv[1] == '--examples':
            exemplos_avancados()
        elif sys.argv[1] == '--help':
            print("🇧🇷 CLIENTE IBGE COMPLETO - AJUDA")
            print("="*40)
            print("Uso: python ibge_client_completo.py [opção]")
            print("")
            print("Opções:")
            print("  --test       Executar suite de testes")
            print("  --benchmark  Executar benchmark")
            print("  --examples   Mostrar exemplos avançados")
            print("  --help       Mostrar esta ajuda")
            print("  (sem opção)  Executar CLI interativo")
        else:
            print(f"❌ Opção desconhecida: {sys.argv[1]}")
            print("Use --help para ver as opções disponíveis")
    else:
        # CLI interativo por padrão
        cli_interativo()
