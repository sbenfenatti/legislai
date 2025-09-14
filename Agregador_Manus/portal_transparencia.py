from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
from app.services.base_service import BaseAPIService
from app.models.search import SearchResult
from app.config import settings

logger = structlog.get_logger()

class PortalTransparenciaService(BaseAPIService):
    """Serviço para integração com a API do Portal da Transparência"""
    
    def __init__(self):
        super().__init__(
            name="Portal da Transparência",
            base_url=settings.portal_transparencia_base_url,
            api_key=settings.portal_transparencia_api_key,
            rate_limit_per_minute=90,
            timeout=30
        )
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Headers de autenticação para o Portal da Transparência"""
        if self.api_key:
            return {"chave-api-dados": self.api_key}
        return {}
    
    async def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[SearchResult]:
        """Busca unificada no Portal da Transparência"""
        results = []
        
        # Determina quais endpoints buscar baseado na query
        endpoints_to_search = self._determine_endpoints(query, filters)
        
        for endpoint_info in endpoints_to_search:
            try:
                endpoint_results = await self._search_endpoint(
                    endpoint_info, query, filters, page, limit
                )
                results.extend(endpoint_results)
            except Exception as e:
                logger.error(
                    "Error searching endpoint",
                    endpoint=endpoint_info["path"],
                    error=str(e)
                )
        
        # Ordena por relevância
        results.sort(key=lambda x: x.relevance, reverse=True)
        
        # Limita o número de resultados
        return results[:limit]
    
    def _determine_endpoints(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Determina quais endpoints buscar baseado na query e filtros"""
        query_lower = query.lower()
        endpoints = []
        
        # Mapeamento de termos para endpoints
        endpoint_mapping = {
            "despesa": [
                {"path": "/despesas/por-orgao", "category": "despesas"},
                {"path": "/despesas/por-favorecido", "category": "despesas"}
            ],
            "servidor": [
                {"path": "/servidores", "category": "servidores"},
                {"path": "/servidores/remuneracao", "category": "servidores"}
            ],
            "viagem": [
                {"path": "/viagens", "category": "viagens"}
            ],
            "licitacao": [
                {"path": "/licitacoes", "category": "licitacoes"}
            ],
            "contrato": [
                {"path": "/contratos", "category": "contratos"}
            ],
            "bolsa": [
                {"path": "/novo-bolsa-familia-por-municipio", "category": "beneficios_sociais"}
            ],
            "auxilio": [
                {"path": "/auxilio-emergencial-por-municipio", "category": "beneficios_sociais"}
            ],
            "bpc": [
                {"path": "/bpc-por-municipio", "category": "beneficios_sociais"}
            ],
            "sancao": [
                {"path": "/ceis", "category": "sancoes"},
                {"path": "/cnep", "category": "sancoes"}
            ],
            "cartao": [
                {"path": "/cartoes", "category": "cartoes"}
            ],
            "emenda": [
                {"path": "/emendas", "category": "emendas"}
            ]
        }
        
        # Busca endpoints relevantes
        for term, term_endpoints in endpoint_mapping.items():
            if term in query_lower:
                endpoints.extend(term_endpoints)
        
        # Se não encontrou endpoints específicos, usa alguns padrão
        if not endpoints:
            endpoints = [
                {"path": "/despesas/por-orgao", "category": "despesas"},
                {"path": "/servidores", "category": "servidores"},
                {"path": "/licitacoes", "category": "licitacoes"}
            ]
        
        return endpoints
    
    async def _search_endpoint(
        self,
        endpoint_info: Dict[str, Any],
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[SearchResult]:
        """Busca em um endpoint específico"""
        endpoint = endpoint_info["path"]
        category = endpoint_info["category"]
        
        # Prepara parâmetros da requisição
        params = {
            "pagina": page,
            "itensPorPagina": min(limit, 50)  # Limite máximo da API
        }
        
        # Adiciona filtros de data se disponíveis
        if filters:
            if filters.get("date_start"):
                params["dataInicio"] = filters["date_start"].strftime("%d/%m/%Y")
            if filters.get("date_end"):
                params["dataFim"] = filters["date_end"].strftime("%d/%m/%Y")
        
        # Faz a requisição
        response_data = await self._make_request(endpoint, params=params)
        
        if not response_data:
            return []
        
        # Processa os resultados
        results = []
        items = response_data if isinstance(response_data, list) else response_data.get("data", [])
        
        for item in items:
            if isinstance(item, dict):
                result = self._process_item(item, category, query)
                if result and result.relevance > 0:
                    results.append(result)
        
        return results
    
    def _process_item(
        self, 
        item: Dict[str, Any], 
        category: str, 
        query: str
    ) -> Optional[SearchResult]:
        """Processa um item individual da resposta da API"""
        try:
            # Extrai informações básicas do item
            title = self._extract_title(item, category)
            description = self._extract_description(item, category)
            
            if not title:
                return None
            
            # Calcula relevância
            relevance = self._calculate_relevance(
                query, 
                f"{title} {description}"
            )
            
            # Cria ID único
            result_id = f"portal_{category}_{hash(str(item))}"
            
            return self._create_search_result(
                result_id=result_id,
                category=category,
                title=title,
                description=description,
                data=item,
                relevance=relevance
            )
            
        except Exception as e:
            logger.error("Error processing item", item=item, error=str(e))
            return None
    
    def _extract_title(self, item: Dict[str, Any], category: str) -> str:
        """Extrai título do item baseado na categoria"""
        if category == "despesas":
            return (
                item.get("nomeOrgao") or 
                item.get("nomeFavorecido") or 
                f"Despesa - {item.get('valor', 'N/A')}"
            )
        elif category == "servidores":
            return (
                item.get("nome") or 
                f"Servidor - {item.get('cpf', 'N/A')}"
            )
        elif category == "viagens":
            return (
                f"Viagem - {item.get('destino', 'N/A')}" or
                f"Viagem de {item.get('nome', 'N/A')}"
            )
        elif category == "licitacoes":
            return (
                item.get("objeto") or
                f"Licitação {item.get('numero', 'N/A')}"
            )
        elif category == "contratos":
            return (
                item.get("objeto") or
                f"Contrato {item.get('numero', 'N/A')}"
            )
        elif category == "beneficios_sociais":
            return (
                f"Benefício - {item.get('municipio', 'N/A')}" or
                f"Benefício - {item.get('valor', 'N/A')}"
            )
        elif category == "sancoes":
            return (
                item.get("nome") or
                item.get("razaoSocial") or
                f"Sanção - {item.get('cnpj', item.get('cpf', 'N/A'))}"
            )
        else:
            # Tenta extrair um título genérico
            for field in ["nome", "titulo", "objeto", "descricao"]:
                if item.get(field):
                    return str(item[field])[:100]
            return f"Item {category}"
    
    def _extract_description(self, item: Dict[str, Any], category: str) -> str:
        """Extrai descrição do item baseado na categoria"""
        if category == "despesas":
            parts = []
            if item.get("valor"):
                parts.append(f"Valor: R$ {item['valor']}")
            if item.get("dataDocumento"):
                parts.append(f"Data: {item['dataDocumento']}")
            return " | ".join(parts)
        
        elif category == "servidores":
            parts = []
            if item.get("cargo"):
                parts.append(f"Cargo: {item['cargo']}")
            if item.get("orgao"):
                parts.append(f"Órgão: {item['orgao']}")
            return " | ".join(parts)
        
        elif category == "viagens":
            parts = []
            if item.get("periodo"):
                parts.append(f"Período: {item['periodo']}")
            if item.get("valor"):
                parts.append(f"Valor: R$ {item['valor']}")
            return " | ".join(parts)
        
        else:
            # Descrição genérica
            desc_fields = ["descricao", "observacao", "detalhamento"]
            for field in desc_fields:
                if item.get(field):
                    return str(item[field])[:200]
            
            # Se não tem descrição específica, monta uma genérica
            return f"Dados do {category} - {len(item)} campos disponíveis"

