# Estrutura do Backend - FastAPI

## Visão Geral
Backend desenvolvido em FastAPI para integração com múltiplas APIs governamentais brasileiras, oferecendo busca unificada, cache inteligente e documentação automática.

## Estrutura de Diretórios
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal FastAPI
│   ├── config.py              # Configurações e variáveis de ambiente
│   ├── dependencies.py        # Dependências injetáveis
│   │
│   ├── api/                   # Endpoints da API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── search.py      # Endpoints de busca
│   │   │   ├── apis.py        # Endpoints para listar APIs
│   │   │   └── health.py      # Health checks
│   │   └── deps.py            # Dependências específicas da API
│   │
│   ├── core/                  # Lógica central
│   │   ├── __init__.py
│   │   ├── cache.py           # Sistema de cache Redis
│   │   ├── rate_limiter.py    # Rate limiting
│   │   ├── logger.py          # Sistema de logging
│   │   └── security.py       # Autenticação e segurança
│   │
│   ├── services/              # Serviços de integração
│   │   ├── __init__.py
│   │   ├── base_service.py    # Classe base para serviços
│   │   ├── portal_transparencia.py
│   │   ├── brasil_api.py
│   │   ├── camara_deputados.py
│   │   ├── senado_federal.py
│   │   ├── ibge.py
│   │   └── banco_central.py
│   │
│   ├── models/                # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── search.py          # Modelos de busca
│   │   ├── responses.py       # Modelos de resposta
│   │   └── api_models.py      # Modelos específicos das APIs
│   │
│   ├── utils/                 # Utilitários
│   │   ├── __init__.py
│   │   ├── formatters.py      # Formatação de dados
│   │   ├── validators.py      # Validadores customizados
│   │   └── helpers.py         # Funções auxiliares
│   │
│   └── tests/                 # Testes
│       ├── __init__.py
│       ├── test_search.py
│       ├── test_services.py
│       └── conftest.py
│
├── requirements.txt           # Dependências Python
├── Dockerfile                # Container Docker
├── docker-compose.yml        # Orquestração local
└── README.md                 # Documentação
```

## Modelos Pydantic

### Modelo de Busca
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    apis: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

class SearchResult(BaseModel):
    id: str
    source: str
    category: str
    title: str
    description: str
    data: dict
    relevance: float
    timestamp: datetime
```

## Endpoints Principais

### 1. Busca Unificada
```python
@router.post("/search", response_model=SearchResponse)
async def unified_search(
    request: SearchRequest,
    cache: Redis = Depends(get_cache),
    rate_limiter = Depends(RateLimiter(times=100, seconds=60))
):
    """
    Busca unificada em todas as APIs governamentais
    """
```

### 2. APIs Disponíveis
```python
@router.get("/apis", response_model=List[APIInfo])
async def list_apis():
    """
    Lista todas as APIs disponíveis e seus status
    """
```

### 3. Categorias
```python
@router.get("/categories", response_model=List[CategoryInfo])
async def list_categories():
    """
    Lista todas as categorias de dados disponíveis
    """
```

## Serviços de Integração

### Classe Base
```python
class BaseAPIService:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = httpx.AsyncClient()
    
    async def make_request(self, endpoint: str, params: dict = None):
        # Implementação base para requisições
        pass
    
    async def search(self, query: str, filters: dict = None):
        # Método abstrato para busca
        raise NotImplementedError
```

### Portal da Transparência
```python
class PortalTransparenciaService(BaseAPIService):
    def __init__(self):
        super().__init__(
            base_url="https://api.portaldatransparencia.gov.br/api-de-dados",
            api_key=settings.PORTAL_TRANSPARENCIA_API_KEY
        )
    
    async def search_despesas(self, query: str, filters: dict):
        # Busca em despesas
        pass
    
    async def search_servidores(self, query: str, filters: dict):
        # Busca em servidores
        pass
```

## Sistema de Cache

### Configuração Redis
```python
class CacheService:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str):
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(value, default=str)
        )
    
    def generate_cache_key(self, endpoint: str, params: dict):
        # Gera chave única para cache
        pass
```

## Rate Limiting

### Implementação com slowapi
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/minute")
async def search_endpoint(request: Request):
    # Endpoint com rate limiting
    pass
```

## Configurações

### Variáveis de Ambiente
```python
class Settings(BaseSettings):
    # APIs
    PORTAL_TRANSPARENCIA_API_KEY: Optional[str] = None
    DADOS_GOV_API_TOKEN: Optional[str] = None
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
```

## Logging e Monitoramento

### Configuração de Logs
```python
import structlog

logger = structlog.get_logger()

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "request_processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response
```

## Testes

### Configuração de Testes
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    # Mock do Redis para testes
    pass

def test_search_endpoint(client, mock_redis):
    response = client.post("/api/v1/search", json={
        "query": "despesas",
        "limit": 10
    })
    assert response.status_code == 200
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Vantagens do FastAPI

1. **Performance**: Baseado em Starlette e Pydantic, muito rápido
2. **Tipagem**: Type hints nativos com validação automática
3. **Documentação**: Swagger UI e ReDoc automáticos
4. **Async**: Suporte nativo a programação assíncrona
5. **Validação**: Validação automática de entrada e saída
6. **IDE Support**: Excelente suporte em IDEs modernas
7. **Standards**: Baseado em padrões OpenAPI e JSON Schema

