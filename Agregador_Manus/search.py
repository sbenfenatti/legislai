from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SearchRequest(BaseModel):
    """Modelo para requisição de busca"""
    query: str = Field(..., min_length=1, max_length=500, description="Termo de busca")
    apis: Optional[List[str]] = Field(None, description="APIs específicas para buscar")
    categories: Optional[List[str]] = Field(None, description="Categorias de dados")
    date_start: Optional[datetime] = Field(None, description="Data inicial do período")
    date_end: Optional[datetime] = Field(None, description="Data final do período")
    page: int = Field(default=1, ge=1, description="Página dos resultados")
    limit: int = Field(default=20, ge=1, le=100, description="Itens por página")

class SearchResult(BaseModel):
    """Modelo para resultado individual de busca"""
    id: str = Field(..., description="ID único do resultado")
    source: str = Field(..., description="Fonte/API do resultado")
    category: str = Field(..., description="Categoria do dado")
    title: str = Field(..., description="Título do resultado")
    description: str = Field(..., description="Descrição do resultado")
    data: Dict[str, Any] = Field(..., description="Dados específicos do resultado")
    relevance: float = Field(..., ge=0, le=1, description="Relevância do resultado (0-1)")
    timestamp: datetime = Field(..., description="Data/hora do resultado")
    url: Optional[str] = Field(None, description="URL para mais detalhes")

class SearchResponse(BaseModel):
    """Modelo para resposta de busca"""
    results: List[SearchResult] = Field(..., description="Lista de resultados")
    total: int = Field(..., ge=0, description="Total de resultados encontrados")
    page: int = Field(..., ge=1, description="Página atual")
    limit: int = Field(..., ge=1, description="Itens por página")
    has_more: bool = Field(..., description="Indica se há mais resultados")
    query: str = Field(..., description="Termo de busca utilizado")
    apis_searched: List[str] = Field(..., description="APIs consultadas")
    search_time_ms: int = Field(..., description="Tempo de busca em milissegundos")

class APIStatus(str, Enum):
    """Status das APIs"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"

class APIInfo(BaseModel):
    """Informações sobre uma API"""
    name: str = Field(..., description="Nome da API")
    key: str = Field(..., description="Chave identificadora da API")
    description: str = Field(..., description="Descrição da API")
    base_url: str = Field(..., description="URL base da API")
    status: APIStatus = Field(..., description="Status atual da API")
    enabled: bool = Field(..., description="Se a API está habilitada")
    token_required: bool = Field(..., description="Se requer token de autenticação")
    rate_limit: Dict[str, int] = Field(..., description="Limites de taxa")
    categories: Optional[List[str]] = Field(None, description="Categorias disponíveis")
    last_check: Optional[datetime] = Field(None, description="Última verificação de status")

class CategoryInfo(BaseModel):
    """Informações sobre uma categoria"""
    key: str = Field(..., description="Chave da categoria")
    name: str = Field(..., description="Nome da categoria")
    description: str = Field(..., description="Descrição da categoria")
    apis: List[str] = Field(..., description="APIs que oferecem esta categoria")
    count: Optional[int] = Field(None, description="Número de endpoints/dados disponíveis")

class HealthCheck(BaseModel):
    """Modelo para health check"""
    status: str = Field(..., description="Status geral do sistema")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da aplicação")
    apis: Dict[str, APIStatus] = Field(..., description="Status de cada API")
    cache_status: str = Field(..., description="Status do cache Redis")
    uptime_seconds: int = Field(..., description="Tempo de atividade em segundos")

class ErrorResponse(BaseModel):
    """Modelo para respostas de erro"""
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp do erro")
    request_id: Optional[str] = Field(None, description="ID da requisição para rastreamento")

