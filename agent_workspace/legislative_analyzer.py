"""
Serviço de análise legislativa
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import uuid

from schemas import PropostaLegislativa, RelatorioRequest

class LegislativeAnalyzer:
    """Classe responsável pela análise legislativa e geração de relatórios"""
    
    def __init__(self):
        self.relatorios_cache = {}
        self.comissoes_almg = self._carregar_comissoes_almg()
    
    def _carregar_comissoes_almg(self) -> Dict[str, Dict[str, Any]]:
        """Carrega informações das comissões da ALMG"""
        return {
            "ccj": {
                "nome": "Constituição e Justiça",
                "descricao": "Análise de legalidade e constitucionalidade",
                "areas": ["constitucional", "juridico", "legalidade"],
                "obrigatoria": True
            },
            "saude": {
                "nome": "Saúde",
                "descricao": "Análise de mérito em questões de saúde",
                "areas": ["saude", "medicina", "sus", "hospitais", "ubs"],
                "obrigatoria": False
            },
            "ffo": {
                "nome": "Fiscalização Financeira e Orçamentária",
                "descricao": "Análise orçamentária e financeira",
                "areas": ["orcamento", "financeiro", "despesas", "receitas"],
                "obrigatoria": False
            },
            "ciencia_tecnologia": {
                "nome": "Ciência e Tecnologia",
                "descricao": "Análise de inovação e tecnologia",
                "areas": ["tecnologia", "inovacao", "ciencia", "inteligencia_artificial", "digital"],
                "obrigatoria": False
            },
            "educacao": {
                "nome": "Educação",
                "descricao": "Análise de políticas educacionais",
                "areas": ["educacao", "ensino", "escola", "universidade"],
                "obrigatoria": False
            },
            "meio_ambiente": {
                "nome": "Meio Ambiente",
                "descricao": "Análise de questões ambientais",
                "areas": ["ambiente", "sustentabilidade", "poluicao", "recursos_naturais"],
                "obrigatoria": False
            },
            "seguranca": {
                "nome": "Segurança Pública",
                "descricao": "Análise de segurança pública",
                "areas": ["seguranca", "policia", "criminalidade", "violencia"],
                "obrigatoria": False
            },
            "transporte": {
                "nome": "Transporte e Obras Públicas",
                "descricao": "Análise de transporte e infraestrutura",
                "areas": ["transporte", "obras", "infraestrutura", "mobilidade"],
                "obrigatoria": False
            }
        }
    
    def gerar_justificativa(self, proposta: PropostaLegislativa, dados: List[Dict[str, Any]]) -> str:
        """
        Gera justificativa baseada na proposta e dados coletados
        """
        # Extrair informações relevantes dos dados
        estatisticas = self._extrair_estatisticas_relevantes(dados, proposta.area_tematica)
        
        # Construir justificativa estruturada
        justificativa_parts = []
        
        # Contextualização
        justificativa_parts.append(
            f"O presente projeto de lei tem como objetivo {proposta.objetivo.lower()}, "
            f"no âmbito {proposta.ambito.lower()}, na área de {proposta.area_tematica.lower()}."
        )
        
        # Dados e estatísticas
        if estatisticas:
            justificativa_parts.append(
                "Com base nos dados oficiais coletados, observa-se que:"
            )
            
            for stat in estatisticas[:3]:  # Limitar a 3 estatísticas principais
                fonte = stat.get("fonte", "Fonte oficial")
                descricao = stat.get("descricao", "Dados relevantes")
                justificativa_parts.append(f"- {fonte}: {descricao}")
        
        # Solução proposta
        if proposta.solucao_proposta:
            justificativa_parts.append(
                f"Diante deste cenário, a solução proposta consiste em {proposta.solucao_proposta.lower()}"
            )
        
        # Resultados esperados
        if proposta.resultados_esperados:
            justificativa_parts.append(
                f"Os resultados esperados incluem {proposta.resultados_esperados.lower()}"
            )
        
        # Conclusão
        justificativa_parts.append(
            f"Portanto, este projeto de lei representa uma importante iniciativa para o "
            f"desenvolvimento da área de {proposta.area_tematica.lower()} no âmbito "
            f"{proposta.ambito.lower()}, contribuindo para o bem-estar da população e o "
            f"aprimoramento das políticas públicas."
        )
        
        return " ".join(justificativa_parts)
    
    def _extrair_estatisticas_relevantes(self, dados: List[Dict[str, Any]], area: str) -> List[Dict[str, str]]:
        """Extrai estatísticas relevantes dos dados coletados"""
        estatisticas = []
        
        for item in dados:
            fonte = item.get("fonte", "")
            descricao = item.get("descricao", "")
            tipo = item.get("tipo", "")
            
            # Filtrar por relevância à área temática
            area_lower = area.lower()
            if (area_lower in fonte.lower() or 
                area_lower in descricao.lower() or 
                area_lower in tipo.lower()):
                
                estatisticas.append({
                    "fonte": fonte,
                    "descricao": descricao,
                    "tipo": tipo
                })
        
        return estatisticas
    
    def identificar_comissoes_relevantes(self, proposta: PropostaLegislativa) -> List[str]:
        """
        Identifica comissões relevantes para a proposta
        """
        comissoes_relevantes = []
        
        # CCJ é sempre obrigatória
        comissoes_relevantes.append("Constituição e Justiça")
        
        # Identificar outras comissões baseadas na área temática e conteúdo
        texto_analise = f"{proposta.objetivo} {proposta.area_tematica} {proposta.solucao_proposta or ''}"
        texto_lower = texto_analise.lower()
        
        for comissao_id, comissao_info in self.comissoes_almg.items():
            if comissao_id == "ccj":  # Já adicionada
                continue
            
            # Verificar se alguma área da comissão está presente no texto
            for area in comissao_info["areas"]:
                if area in texto_lower:
                    comissoes_relevantes.append(comissao_info["nome"])
                    break
        
        # Se envolve gastos públicos, adicionar FFO
        if any(palavra in texto_lower for palavra in ["gasto", "despesa", "orçamento", "recurso", "verba"]):
            if "Fiscalização Financeira e Orçamentária" not in comissoes_relevantes:
                comissoes_relevantes.append("Fiscalização Financeira e Orçamentária")
        
        return comissoes_relevantes
    
    def simular_tramitacao(self, proposta: PropostaLegislativa) -> Dict[str, Any]:
        """
        Simula a tramitação do projeto nas comissões
        """
        comissoes_relevantes = self.identificar_comissoes_relevantes(proposta)
        
        simulacao = {
            "comissoes": [],
            "tempo_estimado": "4 a 8 meses",
            "observacoes": []
        }
        
        for comissao in comissoes_relevantes:
            parecer = self._simular_parecer_comissao(comissao, proposta)
            simulacao["comissoes"].append({
                "nome": comissao,
                "parecer": parecer["status"],
                "observacoes": parecer["observacoes"],
                "tempo_estimado": parecer["tempo"]
            })
        
        # Calcular tempo total estimado
        tempo_total = len(comissoes_relevantes) * 30  # 30 dias por comissão em média
        if tempo_total > 180:
            simulacao["tempo_estimado"] = "6 meses ou mais"
        elif tempo_total > 120:
            simulacao["tempo_estimado"] = "4 a 6 meses"
        else:
            simulacao["tempo_estimado"] = "2 a 4 meses"
        
        return simulacao
    
    def _simular_parecer_comissao(self, comissao: str, proposta: PropostaLegislativa) -> Dict[str, Any]:
        """Simula o parecer de uma comissão específica"""
        
        pareceres_base = {
            "Constituição e Justiça": {
                "status": "Aprovado com Ressalvas",
                "observacoes": "Projeto constitucional, mas requer adequação na redação dos artigos sobre despesas públicas.",
                "tempo": "45 dias"
            },
            "Saúde": {
                "status": "Aprovado",
                "observacoes": "Projeto atende necessidade real do sistema de saúde e está alinhado com diretrizes do SUS.",
                "tempo": "30 dias"
            },
            "Fiscalização Financeira e Orçamentária": {
                "status": "Aprovado com Ressalvas",
                "observacoes": "Necessário apresentar estudo de impacto orçamentário detalhado e fonte de recursos específica.",
                "tempo": "60 dias"
            },
            "Ciência e Tecnologia": {
                "status": "Aprovado",
                "observacoes": "Projeto incentiva inovação tecnológica e modernização do Estado.",
                "tempo": "30 dias"
            }
        }
        
        return pareceres_base.get(comissao, {
            "status": "Aprovado",
            "observacoes": "Projeto aprovado sem ressalvas.",
            "tempo": "30 dias"
        })
    
    def calcular_probabilidade_aprovacao(self, proposta: PropostaLegislativa, dados: List[Dict[str, Any]]) -> float:
        """
        Calcula probabilidade estimada de aprovação (simulado)
        """
        probabilidade_base = 0.6  # 60% base
        
        # Fatores que aumentam a probabilidade
        if dados:  # Tem dados para justificar
            probabilidade_base += 0.15
        
        if proposta.justificativa:  # Tem justificativa elaborada
            probabilidade_base += 0.1
        
        if proposta.solucao_proposta:  # Tem solução clara
            probabilidade_base += 0.1
        
        # Fatores por área temática (algumas áreas têm mais apoio)
        areas_prioritarias = ["saude", "educacao", "seguranca"]
        if proposta.area_tematica.lower() in areas_prioritarias:
            probabilidade_base += 0.05
        
        # Limitar entre 0 e 1
        return min(1.0, max(0.0, probabilidade_base))
    
    def buscar_leis_similares(self, tema: str, ambito: str, limite: int) -> List[Dict[str, Any]]:
        """
        Busca leis similares (simulado com dados de exemplo)
        """
        leis_exemplo = [
            {
                "numero": "Lei nº 23.792/2021",
                "ementa": "Institui o Programa Estadual de Telemedicina no âmbito do SUS-MG",
                "ano": 2021,
                "ambito": "Estadual",
                "area": "Saúde",
                "similaridade": 0.85
            },
            {
                "numero": "Lei nº 23.632/2020",
                "ementa": "Dispõe sobre a informatização dos serviços de saúde pública",
                "ano": 2020,
                "ambito": "Estadual", 
                "area": "Saúde",
                "similaridade": 0.72
            },
            {
                "numero": "Lei Federal nº 13.989/2020",
                "ementa": "Dispõe sobre o uso da telemedicina durante a crise do coronavírus",
                "ano": 2020,
                "ambito": "Federal",
                "area": "Saúde",
                "similaridade": 0.68
            }
        ]
        
        # Filtrar por âmbito se especificado
        if ambito != "Todos":
            leis_exemplo = [lei for lei in leis_exemplo if lei["ambito"] == ambito]
        
        # Ordenar por similaridade e limitar
        leis_exemplo.sort(key=lambda x: x["similaridade"], reverse=True)
        return leis_exemplo[:limite]
    
    def gerar_relatorio_resumido(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório resumido imediatamente"""
        return {
            "tipo": "resumido",
            "timestamp": datetime.now().isoformat(),
            "resumo": {
                "total_dados": len(dados.get("dados_encontrados", [])),
                "fontes": dados.get("fontes_utilizadas", []),
                "comissoes_relevantes": dados.get("comissoes_relevantes", []),
                "probabilidade_aprovacao": dados.get("probabilidade_aprovacao", 0.0)
            },
            "recomendacoes": [
                "Revisar a redação dos artigos sobre despesas públicas",
                "Incluir estudo de impacto orçamentário detalhado",
                "Consultar especialistas da área temática"
            ]
        }
    
    async def gerar_relatorio_completo(self, relatorio_id: str, request: RelatorioRequest):
        """Gera relatório completo em background"""
        # Simular processamento demorado
        import asyncio
        await asyncio.sleep(2)
        
        relatorio = {
            "id": relatorio_id,
            "tipo": "completo",
            "timestamp": datetime.now().isoformat(),
            "dados_completos": request.dados,
            "analise_detalhada": {
                "aspectos_juridicos": "Análise detalhada dos aspectos jurídicos...",
                "impacto_orcamentario": "Estimativa de impacto orçamentário...",
                "viabilidade_tecnica": "Avaliação da viabilidade técnica...",
                "cronograma_implementacao": "Cronograma sugerido para implementação..."
            },
            "anexos": [
                "Estudo de caso comparativo",
                "Planilha de custos estimados",
                "Minuta do projeto de lei"
            ]
        }
        
        self.relatorios_cache[relatorio_id] = relatorio
    
    def obter_relatorio(self, relatorio_id: str) -> Optional[Dict[str, Any]]:
        """Obtém relatório do cache"""
        return self.relatorios_cache.get(relatorio_id)
    
    def listar_comissoes_disponiveis(self) -> List[Dict[str, Any]]:
        """Lista todas as comissões disponíveis"""
        comissoes = []
        for comissao_id, info in self.comissoes_almg.items():
            comissoes.append({
                "id": comissao_id,
                "nome": info["nome"],
                "descricao": info["descricao"],
                "areas_competencia": info["areas"],
                "obrigatoria": info["obrigatoria"]
            })
        return comissoes

