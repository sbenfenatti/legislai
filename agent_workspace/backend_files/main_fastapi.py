"""
Aplicação FastAPI principal - Assistente Legislativo
Backend com integração de APIs governamentais
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os

# Importar configurações e routers
from config import settings
from ibge import router as ibge_router
from datasus import router as datasus_router
from brasil_api import router as brasil_api_router
from legislative import router as legislative_router

# Função para inicialização da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    print(f"🚀 Iniciando {settings.app_name}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🌐 IBGE API: {settings.ibge_base_url}")
    print(f"🏥 DataSUS API: {settings.datasus_base_url}")
    print(f"🇧🇷 Brasil API: {settings.brasil_api_base_url}")
    
    yield
    
    # Shutdown
    print("🛑 Encerrando aplicação")

# Criar aplicação FastAPI
app = FastAPI(
    title="Assistente Legislativo API",
    description="""
    Backend para assistente legislativo com integração de APIs governamentais.
    
    ## Funcionalidades
    
    * **IBGE**: Dados demográficos, estatísticos e geográficos
    * **DataSUS**: Informações sobre estabelecimentos de saúde
    * **Brasil API**: CEP, CNPJ, feriados, bancos
    * **Análise Legislativa**: Geração de justificativas e simulação de tramitação
    * **Agregação de Dados**: Busca inteligente por área temática
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configurar middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Manipulador global de erros
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Erro interno do servidor",
            "error_code": 500
        }
    )

# Registrar routers
app.include_router(
    ibge_router,
    prefix="/api/v1/ibge",
    tags=["IBGE"]
)

app.include_router(
    datasus_router,
    prefix="/api/v1/datasus",
    tags=["DataSUS"]
)

app.include_router(
    brasil_api_router,
    prefix="/api/v1/brasil-api",
    tags=["Brasil API"]
)

app.include_router(
    legislative_router,
    prefix="/api/v1/legislative",
    tags=["Análise Legislativa"]
)

# Endpoints raiz
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "apis": {
                "ibge": "/api/v1/ibge",
                "datasus": "/api/v1/datasus", 
                "brasil_api": "/api/v1/brasil-api",
                "legislative": "/api/v1/legislative"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API"""
    return {
        "status": "healthy",
        "message": f"{settings.app_name} está funcionando normalmente",
        "version": "1.0.0",
        "environment": "development" if settings.debug else "production"
    }

@app.get("/api/v1/status")
async def api_status():
    """Status detalhado de todas as APIs integradas"""
    
    # Verificar status das APIs externas (simulado)
    status = {
        "timestamp": "2025-09-06T21:30:00Z",
        "apis": {
            "ibge": {
                "status": "online",
                "base_url": settings.ibge_base_url,
                "endpoints_disponiveis": ["localidades", "agregados", "nomes", "noticias"]
            },
            "datasus": {
                "status": "simulated",
                "base_url": settings.datasus_base_url,
                "endpoints_disponiveis": ["cnes", "cns", "indicadores", "vacinacao"],
                "observacao": "APIs simuladas (reais requerem autenticação específica)"
            },
            "brasil_api": {
                "status": "online",
                "base_url": settings.brasil_api_base_url,
                "endpoints_disponiveis": ["cep", "cnpj", "bancos", "feriados", "ddd", "taxas"]
            },
            "legislative_analyzer": {
                "status": "online",
                "funcionalidades": ["analise", "simulacao", "relatorios", "templates"]
            }
        },
        "cache": {
            "status": "disabled",
            "redis_url": settings.redis_url or "not_configured"
        }
    }
    
    return {
        "success": True,
        "message": "Status das APIs recuperado com sucesso",
        "data": status
    }

# Executar aplicação
if __name__ == "__main__":
    uvicorn.run(
        "main_fastapi:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
