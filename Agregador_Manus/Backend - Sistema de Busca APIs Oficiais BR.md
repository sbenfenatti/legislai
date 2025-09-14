# Backend - Sistema de Busca APIs Oficiais BR

Backend desenvolvido em FastAPI para integração com múltiplas APIs governamentais brasileiras.

## Funcionalidades

- ✅ Busca unificada em múltiplas APIs governamentais
- ✅ Cache Redis para otimização de performance
- ✅ Rate limiting para proteção das APIs
- ✅ Documentação automática (Swagger/ReDoc)
- ✅ Logging estruturado
- ✅ Health checks automáticos
- ✅ Suporte a CORS para frontend
- ✅ Validação automática com Pydantic

## APIs Integradas

1. **Portal da Transparência** - Despesas, servidores, licitações, benefícios sociais
2. **Brasil API** - CEP, CNPJ, bancos, municípios
3. **Câmara dos Deputados** - Deputados, proposições, votações
4. **Senado Federal** - Senadores, matérias legislativas
5. **IBGE** - Dados geográficos e demográficos
6. **Banco Central** - Cotações e dados financeiros

## Instalação

### Desenvolvimento Local

1. **Clone o repositório e navegue para o backend:**
```bash
cd sistema-busca-apis/backend
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Inicie o Redis (necessário para cache):**
```bash
# Via Docker
docker run -d -p 6379:6379 redis:7-alpine

# Ou instale localmente
sudo apt-get install redis-server
redis-server
```

5. **Execute a aplicação:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker Compose (Recomendado)

```bash
# Inicia todos os serviços
docker-compose up -d

# Visualiza logs
docker-compose logs -f

# Para os serviços
docker-compose down
```

## Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# APIs Governamentais
PORTAL_TRANSPARENCIA_API_KEY=sua_chave_aqui
DADOS_GOV_API_TOKEN=seu_token_aqui

# Cache Redis
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

### Chaves de API

1. **Portal da Transparência:**
   - Registre-se em: https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
   - Configure `PORTAL_TRANSPARENCIA_API_KEY`

2. **Portal de Dados Abertos:**
   - Registre-se em: https://dados.gov.br
   - Configure `DADOS_GOV_API_TOKEN`

## Uso da API

### Endpoints Principais

- **POST /api/v1/search** - Busca unificada
- **GET /api/v1/search/suggestions** - Sugestões de busca
- **GET /api/v1/health** - Status do sistema
- **GET /api/v1/health/apis** - Status das APIs
- **GET /docs** - Documentação Swagger
- **GET /redoc** - Documentação ReDoc

### Exemplo de Busca

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "despesas educação",
    "page": 1,
    "limit": 20
  }'
```

### Resposta da Busca

```json
{
  "results": [
    {
      "id": "portal_despesas_123",
      "source": "Portal da Transparência",
      "category": "despesas",
      "title": "Ministério da Educação",
      "description": "Valor: R$ 1.000.000 | Data: 01/09/2024",
      "data": {...},
      "relevance": 0.95,
      "timestamp": "2024-09-11T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "has_more": true,
  "query": "despesas educação",
  "apis_searched": ["portal_transparencia"],
  "search_time_ms": 245
}
```

## Arquitetura

```
app/
├── main.py              # Aplicação FastAPI principal
├── config.py            # Configurações e variáveis
├── api/v1/              # Endpoints da API
│   ├── search.py        # Busca unificada
│   └── health.py        # Health checks
├── core/                # Funcionalidades centrais
│   ├── cache.py         # Sistema de cache Redis
│   └── logger.py        # Logging estruturado
├── services/            # Integração com APIs
│   ├── base_service.py  # Classe base
│   └── portal_transparencia.py
├── models/              # Modelos Pydantic
│   └── search.py        # Modelos de busca
└── utils/               # Utilitários
```

## Desenvolvimento

### Adicionando Nova API

1. **Crie um novo serviço:**
```python
# app/services/nova_api.py
from app.services.base_service import BaseAPIService

class NovaAPIService(BaseAPIService):
    def __init__(self):
        super().__init__(
            name="Nova API",
            base_url="https://api.exemplo.gov.br",
            rate_limit_per_minute=100
        )
    
    async def search(self, query, filters=None, page=1, limit=20):
        # Implementar busca específica
        pass
```

2. **Registre no endpoint de busca:**
```python
# app/api/v1/search.py
from app.services.nova_api import NovaAPIService

# Adicione no método unified_search
if api_name == "nova_api":
    service = NovaAPIService()
    # ...
```

3. **Atualize configurações:**
```python
# app/config.py
API_CONFIG["nova_api"] = {
    "name": "Nova API",
    "base_url": "https://api.exemplo.gov.br",
    "enabled": True
}
```

### Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest app/tests/
```

### Logs

Os logs são estruturados e incluem:
- Requisições HTTP
- Erros de API
- Performance de cache
- Métricas de busca

```bash
# Visualizar logs em desenvolvimento
docker-compose logs -f api
```

## Monitoramento

### Health Checks

- **GET /api/v1/health** - Status geral
- **GET /api/v1/health/cache** - Status do Redis
- **GET /api/v1/health/apis** - Status das APIs

### Métricas

- Tempo de resposta das buscas
- Taxa de acerto do cache
- Disponibilidade das APIs
- Rate limiting por IP

## Deploy

### Produção

1. **Configure variáveis de ambiente de produção**
2. **Use Redis externo (não Docker)**
3. **Configure proxy reverso (Nginx)**
4. **Monitore logs e métricas**

```bash
# Build para produção
docker build -t busca-apis-backend .

# Execute com configurações de produção
docker run -d \
  -p 8000:8000 \
  -e DEBUG=false \
  -e REDIS_URL=redis://redis-prod:6379 \
  busca-apis-backend
```

## Troubleshooting

### Problemas Comuns

1. **Redis não conecta:**
   - Verifique se o Redis está rodando
   - Confirme a URL no `.env`

2. **APIs retornam 401:**
   - Verifique as chaves de API
   - Confirme se estão configuradas no `.env`

3. **Rate limit atingido:**
   - Aguarde alguns minutos
   - Verifique configurações de rate limiting

4. **Performance lenta:**
   - Verifique status do cache
   - Monitore logs de performance

### Logs de Debug

```bash
# Ativar logs detalhados
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload
```

