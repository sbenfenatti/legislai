import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
from app.models.search import SearchResult
from app.core.cache import CacheService

logger = structlog.get_logger()

class BaseAPIService:
    """Classe base para serviços de integração com APIs"""
    
    def __init__(
        self, 
        name: str,
        base_url: str, 
        api_key: Optional[str] = None,
        rate_limit_per_minute: int = 60,
        timeout: int = 30
    ):
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.rate_limit_per_minute = rate_limit_per_minute
        self.timeout = timeout
        
        # Cliente HTTP assíncrono
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Rate limiting simples
        self._last_requests = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _check_rate_limit(self) -> bool:
        """Verifica se pode fazer uma nova requisição"""
        now = datetime.now()
        # Remove requisições antigas (mais de 1 minuto)
        self._last_requests = [
            req_time for req_time in self._last_requests 
            if (now - req_time).total_seconds() < 60
        ]
        
        # Verifica se excedeu o limite
        if len(self._last_requests) >= self.rate_limit_per_minute:
            return False
        
        # Adiciona a requisição atual
        self._last_requests.append(now)
        return True
    
    async def _make_request(
        self, 
        endpoint: str, 
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Faz uma requisição HTTP para a API"""
        
        # Verifica rate limiting
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded", service=self.name)
            return None
        
        # Prepara headers
        request_headers = headers or {}
        if self.api_key:
            # Cada API pode ter um formato diferente de autenticação
            request_headers.update(self._get_auth_headers())
        
        # URL completa
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(
                "Making API request",
                service=self.name,
                method=method,
                url=url,
                params=params
            )
            
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                headers=request_headers,
                json=data
            )
            
            # Log da resposta
            logger.debug(
                "API response received",
                service=self.name,
                status_code=response.status_code,
                response_time=response.elapsed.total_seconds()
            )
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("API rate limit hit", service=self.name)
                return None
            else:
                logger.error(
                    "API request failed",
                    service=self.name,
                    status_code=response.status_code,
                    response_text=response.text[:500]
                )
                return None
                
        except httpx.TimeoutException:
            logger.error("API request timeout", service=self.name, url=url)
            return None
        except Exception as e:
            logger.error("API request error", service=self.name, error=str(e))
            return None
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Retorna headers de autenticação (implementar em subclasses)"""
        return {}
    
    async def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[SearchResult]:
        """Método abstrato para busca (implementar em subclasses)"""
        raise NotImplementedError("Subclasses must implement search method")
    
    async def health_check(self) -> bool:
        """Verifica se a API está funcionando"""
        try:
            # Faz uma requisição simples para testar a API
            response = await self._make_request("", method="GET")
            return response is not None
        except Exception:
            return False
    
    def _create_search_result(
        self,
        result_id: str,
        category: str,
        title: str,
        description: str,
        data: Dict[str, Any],
        relevance: float = 1.0,
        url: Optional[str] = None
    ) -> SearchResult:
        """Cria um objeto SearchResult padronizado"""
        return SearchResult(
            id=result_id,
            source=self.name,
            category=category,
            title=title,
            description=description,
            data=data,
            relevance=relevance,
            timestamp=datetime.now(),
            url=url
        )
    
    def _calculate_relevance(self, query: str, text: str) -> float:
        """Calcula relevância simples baseada na presença do termo de busca"""
        if not query or not text:
            return 0.0
        
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Relevância baseada na presença e frequência do termo
        if query_lower in text_lower:
            # Conta quantas vezes o termo aparece
            count = text_lower.count(query_lower)
            # Normaliza pela quantidade de palavras
            words = len(text_lower.split())
            relevance = min(count / max(words, 1), 1.0)
            return relevance
        
        # Verifica palavras individuais
        query_words = query_lower.split()
        text_words = text_lower.split()
        matches = sum(1 for word in query_words if word in text_words)
        
        if matches > 0:
            return matches / len(query_words) * 0.5  # Relevância menor para matches parciais
        
        return 0.0

