"""
Serviço de agregação de dados de múltiplas APIs
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from config import settings

class DataAggregator:
    """Classe responsável por agregar dados de múltiplas APIs"""
    
    def __init__(self):
        self.fontes_utilizadas = []
        self.timeout = settings.api_timeout
    
    async def buscar_dados_por_area(self, area_tematica: str, ambito: str) -> List[Dict[str, Any]]:
        """
        Busca dados relevantes baseados na área temática
        """
        dados_agregados = []
        self.fontes_utilizadas = []
        
        # Mapear área temática para fontes de dados
        fontes_por_area = {
            "saude": ["ibge_saude", "datasus", "brasil_api_demograficos"],
            "educacao": ["ibge_educacao", "brasil_api_demograficos"],
            "seguranca": ["ibge_violencia", "brasil_api_demograficos"],
            "economia": ["ibge_economia", "brasil_api_economicos"],
            "meio_ambiente": ["ibge_ambiente", "brasil_api_demograficos"],
            "transporte": ["ibge_transporte", "brasil_api_demograficos"],
            "habitacao": ["ibge_habitacao", "brasil_api_demograficos"],
            "assistencia_social": ["ibge_social", "brasil_api_demograficos"]
        }
        
        area_normalizada = area_tematica.lower().replace(" ", "_")
        fontes = fontes_por_area.get(area_normalizada, ["ibge_geral", "brasil_api_demograficos"])
        
        # Buscar dados de cada fonte
        tasks = []
        for fonte in fontes:
            if fonte.startswith("ibge"):
                tasks.append(self._buscar_dados_ibge(fonte, ambito))
            elif fonte.startswith("datasus"):
                tasks.append(self._buscar_dados_datasus(fonte, ambito))
            elif fonte.startswith("brasil_api"):
                tasks.append(self._buscar_dados_brasil_api(fonte, ambito))
        
        # Executar buscas em paralelo
        resultados = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        for i, resultado in enumerate(resultados):
            if not isinstance(resultado, Exception) and resultado:
                dados_agregados.extend(resultado)
        
        return dados_agregados
    
    async def _buscar_dados_ibge(self, fonte: str, ambito: str) -> List[Dict[str, Any]]:
        """Busca dados específicos do IBGE"""
        dados = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if fonte == "ibge_saude":
                    # Buscar dados de saúde do IBGE
                    response = await client.get(f"{settings.ibge_base_url}/v3/agregados/4057/periodos/-1/variaveis")
                    if response.status_code == 200:
                        data = response.json()
                        dados.append({
                            "fonte": "IBGE - Pesquisa Nacional de Saúde",
                            "tipo": "estatistica_saude",
                            "dados": data,
                            "descricao": "Dados sobre acesso e utilização dos serviços de saúde"
                        })
                        self.fontes_utilizadas.append("IBGE")
                
                elif fonte == "ibge_geral":
                    # Buscar dados demográficos gerais
                    response = await client.get(f"{settings.ibge_base_url}/v1/localidades/estados")
                    if response.status_code == 200:
                        estados = response.json()
                        dados.append({
                            "fonte": "IBGE - Localidades",
                            "tipo": "demografico",
                            "dados": {"total_estados": len(estados), "estados": estados[:5]},  # Limitar para exemplo
                            "descricao": "Dados sobre divisão territorial brasileira"
                        })
                        self.fontes_utilizadas.append("IBGE")
                
        except Exception as e:
            print(f"Erro ao buscar dados IBGE ({fonte}): {e}")
        
        return dados
    
    async def _buscar_dados_datasus(self, fonte: str, ambito: str) -> List[Dict[str, Any]]:
        """Busca dados do DataSUS (simulado)"""
        dados = []
        
        # Dados simulados do DataSUS
        if fonte == "datasus":
            dados.append({
                "fonte": "DataSUS - CNES",
                "tipo": "estabelecimentos_saude",
                "dados": {
                    "ubs_total_brasil": 45000,
                    "ubs_com_informatizacao": 31500,
                    "percentual_informatizacao": 70,
                    "tempo_medio_espera_dias": 45,
                    "taxa_absenteismo_percent": 25
                },
                "descricao": "Dados sobre estabelecimentos de saúde e indicadores de atendimento"
            })
            self.fontes_utilizadas.append("DataSUS")
        
        return dados
    
    async def _buscar_dados_brasil_api(self, fonte: str, ambito: str) -> List[Dict[str, Any]]:
        """Busca dados da Brasil API"""
        dados = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if fonte == "brasil_api_demograficos":
                    # Buscar dados de feriados como exemplo de dados estruturados
                    response = await client.get(f"{settings.brasil_api_base_url}/v1/holidays/2024")
                    if response.status_code == 200:
                        feriados = response.json()
                        dados.append({
                            "fonte": "Brasil API - Feriados Nacionais",
                            "tipo": "calendario_oficial",
                            "dados": {"total_feriados_2024": len(feriados), "feriados": feriados[:3]},
                            "descricao": "Calendário oficial de feriados nacionais"
                        })
                        self.fontes_utilizadas.append("Brasil API")
                
                elif fonte == "brasil_api_economicos":
                    # Buscar dados de bancos como proxy para dados econômicos
                    response = await client.get(f"{settings.brasil_api_base_url}/v1/banks")
                    if response.status_code == 200:
                        bancos = response.json()
                        dados.append({
                            "fonte": "Brasil API - Sistema Bancário",
                            "tipo": "economia_financeiro",
                            "dados": {"total_bancos": len(bancos), "principais_bancos": bancos[:5]},
                            "descricao": "Dados sobre o sistema bancário brasileiro"
                        })
                        self.fontes_utilizadas.append("Brasil API")
        
        except Exception as e:
            print(f"Erro ao buscar dados Brasil API ({fonte}): {e}")
        
        return dados
    
    async def buscar_dados_especificos(self, consultas: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Busca dados específicos baseados em consultas customizadas
        """
        dados_especificos = []
        
        for consulta in consultas:
            api = consulta.get("api")
            endpoint = consulta.get("endpoint")
            parametros = consulta.get("parametros", {})
            
            try:
                if api == "ibge":
                    dados = await self._consultar_ibge_customizado(endpoint, parametros)
                elif api == "brasil_api":
                    dados = await self._consultar_brasil_api_customizado(endpoint, parametros)
                else:
                    continue
                
                if dados:
                    dados_especificos.append(dados)
            
            except Exception as e:
                print(f"Erro na consulta específica {api}/{endpoint}: {e}")
        
        return dados_especificos
    
    async def _consultar_ibge_customizado(self, endpoint: str, parametros: Dict) -> Optional[Dict[str, Any]]:
        """Consulta customizada ao IBGE"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{settings.ibge_base_url}/{endpoint}"
                response = await client.get(url, params=parametros)
                response.raise_for_status()
                
                return {
                    "fonte": f"IBGE - {endpoint}",
                    "tipo": "consulta_customizada",
                    "dados": response.json(),
                    "parametros": parametros
                }
        except Exception:
            return None
    
    async def _consultar_brasil_api_customizado(self, endpoint: str, parametros: Dict) -> Optional[Dict[str, Any]]:
        """Consulta customizada à Brasil API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{settings.brasil_api_base_url}/{endpoint}"
                response = await client.get(url, params=parametros)
                response.raise_for_status()
                
                return {
                    "fonte": f"Brasil API - {endpoint}",
                    "tipo": "consulta_customizada",
                    "dados": response.json(),
                    "parametros": parametros
                }
        except Exception:
            return None
    
    def get_fontes_utilizadas(self) -> List[str]:
        """Retorna lista de fontes utilizadas na última consulta"""
        return list(set(self.fontes_utilizadas))
    
    def limpar_cache_fontes(self):
        """Limpa o cache de fontes utilizadas"""
        self.fontes_utilizadas = []

