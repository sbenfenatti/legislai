"""
Endpoints para análise legislativa e geração de relatórios
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import uuid
from datetime import datetime
import asyncio

from schemas import (
    APIResponse, PropostaLegislativa, AnaliseResponse, 
    SimulacaoTramitacao, RelatorioRequest, RelatorioResponse
)
from legislative_analyzer import LegislativeAnalyzer
from data_aggregator import DataAggregator

router = APIRouter()
analyzer = LegislativeAnalyzer()
aggregator = DataAggregator()

@router.post("/analyze", response_model=AnaliseResponse)
async def analisar_proposta(proposta: PropostaLegislativa):
    """
    Analisa uma proposta legislativa e busca dados relevantes
    """
    try:
        # Buscar dados relevantes baseados na área temática
        dados_encontrados = await aggregator.buscar_dados_por_area(
            proposta.area_tematica, 
            proposta.ambito
        )
        
        # Gerar justificativa baseada nos dados
        justificativa = analyzer.gerar_justificativa(proposta, dados_encontrados)
        
        # Identificar comissões relevantes
        comissoes = analyzer.identificar_comissoes_relevantes(proposta)
        
        # Calcular probabilidade de aprovação (simulado)
        probabilidade = analyzer.calcular_probabilidade_aprovacao(proposta, dados_encontrados)
        
        return AnaliseResponse(
            proposta=proposta,
            dados_encontrados=dados_encontrados,
            fontes_utilizadas=aggregator.get_fontes_utilizadas(),
            justificativa_gerada=justificativa,
            comissoes_relevantes=comissoes,
            probabilidade_aprovacao=probabilidade
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.post("/simulate/tramitation", response_model=APIResponse)
async def simular_tramitacao(proposta: PropostaLegislativa):
    """
    Simula a tramitação de um projeto de lei nas comissões
    """
    try:
        simulacao = analyzer.simular_tramitacao(proposta)
        
        return APIResponse(
            message="Simulação de tramitação realizada com sucesso",
            data={"simulacao": simulacao}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na simulação: {str(e)}")

@router.get("/similar-laws", response_model=APIResponse)
async def buscar_leis_similares(
    tema: str,
    ambito: str = "Federal",
    limite: int = 10
):
    """
    Busca por leis similares já existentes
    """
    try:
        leis_similares = analyzer.buscar_leis_similares(tema, ambito, limite)
        
        return APIResponse(
            message=f"Encontradas {len(leis_similares)} leis similares",
            data={"leis_similares": leis_similares}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")

@router.post("/generate-report", response_model=RelatorioResponse)
async def gerar_relatorio(
    relatorio_request: RelatorioRequest,
    background_tasks: BackgroundTasks
):
    """
    Gera um relatório baseado nos dados fornecidos
    """
    try:
        relatorio_id = str(uuid.uuid4())
        
        # Se for um relatório simples, gerar imediatamente
        if relatorio_request.tipo == "resumido":
            conteudo = analyzer.gerar_relatorio_resumido(relatorio_request.dados)
            
            return RelatorioResponse(
                id=relatorio_id,
                tipo=relatorio_request.tipo,
                formato=relatorio_request.formato,
                conteudo=conteudo
            )
        
        # Para relatórios complexos, processar em background
        background_tasks.add_task(
            analyzer.gerar_relatorio_completo,
            relatorio_id,
            relatorio_request
        )
        
        return RelatorioResponse(
            id=relatorio_id,
            tipo=relatorio_request.tipo,
            formato=relatorio_request.formato,
            url_download=f"/api/v1/legislative/reports/{relatorio_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração do relatório: {str(e)}")

@router.get("/reports/{relatorio_id}", response_model=APIResponse)
async def obter_relatorio(relatorio_id: str):
    """
    Obtém um relatório gerado anteriormente
    """
    try:
        relatorio = analyzer.obter_relatorio(relatorio_id)
        
        if not relatorio:
            raise HTTPException(status_code=404, detail="Relatório não encontrado")
        
        return APIResponse(
            message="Relatório recuperado com sucesso",
            data={"relatorio": relatorio}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter relatório: {str(e)}")

@router.get("/templates/project", response_model=APIResponse)
async def obter_template_projeto():
    """
    Retorna um template para criação de projeto de lei
    """
    try:
        template = {
            "estrutura": {
                "ementa": "Descrição sucinta do objeto da lei",
                "preambulo": "A Assembleia Legislativa do Estado de [ESTADO] decreta:",
                "artigos": [
                    {
                        "numero": 1,
                        "texto": "Fica instituído...",
                        "paragrafos": [],
                        "incisos": []
                    }
                ],
                "disposicoes_finais": [
                    "As despesas decorrentes da execução desta Lei correrão por conta de dotações orçamentárias próprias.",
                    "Esta Lei entra em vigor na data de sua publicação."
                ]
            },
            "justificativa": {
                "estrutura": [
                    "Contextualização do problema",
                    "Dados e estatísticas relevantes",
                    "Soluções propostas",
                    "Benefícios esperados",
                    "Conclusão"
                ]
            }
        }
        
        return APIResponse(
            message="Template de projeto de lei recuperado com sucesso",
            data={"template": template}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter template: {str(e)}")

@router.get("/commissions", response_model=APIResponse)
async def listar_comissoes():
    """
    Lista todas as comissões legislativas disponíveis
    """
    try:
        comissoes = analyzer.listar_comissoes_disponiveis()
        
        return APIResponse(
            message="Comissões legislativas recuperadas com sucesso",
            data={"comissoes": comissoes}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar comissões: {str(e)}")

@router.get("/health")
async def legislative_health_check():
    """
    Verifica o status dos serviços de análise legislativa
    """
    return {
        "status": "healthy",
        "message": "Serviços de análise legislativa funcionando normalmente",
        "components": {
            "analyzer": "ok",
            "aggregator": "ok",
            "report_generator": "ok"
        }
    }

