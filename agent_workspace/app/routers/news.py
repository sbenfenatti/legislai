from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services import news_service
from schemas import NewsArticle, NewsSearchRequest

router = APIRouter()

@router.post("/search", response_model=List[NewsArticle])
async def search_news(
    request: NewsSearchRequest
):
    """
    Busca notícias sobre um tema
    - Mídia hegemônica (Folha, Globo, Estado)
    - Mídia independente esquerda/direita
    - Fontes internacionais
    """
    try:
        articles = await news_service.search_news(
            query=request.query,
            sources=request.sources,
            political_spectrum=request.political_spectrum,
            timeframe=request.timeframe,
            max_results=request.max_results
        )
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca de notícias: {str(e)}")

@router.get("/sources")
async def list_news_sources(
    spectrum: Optional[str] = Query(None, description="Espectro político: hegemonica, esquerda, direita, internacional")
):
    """
    Lista fontes de notícias disponíveis por espectro político
    """
    try:
        sources = await news_service.get_news_sources(spectrum)
        return sources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar fontes: {str(e)}")

@router.get("/coverage/{query}")
async def analyze_news_coverage(
    query: str,
    days: int = Query(30, description="Período de análise em dias"),
    compare_spectrum: bool = Query(True, description="Comparar cobertura por espectro")
):
    """
    Análise da cobertura midiática de um tema
    """
    try:
        coverage = await news_service.analyze_coverage(
            query=query,
            days=days,
            compare_spectrum=compare_spectrum
        )
        return coverage
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de cobertura: {str(e)}")