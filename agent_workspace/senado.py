"""
Dados Abertos do Senado Federal
Docs: https://legis.senado.leg.br/dadosabertos
As respostas são XML; este proxy converte para JSON.
"""

from fastapi import APIRouter, HTTPException, Query
import httpx
import xmltodict
from typing import Optional
from config import settings

router = APIRouter()
BASE = settings.senado_base_url.rstrip("/")

async def _xml_get(path: str, params: dict = None):
    url = f"{BASE}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        try:
            data = xmltodict.parse(resp.text)
            return data
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Falha ao converter XML do Senado: {str(e)}")

@router.get("/materias")
async def listar_materias(
    sigla: Optional[str] = Query(None, description="Sigla (PL, PEC, etc.)"),
    numero: Optional[int] = None,
    ano: Optional[int] = None,
):
    """Lista matérias legislativas (proxy simplificado)."""
    params = {}
    if sigla: params["sigla"] = sigla
    if numero: params["numero"] = numero
    if ano: params["ano"] = ano
    # endpoint comum
    return await _xml_get("materia/pesquisa/lista", params)

@router.get("/senadores")
async def listar_senadores(mandato: Optional[str] = None):
    params = {"mandato": mandato} if mandato else None
    return await _xml_get("senador/lista", params)
