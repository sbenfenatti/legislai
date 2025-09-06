"""
Integração REAL com APIs do DataSUS (DEMAS)
Necessita autenticação: defina DATASUS_LOGIN e DATASUS_PASSWORD no .env
Base: https://apidadosabertos.saude.gov.br
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict
import httpx
from datetime import datetime, timedelta
from config import settings

router = APIRouter()

_token_cache: Dict[str, str] = {"token": None, "exp": None}

async def _get_token(force_refresh: bool = False) -> str:
    if not force_refresh and _token_cache["token"] and _token_cache["exp"] and datetime.utcnow() < _token_cache["exp"]:
        return _token_cache["token"]

    if not settings.datasus_login or not settings.datasus_password:
        raise HTTPException(status_code=400, detail="Credenciais DATASUS não configuradas. Defina DATASUS_LOGIN e DATASUS_PASSWORD no .env")

    payload = {"login": settings.datasus_login, "senha": settings.datasus_password}
    url = f"{settings.datasus_open_base_url}/autenticacao/login"
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            token = data.get("access_token") or data.get("token") or data.get("accessToken")
            if not token:
                raise HTTPException(status_code=502, detail="Resposta inesperada do login do DataSUS")
            # tokens tipicamente expiram ~1h; usa margem de 50min
            _token_cache["token"] = token
            _token_cache["exp"] = datetime.utcnow() + timedelta(minutes=50)
            return token
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Falha ao autenticar no DataSUS: {str(e)}")

@router.post("/auth/token")
async def obter_token_datasus(force_refresh: bool = Query(False)):
    token = await _get_token(force_refresh)
    return {"access_token": token, "expires_at": _token_cache["exp"].isoformat() if _token_cache["exp"] else None}


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

@router.get("/cnes/tipounidades")
async def listar_tipos_unidade(limit: int = Query(20, le=20), offset: int = 0):
    token = await _get_token()
    url = f"{settings.datasus_open_base_url}/cnes/tipounidades"
    async with httpx.AsyncClient(timeout=settings.api_timeout, headers=_auth_headers(token)) as client:
        resp = await client.get(url, params={"limit": limit, "offset": offset})
        resp.raise_for_status()
        return resp.json()

@router.get("/cnes/estabelecimentos")
async def listar_estabelecimentos(
    codigo_tipo_unidade: Optional[int] = None,
    codigo_uf: Optional[int] = None,
    codigo_municipio: Optional[int] = None,
    status: Optional[int] = Query(None, description="1=ativo,0=inativo"),
    estabelecimento_possui_centro_cirurgico: Optional[int] = None,
    estabelecimento_possui_centro_obstetrico: Optional[int] = None,
    limit: int = Query(20, le=20),
    offset: int = 0,
):
    token = await _get_token()
    params = {
        "limit": limit,
        "offset": offset,
    }
    if codigo_tipo_unidade is not None:
        params["codigo_tipo_unidade"] = codigo_tipo_unidade
    if codigo_uf is not None:
        params["codigo_uf"] = codigo_uf
    if codigo_municipio is not None:
        params["codigo_municipio"] = codigo_municipio
    if status is not None:
        params["status"] = status
    if estabelecimento_possui_centro_cirurgico is not None:
        params["estabelecimento_possui_centro_cirurgico"] = estabelecimento_possui_centro_cirurgico
    if estabelecimento_possui_centro_obstetrico is not None:
        params["estabelecimento_possui_centro_obstetrico"] = estabelecimento_possui_centro_obstetrico

    url = f"{settings.datasus_open_base_url}/cnes/estabelecimentos"
    async with httpx.AsyncClient(timeout=settings.api_timeout, headers=_auth_headers(token)) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

@router.get("/cnes/estabelecimentos/{codigo_cnes}")
async def obter_estabelecimento(codigo_cnes: int):
    token = await _get_token()
    url = f"{settings.datasus_open_base_url}/cnes/estabelecimentos/{codigo_cnes}"
    async with httpx.AsyncClient(timeout=settings.api_timeout, headers=_auth_headers(token)) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
