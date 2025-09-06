"""
Dados Abertos Câmara dos Deputados
Docs: https://dadosabertos.camara.leg.br/api
"""

from fastapi import APIRouter, HTTPException, Path, Query
import httpx
from typing import Optional
from config import settings

router = APIRouter()

BASE = settings.camara_base_url.rstrip("/")

async def _get(path: str, params: dict = None):
    url = f"{BASE}/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

@router.get("/proposicoes")
async def listar_proposicoes(
    siglaTipo: Optional[str] = None,
    ano: Optional[int] = None,
    pagina: int = 1,
    itens: int = 100,
    ordenarPor: Optional[str] = None,
    ordem: Optional[str] = None,
    keywords: Optional[str] = Query(None, description="Busca no campo ementa")
):
    params = {"pagina": pagina, "itens": itens}
    if siglaTipo: params["siglaTipo"] = siglaTipo
    if ano: params["ano"] = ano
    if ordenarPor: params["ordenarPor"] = ordenarPor
    if ordem: params["ordem"] = ordem
    if keywords: params["keywords"] = keywords
    return await _get("proposicoes", params)

@router.get("/proposicoes/{id}")
async def obter_proposicao(id: int = Path(...)):
    return await _get(f"proposicoes/{id}")

@router.get("/proposicoes/{id}/autores")
async def autores_proposicao(id: int):
    return await _get(f"proposicoes/{id}/autores")

@router.get("/proposicoes/{id}/tramitacoes")
async def tramitacoes_proposicao(id: int, pagina: int = 1, itens: int = 100):
    return await _get(f"proposicoes/{id}/tramitacoes", {"pagina": pagina, "itens": itens})

@router.get("/deputados")
async def listar_deputados(nome: Optional[str] = None, pagina: int = 1, itens: int = 100):
    params = {"pagina": pagina, "itens": itens}
    if nome: params["nome"] = nome
    return await _get("deputados", params)
