from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services import social_service
from schemas import SocialMediaResult, SocialMediaSearchRequest

router = APIRouter()

@router.post("/search", response_model=List[SocialMediaResult])
async def search_social_media(
    request: SocialMediaSearchRequest
):
    """
    Busca análise de redes sociais sobre um tema
    - Twitter, Instagram, TikTok, Reddit, YouTube
    - Google Trends, hashtags, sentiment analysis
    """
    try:
        results = await social_service.search_social_trends(
            query=request.query,
            platforms=request.platforms,
            timeframe=request.timeframe
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca social: {str(e)}")

@router.get("/trending")
async def get_trending_topics(
    platform: Optional[str] = Query(None, description="Plataforma específica"),
    limit: int = Query(10, description="Número máximo de resultados")
):
    """
    Retorna tópicos em trending
    """
    try:
        trending = await social_service.get_trending_topics(platform, limit)
        return trending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar trending: {str(e)}")

@router.get("/sentiment/{query}")
async def analyze_sentiment(
    query: str,
    platform: Optional[str] = Query(None),
    days: int = Query(7, description="Dias para análise")
):
    """
    Análise de sentimento sobre um tema
    """
    try:
        sentiment = await social_service.analyze_sentiment(query, platform, days)
        return sentiment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise de sentimento: {str(e)}")