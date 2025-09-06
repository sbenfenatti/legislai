from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services import academic_service
from schemas import AcademicPaper, AcademicSearchRequest

router = APIRouter()

@router.post("/search", response_model=List[AcademicPaper])
async def search_academic_papers(
    request: AcademicSearchRequest
):
    """
    Busca artigos acadêmicos sobre um tema
    - Scielo, PubMed, repositórios brasileiros
    - Filtro Qualis B2+
    - Análise por IA dos artigos relevantes
    """
    try:
        papers = await academic_service.search_papers(
            query=request.query,
            repositories=request.repositories,
            qualis_level=request.min_qualis_level,
            max_results=request.max_results
        )
        return papers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca acadêmica: {str(e)}")

@router.get("/analyze/{paper_id}")
async def analyze_paper(
    paper_id: str,
    focus_keywords: Optional[str] = Query(None, description="Palavras-chave para análise")
):
    """
    Análise detalhada de um artigo por IA
    """
    try:
        analysis = await academic_service.analyze_paper_relevance(paper_id, focus_keywords)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise do artigo: {str(e)}")

@router.get("/repositories")
async def list_repositories():
    """
    Lista repositórios acadêmicos disponíveis
    """
    try:
        repositories = await academic_service.get_available_repositories()
        return repositories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar repositórios: {str(e)}")