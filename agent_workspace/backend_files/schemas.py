"""
Modelos Pydantic para validação de dados
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Modelos base
class APIResponse(BaseModel):
    """Resposta padrão da API"""
    success: bool = True
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseModel):
    """Resposta de erro da API"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Modelos para IBGE
class LocalidadeIBGE(BaseModel):
    """Modelo para localidades do IBGE"""
    id: int
    nome: str
    microrregiao: Optional[Dict[str, Any]] = None
    mesorregiao: Optional[Dict[str, Any]] = None
    UF: Optional[Dict[str, Any]] = None
    regiao: Optional[Dict[str, Any]] = None

class AgregadoIBGE(BaseModel):
    """Modelo para agregados do IBGE"""
    id: str
    nome: str
    URL: str
    pesquisa: str
    assunto: str

# Modelos para Brasil API
class EnderecoResponse(BaseModel):
    """Resposta de consulta de CEP"""
    cep: str
    state: str
    city: str
    neighborhood: str
    street: str
    service: Optional[str] = None

class EmpresaResponse(BaseModel):
    """Resposta de consulta de CNPJ"""
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    uf: str
    municipio: str
    logradouro: str
    numero: str
    cep: str
    situacao: str

# Modelos para análise legislativa
class PropostaLegislativa(BaseModel):
    """Modelo para proposta legislativa"""
    objetivo: str = Field(..., description="Objetivo principal do projeto de lei")
    ambito: str = Field(..., description="Âmbito do projeto (Municipal, Estadual, Federal)")
    area_tematica: str = Field(..., description="Área temática (Saúde, Educação, etc.)")
    justificativa: Optional[str] = None
    solucao_proposta: Optional[str] = None
    resultados_esperados: Optional[str] = None

class AnaliseResponse(BaseModel):
    """Resposta da análise legislativa"""
    proposta: PropostaLegislativa
    dados_encontrados: List[Dict[str, Any]]
    fontes_utilizadas: List[str]
    justificativa_gerada: str
    comissoes_relevantes: List[str]
    probabilidade_aprovacao: Optional[float] = None

class SimulacaoTramitacao(BaseModel):
    """Simulação de tramitação legislativa"""
    comissoes: List[Dict[str, Any]]
    tempo_estimado: str
    observacoes: List[str]

# Modelos para relatórios
class RelatorioRequest(BaseModel):
    """Requisição para geração de relatório"""
    tipo: str = Field(..., description="Tipo do relatório (completo, resumido, etc.)")
    dados: Dict[str, Any] = Field(..., description="Dados para o relatório")
    formato: str = Field(default="json", description="Formato de saída (json, pdf, html)")

class RelatorioResponse(BaseModel):
    """Resposta da geração de relatório"""
    id: str
    tipo: str
    formato: str
    url_download: Optional[str] = None
    conteudo: Optional[Dict[str, Any]] = None
    criado_em: datetime = Field(default_factory=datetime.now)

