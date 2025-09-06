from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Importações dos routers existentes
from app.routers import academic, institutional, media, official, social

# Importações dos novos routers
from app.routers import news, general

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Plataforma de Pesquisa Governamental",
    description="Centraliza informações governamentais e sociais para cidadãos e legisladores",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers existentes (mantidos para compatibilidade)
app.include_router(academic.router, prefix="/academic", tags=["academic"])
app.include_router(institutional.router, prefix="/institutional", tags=["institutional"])
app.include_router(media.router, prefix="/media", tags=["media"])
app.include_router(official.router, prefix="/official", tags=["official"])
app.include_router(social.router, prefix="/social", tags=["social"])

# Novos routers das 5 categorias principais
app.include_router(official.router, prefix="/api/v2/official", tags=["Fontes Oficiais v2"])
app.include_router(social.router, prefix="/api/v2/social", tags=["Redes Digitais"])
app.include_router(academic.router, prefix="/api/v2/academic", tags=["Acadêmicos"])  # Reutiliza o existente
app.include_router(news.router, prefix="/api/v2/news", tags=["Notícias"])
app.include_router(general.router, prefix="/api/v2/general", tags=["Busca Geral"])

@app.get("/")
async def root():
    return {
        "message": "Plataforma de Pesquisa Governamental - API v2.0",
        "description": "Centraliza informações de 5 categorias: Oficiais, Redes Digitais, Acadêmicos, Notícias e Busca Geral",
        "categories": {
            "official": "/api/v2/official - APIs governamentais brasileiras",
            "social": "/api/v2/social - Análise de redes sociais e tendências",
            "academic": "/api/v2/academic - Artigos científicos Qualis B2+",
            "news": "/api/v2/news - Notícias por espectro político",
            "general": "/api/v2/general - Busca complementar tipo Google"
        },
        "docs": "/docs",
        "version": "2.0.0"
    }

@app.get("/api/v2/search")
async def unified_search(
    query: str,
    categories: str = "official,social,academic,news,general",
    max_results_per_category: int = 10
):
    """
    Busca unificada em todas as 5 categorias
    """
    from app.services import official_service, social_service, academic_service, news_service, general_service
    from schemas import (
        SocialMediaSearchRequest, AcademicSearchRequest, 
        NewsSearchRequest, GeneralSearchRequest
    )
    
    results = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "categories": {}
    }
    
    selected_categories = categories.split(",")
    
    # Busca em cada categoria selecionada
    if "official" in selected_categories:
        try:
            # Reutiliza serviço existente do official
            official_results = await official_service.search_propositions(keywords=query)
            results["categories"]["official"] = official_results[:max_results_per_category]
        except:
            results["categories"]["official"] = []
    
    if "social" in selected_categories:
        try:
            social_request = SocialMediaSearchRequest(query=query)
            social_results = await social_service.search_social_trends(
                query=query, 
                platforms=["twitter", "youtube", "reddit"],
                timeframe="7d"
            )
            results["categories"]["social"] = social_results[:max_results_per_category]
        except:
            results["categories"]["social"] = []
    
    if "academic" in selected_categories:
        try:
            academic_request = AcademicSearchRequest(
                query=query,
                repositories=["scielo", "pubmed"],
                min_qualis_level="B2",
                max_results=max_results_per_category
            )
            academic_results = await academic_service.search_papers(
                query=query,
                repositories=["scielo", "pubmed"],
                qualis_level="B2",
                max_results=max_results_per_category
            )
            results["categories"]["academic"] = academic_results
        except:
            results["categories"]["academic"] = []
    
    if "news" in selected_categories:
        try:
            news_request = NewsSearchRequest(
                query=query,
                sources=[],
                political_spectrum=None,
                timeframe="30d",
                max_results=max_results_per_category
            )
            news_results = await news_service.search_news(
                query=query,
                sources=[],
                political_spectrum=None,
                timeframe="30d",
                max_results=max_results_per_category
            )
            results["categories"]["news"] = news_results
        except:
            results["categories"]["news"] = []
    
    if "general" in selected_categories:
        try:
            general_request = GeneralSearchRequest(
                query=query,
                site_types=["ong", "instituto", "fundacao"],
                file_types=["pdf"],
                max_results=max_results_per_category
            )
            general_results = await general_service.perform_general_search(
                query=query,
                site_types=["ong", "instituto", "fundacao"],
                file_types=["pdf"],
                max_results=max_results_per_category
            )
            results["categories"]["general"] = general_results
        except:
            results["categories"]["general"] = []
    
    return results

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)