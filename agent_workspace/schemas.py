"""
Modelos Pydantic para validação de dados
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Modelos base
class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# IBGE
class LocalidadeIBGE(BaseModel):
    id: int
    nome: str
    microrregiao: Optional[Dict[str, Any]] = None
    mesorregiao: Optional[Dict[str, Any]] = None
    UF: Optional[Dict[str, Any]] = None
    regiao: Optional[Dict[str, Any]] = None

class AgregadoIBGE(BaseModel):
    id: str
    nome: str
    URL: str
    pesquisa: str
    assunto: str

# Brasil API
class EnderecoResponse(BaseModel):
    cep: str
    state: str
    city: str
    neighborhood: str
    street: str
    service: Optional[str] = None

class EmpresaResponse(BaseModel):
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    uf: str
    municipio: str
    logradouro: str
    numero: str
    cep: str
    situacao: str

# Análise legislativa
class PropostaLegislativa(BaseModel):
    objetivo: str = Field(..., description="Objetivo principal do projeto de lei")
    ambito: str = Field(..., description="Âmbito do projeto (Municipal, Estadual, Federal)")
    area_tematica: str = Field(..., description="Área temática (Saúde, Educação, etc.)")
    justificativa: Optional[str] = None
    solucao_proposta: Optional[str] = None
    resultados_esperados: Optional[str] = None

class AnaliseResponse(BaseModel):
    proposta: PropostaLegislativa
    dados_encontrados: List[Dict[str, Any]]
    fontes_utilizadas: List[str]
    justificativa_gerada: str
    comissoes_relevantes: List[str]
    probabilidade_aprovacao: Optional[float] = None

class SimulacaoTramitacao(BaseModel):
    comissoes: List[Dict[str, Any]]
    tempo_estimado: str
    observacoes: List[str]

class RelatorioRequest(BaseModel):
    tipo: str = Field(..., description="Tipo do relatório (completo, resumido, etc.)")
    dados: Dict[str, Any] = Field(..., description="Dados para o relatório")
    formato: str = Field(default="json", description="Formato de saída (json, pdf, html)")

class RelatorioResponse(BaseModel):
    id: str
    tipo: str
    formato: str
    url_download: Optional[str] = None
    conteudo: Optional[Dict[str, Any]] = None
    criado_em: datetime = Field(default_factory=datetime.now)

# Redes sociais
class SocialMediaSearchRequest(BaseModel):
    query: str = Field(..., description="Termo de busca")
    platforms: Optional[List[str]] = Field(default=None, description="Plataformas: twitter, youtube, reddit, trends")
    timeframe: Optional[str] = Field(default="7d", description="Janela de tempo: 7d, 30d...")

class SocialMediaResult(BaseModel):
    platform: str
    content: str
    author: str
    engagement: Dict[str, Any]
    sentiment_score: Optional[float] = None
    hashtags: List[str]
    posted_at: datetime
    source_url: str

# Pesquisa acadêmica
class AcademicPaper(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    journal: Optional[str] = None
    # Campos adicionais usados pelos serviços
    repository: Optional[str] = None
    year: Optional[int] = None
    qualis_level: Optional[str] = None
    qualis_rating: Optional[str] = None
    relevance_score: Optional[float] = None
    citation_count: Optional[int] = None
    citations: Optional[int] = None
    keywords: Optional[List[str]] = None
    pdf_url: Optional[str] = None
    published_date: Optional[datetime] = None

class AcademicSearchRequest(BaseModel):
    query: str = Field(..., description="Termo de busca")
    repositories: Optional[List[str]] = Field(default=["scielo", "pubmed"], description="Repositórios")
    min_qualis_level: Optional[str] = Field(default="B2", description="Filtro Qualis mínimo")
    max_results: Optional[int] = Field(default=20, description="Limite de resultados")
    # Compatibilidade retroativa
    databases: Optional[List[str]] = None
    qualis_filter: Optional[str] = None

# Notícias
class NewsArticle(BaseModel):
    title: str
    url: str
    source: str
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    bias_score: Optional[float] = None
    credibility_score: Optional[float] = None
    political_spectrum: Optional[str] = None
    tags: Optional[List[str]] = None
    sentiment_score: Optional[float] = None

class NewsSearchRequest(BaseModel):
    query: str = Field(..., description="Termo de busca")
    sources: Optional[List[str]] = Field(default=[], description="Fontes específicas")
    political_spectrum: Optional[str] = Field(default=None, description="hegemonica, esquerda, direita, internacional")
    timeframe: Optional[str] = Field(default="30d", description="Período de busca")
    max_results: Optional[int] = Field(default=50, description="Limite de resultados")

# Busca geral
class GeneralSearchRequest(BaseModel):
    query: str = Field(..., description="Termo de busca")
    site_types: Optional[List[str]] = Field(default=None, description="Tipos de site: ong, instituto, fundacao...")
    file_types: Optional[List[str]] = Field(default=None, description="Tipos de arquivo: pdf, xlsx...")
    max_results: Optional[int] = Field(default=30, description="Limite de resultados")
    # Compatibilidade retroativa
    search_type: Optional[str] = None
    sources: Optional[List[str]] = None
    limit: Optional[int] = None

class GeneralSearchResult(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    description: Optional[str] = None
    source_type: str
    organization: Optional[str] = None
    file_type: Optional[str] = None
    published_date: Optional[datetime] = None
    relevance_score: Optional[float] = None
    content_type: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[List[str]] = None
    last_updated: Optional[datetime] = None

# Modelo unificado de pesquisa
class ResearchRequest(BaseModel):
    query: str
    categories: List[str]
    filters: Optional[Dict[str, Any]] = Field(default={})
    user_type: Optional[str] = Field(default="citizen")

class UnifiedSearchResponse(BaseModel):
    query: str
    categories_searched: List[str]
    results: Dict[str, List[Dict[str, Any]]]
    summary: Dict[str, Any]
    total_results: int
    search_timestamp: datetime = Field(default_factory=datetime.now)
