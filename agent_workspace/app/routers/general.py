from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services import general_service
from schemas import GeneralSearchRequest, GeneralSearchResult

router = APIRouter()

@router.post("/search", response_model=List[GeneralSearchResult])
async def general_search(
    request: GeneralSearchRequest
):
    """
    Busca geral complementar (tipo Google)
    - Sites institucionais, ONGs, relatórios
    - Documentos não indexados pelas outras bases
    - Informações complementares
    """
    try:
        results = await general_service.perform_general_search(
            query=request.query,
            site_types=request.site_types,
            file_types=request.file_types,
            max_results=request.max_results
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca geral: {str(e)}")

@router.get("/institutional")
async def search_institutional_sites(
    query: str,
    category: Optional[str] = Query(None, description="Categoria: ong, instituto, fundacao, etc")
):
    """
    Busca específica em sites institucionais
    """
    try:
        results = await general_service.search_institutional_content(query, category)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca institucional: {str(e)}")

@router.get("/reports/{query}")
async def find_reports(
    query: str,
    organization_type: Optional[str] = Query(None, description="Tipo de organização")
):
    """
    Busca relatórios e documentos técnicos
    """
    try:
        reports = await general_service.find_technical_reports(query, organization_type)
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca de relatórios: {str(e)}")