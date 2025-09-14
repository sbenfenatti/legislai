from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import structlog
from contextlib import asynccontextmanager

from app.config import settings
from app.core.logger import configure_logging
from app.core.cache import cache_service
from app.api.v1 import search, health
from app.models.search import ErrorResponse

# Configurar logging
configure_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("Starting application", version=settings.app_version)
    
    # Conecta ao Redis
    try:
        await cache_service.connect()
        logger.info("Cache service connected")
    except Exception as e:
        logger.error("Failed to connect cache service", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await cache_service.disconnect()

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para busca unificada em dados oficiais do governo brasileiro",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de hosts confiáveis (apenas em produção)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configurar adequadamente em produção
    )

# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log de todas as requisições HTTP"""
    start_time = time.time()
    
    # Processa a requisição
    response = await call_next(request)
    
    # Calcula tempo de processamento
    process_time = time.time() - start_time
    
    # Log da requisição
    logger.info(
        "HTTP request processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time_ms=round(process_time * 1000, 2),
        user_agent=request.headers.get("user-agent", ""),
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Adiciona header de tempo de resposta
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Handler global de exceções
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(
        "Unhandled exception",
        url=str(request.url),
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    error_response = ErrorResponse(
        error="internal_server_error",
        message="Erro interno do servidor",
        details={"url": str(request.url), "method": request.method}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )

# Incluir routers
app.include_router(
    search.router,
    prefix="/api/v1",
    tags=["search"]
)

app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["health"]
)

# Endpoint raiz
@app.get("/")
async def root():
    """Endpoint raiz com informações básicas da API"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "API para busca unificada em dados oficiais do governo brasileiro",
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "search": "/api/v1/search",
            "suggestions": "/api/v1/search/suggestions",
            "health": "/api/v1/health",
            "apis": "/api/v1/health/apis"
        }
    }

# Endpoint de métricas (placeholder para Prometheus)
@app.get("/metrics")
async def metrics():
    """Endpoint de métricas para monitoramento"""
    # Implementar métricas Prometheus se necessário
    return {"message": "Metrics endpoint - implement Prometheus metrics here"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

