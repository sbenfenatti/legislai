"""
Endpoints para integração com APIs do IBGE
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import httpx
from config import settings
from schemas import APIResponse, LocalidadeIBGE, AgregadoIBGE

router = APIRouter()

@router.get("/localidades/estados", response_model=APIResponse)
async def get_estados():
    """Busca todos os estados brasileiros"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.ibge_base_url}/v1/localidades/estados")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message="Estados recuperados com sucesso",
            data={"estados": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar API do IBGE: {str(e)}")

@router.get("/localidades/municipios", response_model=APIResponse)
async def get_municipios(uf: Optional[str] = Query(None, description="Sigla da UF para filtrar municípios")):
    """Busca municípios, opcionalmente filtrados por UF"""
    try:
        url = f"{settings.ibge_base_url}/v1/localidades/municipios"
        if uf:
            # Primeiro busca o ID da UF
            async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
                uf_response = await client.get(f"{settings.ibge_base_url}/v1/localidades/estados/{uf}")
                if uf_response.status_code == 200:
                    uf_data = uf_response.json()
                    uf_id = uf_data.get('id')
                    url = f"{settings.ibge_base_url}/v1/localidades/estados/{uf_id}/municipios"
        
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Municípios recuperados com sucesso{' para ' + uf if uf else ''}",
            data={"municipios": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar API do IBGE: {str(e)}")

@router.get("/agregados/pesquisas", response_model=APIResponse)
async def get_pesquisas():
    """Busca lista de pesquisas disponíveis no IBGE"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.ibge_base_url}/v3/agregados")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message="Pesquisas recuperadas com sucesso",
            data={"pesquisas": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar API do IBGE: {str(e)}")

@router.get("/agregados/{agregado_id}", response_model=APIResponse)
async def get_agregado_dados(
    agregado_id: str,
    localidades: Optional[str] = Query(None, description="IDs das localidades separados por |"),
    variaveis: Optional[str] = Query(None, description="IDs das variáveis separados por |"),
    periodos: Optional[str] = Query(None, description="Períodos separados por |")
):
    """Busca dados de um agregado específico"""
    try:
        params = {}
        if localidades:
            params['localidades'] = localidades
        if variaveis:
            params['variaveis'] = variaveis
        if periodos:
            params['periodos'] = periodos
            
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(
                f"{settings.ibge_base_url}/v3/agregados/{agregado_id}/periodos/-1/variaveis",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Dados do agregado {agregado_id} recuperados com sucesso",
            data={"agregado_dados": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar API do IBGE: {str(e)}")

@router.get("/nomes/{nome}", response_model=APIResponse)
async def get_dados_nome(nome: str):
    """Busca dados sobre a frequência de um nome no Brasil"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.ibge_base_url}/v2/censos/nomes/{nome}")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Dados do nome '{nome}' recuperados com sucesso",
            data={"nome_dados": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar API do IBGE: {str(e)}")

@router.get("/noticias", response_model=APIResponse)
async def get_noticias(
    qtd: int = Query(10, description="Quantidade de notícias", ge=1, le=100)
):
    """Busca notícias recentes do IBGE"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(
                f"{settings.ibge_base_url}/v3/noticias",
                params={"qtd": qtd}
            )
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message="Notícias recuperadas com sucesso",
            data={"noticias": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar API do IBGE: {str(e)}")

@router.get("/health")
async def ibge_health_check():
    """Verifica se a API do IBGE está funcionando"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{settings.ibge_base_url}/v1/localidades/estados")
            response.raise_for_status()
            
        return {"status": "healthy", "message": "API do IBGE está funcionando"}
    except httpx.HTTPError:
        return {"status": "unhealthy", "message": "API do IBGE não está respondendo"}

