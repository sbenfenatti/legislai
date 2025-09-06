"""
Portal da Transparência - API
Docs: https://www.portaltransparencia.gov.br/api-de-dados
Requer cabeçalho 'chave-api-dados' (defina TRANSPARENCIA_API_KEY no .env)
"""

from fastapi import APIRouter, HTTPException, Request, Path
import httpx
from config import settings

router = APIRouter()

COMMON_RESOURCES = {
    # lista parcial dos recursos mais usados
    "orgaos": "orgaos",
    "despesas": "despesas",
    "emendas": "emendas",
    "licitacoes": "licitacoes",
    "contratos": "contratos",
    "convenios": "convenios",
    "obras": "obras",
}

async def _call(resource: str, query: dict):
    api_key = settings.transparencia_api_key
    if not api_key:
        raise HTTPException(status_code=400, detail="Defina TRANSPARENCIA_API_KEY no .env para usar a API do Portal da Transparência")
    base = settings.transparencia_base_url.rstrip("/")
    url = f"{base}/{resource}"
    headers = {"chave-api-dados": api_key, "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=settings.api_timeout, headers=headers) as client:
        resp = await client.get(url, params=query)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Recurso não encontrado no Portal da Transparência")
        resp.raise_for_status()
        return resp.json()

@router.get("/health")
async def health():
    try:
        data = await _call("orgaos", {"pagina": 1})
        return {"status": "healthy", "sample_len": len(data) if isinstance(data, list) else None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/{resource}")
async def transparencia_proxy(resource: str = Path(..., description=f"Alguns: {', '.join(COMMON_RESOURCES.keys())}"), request: Request = None):
    query = dict(request.query_params) if request else {}
    return await _call(resource, query)
