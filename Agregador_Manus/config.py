from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Aplicação
    app_name: str = "Sistema de Busca - APIs Oficiais BR"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # APIs Governamentais
    portal_transparencia_api_key: Optional[str] = None
    dados_gov_api_token: Optional[str] = None
    
    # Cache Redis
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 100
    
    # CORS
    cors_origins: list = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    # URLs das APIs
    portal_transparencia_base_url: str = "https://api.portaldatransparencia.gov.br/api-de-dados"
    brasil_api_base_url: str = "https://brasilapi.com.br/api"
    camara_deputados_base_url: str = "https://dadosabertos.camara.leg.br/api/v2"
    senado_federal_base_url: str = "https://legis.senado.leg.br/dadosabertos"
    ibge_base_url: str = "https://servicodados.ibge.gov.br/api/v1"
    banco_central_base_url: str = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"
    dados_gov_base_url: str = "https://dados.gov.br/api/3"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()

# Configuração de APIs baseada no YAML
API_CONFIG = {
    "portal_transparencia": {
        "name": "Portal da Transparência",
        "base_url": settings.portal_transparencia_base_url,
        "enabled": True,
        "token_required": True,
        "token_header": "chave-api-dados",
        "rate_limit": {"requests_per_minute": 90, "burst_limit": 100},
        "categories": {
            "despesas": "Despesas e Orçamento",
            "servidores": "Servidores Públicos", 
            "viagens": "Viagens e Deslocamentos",
            "licitacoes": "Licitações",
            "contratos": "Contratos e Convênios",
            "beneficios_sociais": "Benefícios Sociais",
            "sancoes": "Sanções e Impedimentos",
            "cartoes": "Cartões de Pagamento",
            "emendas": "Emendas Parlamentares"
        }
    },
    "brasil_api": {
        "name": "Brasil API",
        "base_url": settings.brasil_api_base_url,
        "enabled": True,
        "token_required": False,
        "rate_limit": {"requests_per_minute": 200, "burst_limit": 50}
    },
    "camara_deputados": {
        "name": "API Câmara dos Deputados",
        "base_url": settings.camara_deputados_base_url,
        "enabled": True,
        "token_required": False,
        "rate_limit": {"requests_per_minute": 120, "burst_limit": 30}
    },
    "senado_federal": {
        "name": "API Senado Federal", 
        "base_url": settings.senado_federal_base_url,
        "enabled": True,
        "token_required": False,
        "rate_limit": {"requests_per_minute": 100, "burst_limit": 25}
    },
    "ibge": {
        "name": "API IBGE",
        "base_url": settings.ibge_base_url,
        "enabled": True,
        "token_required": False,
        "rate_limit": {"requests_per_minute": 200, "burst_limit": 50}
    },
    "banco_central": {
        "name": "APIs Banco Central",
        "base_url": settings.banco_central_base_url,
        "enabled": True,
        "token_required": False,
        "rate_limit": {"requests_per_minute": 60, "burst_limit": 15}
    }
}

# Mapeamento de termos de busca para APIs
SEARCH_MAPPING = {
    "deputado": ["camara_deputados"],
    "senador": ["senado_federal"],
    "congresso": ["camara_deputados", "senado_federal"],
    "lei": ["camara_deputados", "senado_federal"],
    "proposicao": ["camara_deputados", "senado_federal"],
    "votacao": ["camara_deputados", "senado_federal"],
    "orcamento": ["portal_transparencia"],
    "despesa": ["portal_transparencia"],
    "gastos": ["portal_transparencia"],
    "servidor": ["portal_transparencia"],
    "licitacao": ["portal_transparencia"],
    "transparencia": ["portal_transparencia"],
    "cnpj": ["brasil_api"],
    "cep": ["brasil_api"],
    "ddd": ["brasil_api"],
    "municipio": ["ibge", "brasil_api"],
    "estado": ["ibge", "brasil_api"],
    "cidade": ["ibge", "brasil_api"],
    "geografia": ["ibge"],
    "nome": ["ibge"],
    "banco": ["brasil_api"],
    "cotacao": ["banco_central"],
    "dolar": ["banco_central"],
    "cambio": ["banco_central"],
    "bolsa_familia": ["portal_transparencia"],
    "auxilio_emergencial": ["portal_transparencia"],
    "bpc": ["portal_transparencia"],
    "beneficios": ["portal_transparencia"],
    "sancoes": ["portal_transparencia"],
    "contratos": ["portal_transparencia"],
    "convenios": ["portal_transparencia"],
    "cartoes": ["portal_transparencia"],
    "emendas": ["portal_transparencia"]
}

