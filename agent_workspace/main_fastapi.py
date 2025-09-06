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
from fastapi.staticfiles import StaticFiles

# Config & Routers v1
from config import settings
from ibge import router as ibge_router
from datasus import router as datasus_router  # simulado
from brasil_api import router as brasil_api_router
from legislative import router as legislative_router

# Novas integrações reais
from datasus_real import router as datasus_real_router
from siconfi import router as siconfi_router
from transparencia import router as transparencia_router
from camara import router as camara_router
from senado import router as senado_router

# Routers v2 (categorias complementares)
try:
    from app.routers import academic as v2_academic
    from app.routers import general as v2_general
    from app.routers import news as v2_news
    from app.routers import social as v2_social
    V2_AVAILABLE = True
except Exception:
    V2_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Iniciando {settings.app_name}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🌐 IBGE API: {settings.ibge_base_url}")
    print(f"🏥 DataSUS (DEMAS): {settings.datasus_open_base_url}")
    print(f"💰 SICONFI: {settings.siconfi_base_url}")
    print(f"💸 Portal da Transparência: {settings.transparencia_base_url}")
    print(f"🏛️ Câmara: {settings.camara_base_url}")
    print(f"🏛️ Senado: {settings.senado_base_url}")
    yield
    print("🛑 Encerrando aplicação")

app = FastAPI(
    title="Assistente Legislativo API",
    description=(
        "Backend para assistente legislativo com integração de APIs governamentais.\n\n"
        "Inclui: IBGE, Brasil API, DataSUS (simulado e real via DEMAS), SICONFI, Portal da Transparência, "
        "Câmara e Senado, além de categorias complementares (acadêmicos, notícias, redes e busca geral)."
    ),
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "message": exc.detail, "error_code": exc.status_code})

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"success": False, "message": "Erro interno do servidor", "error_code": 500})

# v1 Routers (oficiais)
app.include_router(ibge_router, prefix="/api/v1/ibge", tags=["IBGE"])
app.include_router(datasus_router, prefix="/api/v1/datasus-simulado", tags=["DataSUS (simulado)"])
app.include_router(brasil_api_router, prefix="/api/v1/brasil-api", tags=["Brasil API"])
app.include_router(legislative_router, prefix="/api/v1/legislative", tags=["Análise Legislativa"])

# Integrações reais
app.include_router(datasus_real_router, prefix="/api/v1/datasus", tags=["DataSUS (real)"])
app.include_router(siconfi_router, prefix="/api/v1/siconfi", tags=["SICONFI"])
app.include_router(transparencia_router, prefix="/api/v1/transparencia", tags=["Portal da Transparência"])
app.include_router(camara_router, prefix="/api/v1/camara", tags=["Câmara dos Deputados"])
app.include_router(senado_router, prefix="/api/v1/senado", tags=["Senado Federal"])

# v2 Routers (se disponíveis)
if V2_AVAILABLE:
    app.include_router(v2_academic.router, prefix="/api/v2/academic", tags=["Acadêmicos"])
    app.include_router(v2_news.router, prefix="/api/v2/news", tags=["Notícias"])
    app.include_router(v2_social.router, prefix="/api/v2/social", tags=["Redes Digitais"])
    app.include_router(v2_general.router, prefix="/api/v2/general", tags=["Busca Geral"])

# Servir os HTMLs
app.mount("/web", StaticFiles(directory=".", html=True), name="web")

@app.get("/")
async def root():
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": "1.2.0",
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "web": "/web/1.html",
        "apis": {
            "v1": {
                "ibge": "/api/v1/ibge",
                "datasus_real": "/api/v1/datasus",
                "datasus_simulado": "/api/v1/datasus-simulado",
                "brasil_api": "/api/v1/brasil-api",
                "siconfi": "/api/v1/siconfi",
                "transparencia": "/api/v1/transparencia",
                "camara": "/api/v1/camara",
                "senado": "/api/v1/senado",
                "legislative": "/api/v1/legislative",
            },
        },
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": f"{settings.app_name} está funcionando normalmente",
        "version": "1.2.0",
        "environment": "development" if settings.debug else "production",
    }

if __name__ == "__main__":
    uvicorn.run("main_fastapi:app", host="0.0.0.0", port=8000, reload=settings.debug, log_level="debug" if settings.debug else "info")
