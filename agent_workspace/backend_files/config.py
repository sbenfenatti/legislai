"""
Configurações da aplicação
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações gerais
    app_name: str = "Auxiliar Legislativo API"
    debug: bool = True
    
    # URLs das APIs externas
    ibge_base_url: str = "https://servicodados.ibge.gov.br/api"
    datasus_base_url: str = "https://servicos-datasus.saude.gov.br"
    brasil_api_base_url: str = "https://brasilapi.com.br/api"
    conecta_base_url: str = "https://www.gov.br/conecta/catalogo"
    
    # Configurações de cache
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hora em segundos
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Configurações de timeout para APIs externas
    api_timeout: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()

