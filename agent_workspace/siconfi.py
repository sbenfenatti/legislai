"""
Proxy para SICONFI (Tesouro Transparente - ORDS)
Base pública, sem autenticação.
Documentação: http://apidatalake.tesouro.gov.br/docs/siconfi/
"""

from fastapi import APIRouter, HTTPException, Request, Path
import httpx
from config import settings

router = APIRouter()

VALID_RESOURCES = {
    "entes": "entes",
    "rgf": "rgf",
    "dca": "dca",
    "mscorcamentaria": "mscOrcamentaria",
    "mscpatrimonial": "mscPatrimonial",
    "msccontrole": "mscControle",
    "extratoentregas": "extratoEntregas",
    "anexosrelatorios": "anexosRelatorios",
}

async def _forward(resource: str, query: dict):
    schema = settings.siconfi_schema.strip("/")
    base = settings.siconfi_base_url.rstrip("/")
    url = f"{base}/{schema}/{resource}"
    async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
        resp = await client.get(url, params=query)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Recurso SICONFI não encontrado")
        resp.raise_for_status()
        return resp.json()

@router.get("/health")
async def health():
    try:
        data = await _forward("entes", {"limit": 1})
        return {"status": "healthy", "sample": data}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/{resource}")
async def siconfi_proxy(resource: str = Path(..., description=f"Um de: {', '.join(VALID_RESOURCES.keys())}"), request: Request = None):
    key = resource.lower()
    if key not in VALID_RESOURCES:
        raise HTTPException(status_code=400, detail=f"Recurso inválido. Use: {', '.join(VALID_RESOURCES.keys())}")
    mapped = VALID_RESOURCES[key]
    query = dict(request.query_params) if request else {}
    return await _forward(mapped, query)
