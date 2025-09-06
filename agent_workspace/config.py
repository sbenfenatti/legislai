"""
Configurações da aplicação
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Auxiliar Legislativo API"
    debug: bool = True

    # Bases de APIs públicas
    ibge_base_url: str = "https://servicodados.ibge.gov.br/api"
    brasil_api_base_url: str = "https://brasilapi.com.br/api"

    # DataSUS (DEMAS - apidadosabertos.saude.gov.br)
    datasus_open_base_url: str = "https://apidadosabertos.saude.gov.br"
    datasus_login: Optional[str] = None
    datasus_password: Optional[str] = None

    # SICONFI (Tesouro Transparente - ORDS)
    siconfi_base_url: str = "http://apidatalake.tesouro.gov.br/ords/siconfi"
    siconfi_schema: str = "tt"

    # Portal da Transparência (chave obrigatória)
    transparencia_base_url: str = "http://api.portaldatransparencia.gov.br/api-de-dados"
    transparencia_api_key: Optional[str] = None

    # Câmara e Senado
    camara_base_url: str = "https://dadosabertos.camara.leg.br/api/v2"
    senado_base_url: str = "https://legis.senado.leg.br/dadosabertos"

    # Cache/tempo de requisição
    redis_url: Optional[str] = None
    cache_ttl: int = 3600
    rate_limit_per_minute: int = 60
    api_timeout: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
