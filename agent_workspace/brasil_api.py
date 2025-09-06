"""
Endpoints para integração com Brasil API
"""

from fastapi import APIRouter, HTTPException, Path
from typing import List, Optional
import httpx
from config import settings
from schemas import APIResponse, EnderecoResponse, EmpresaResponse

router = APIRouter()

@router.get("/cep/{cep}", response_model=APIResponse)
async def get_endereco_por_cep(
    cep: str = Path(..., description="CEP para consulta (8 dígitos)", regex=r"^\d{8}$")
):
    """Busca endereço por CEP"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v2/cep/{cep}")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Endereço para CEP {cep} encontrado",
            data={"endereco": data}
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="CEP não encontrado")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")

@router.get("/cnpj/{cnpj}", response_model=APIResponse)
async def get_empresa_por_cnpj(
    cnpj: str = Path(..., description="CNPJ para consulta (14 dígitos)", regex=r"^\d{14}$")
):
    """Busca dados de empresa por CNPJ"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v1/cnpj/{cnpj}")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Dados da empresa com CNPJ {cnpj} encontrados",
            data={"empresa": data}
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="CNPJ não encontrado")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")

@router.get("/bancos", response_model=APIResponse)
async def get_bancos():
    """Lista todos os bancos do Brasil"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v1/banks")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message="Lista de bancos recuperada com sucesso",
            data={"bancos": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")

@router.get("/bancos/{codigo}", response_model=APIResponse)
async def get_banco_por_codigo(
    codigo: int = Path(..., description="Código do banco")
):
    """Busca dados de um banco específico por código"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v1/banks/{codigo}")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Dados do banco {codigo} encontrados",
            data={"banco": data}
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Banco não encontrado")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")

@router.get("/feriados/{ano}", response_model=APIResponse)
async def get_feriados_nacionais(
    ano: int = Path(..., description="Ano para consulta de feriados", ge=1900, le=2100)
):
    """Busca feriados nacionais de um ano específico"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v1/holidays/{ano}")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Feriados nacionais de {ano} recuperados com sucesso",
            data={"feriados": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")

@router.get("/ddd/{ddd}", response_model=APIResponse)
async def get_cidades_por_ddd(
    ddd: int = Path(..., description="Código DDD", ge=11, le=99)
):
    """Busca cidades por código DDD"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v1/ddd/{ddd}")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message=f"Cidades do DDD {ddd} encontradas",
            data={"cidades": data}
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="DDD não encontrado")
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")

@router.get("/taxas", response_model=APIResponse)
async def get_taxas():
    """Busca taxas de juros atuais"""
    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v1/taxas")
            response.raise_for_status()
            data = response.json()
            
        return APIResponse(
            message="Taxas de juros recuperadas com sucesso",
            data={"taxas": data}
        )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar Brasil API: {str(e)}")

@router.get("/health")
async def brasil_api_health_check():
    """Verifica se a Brasil API está funcionando"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{settings.brasil_api_base_url}/v1/banks")
            response.raise_for_status()
            
        return {"status": "healthy", "message": "Brasil API está funcionando"}
    except httpx.HTTPError:
        return {"status": "unhealthy", "message": "Brasil API não está respondendo"}

