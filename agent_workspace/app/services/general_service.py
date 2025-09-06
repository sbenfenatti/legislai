import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from schemas import GeneralSearchResult

class GeneralSearchService:
    def __init__(self):
        self.institutional_sites = {
            'ong': [
                'https://www.greenpeace.org.br/',
                'https://www.wwf.org.br/',
                'https://www.oxfam.org.br/',
                'https://www.actionaid.org.br/'
            ],
            'instituto': [
                'https://www.ipea.gov.br/',
                'https://www.fgv.br/',
                'https://www.institutounibanco.org.br/',
                'https://www.abrasco.org.br/'
            ],
            'fundacao': [
                'https://www.fapesp.br/',
                'https://www.fundacaogetuliovargas.org.br/',
                'https://www.fundacaooswaldomercury.org.br/'
            ],
            'org_internacional': [
                'https://www.who.int/',
                'https://www.unesco.org/',
                'https://www.worldbank.org/',
                'https://www.oecd.org/'
            ]
        }
        
        self.file_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
    
    async def perform_general_search(
        self,
        query: str,
        site_types: List[str] = None,
        file_types: List[str] = None,
        max_results: int = 30
    ) -> List[GeneralSearchResult]:
        """
        Busca geral complementar (tipo Google)
        """
        results = []
        
        # Busca em sites institucionais
        institutional_results = await self._search_institutional_sites(query, site_types)
        results.extend(institutional_results)
        
        # Busca documentos técnicos
        document_results = await self._search_technical_documents(query, file_types)
        results.extend(document_results)
        
        # Busca geral na web
        web_results = await self._search_general_web(query)
        results.extend(web_results)
        
        # Ordena por relevância
        sorted_results = sorted(results, key=lambda r: r.relevance_score, reverse=True)
        
        return sorted_results[:max_results]
    
    async def _search_institutional_sites(
        self,
        query: str,
        site_types: List[str] = None
    ) -> List[GeneralSearchResult]:
        """
        Busca em sites institucionais
        """
        results = []
        
        # Mock data para sites institucionais
        institutional_results = [
            GeneralSearchResult(
                title=f"Relatório IPEA: Análise de {query} no Brasil (2024)",
                summary=f"Estudo abrangente do IPEA sobre {query}, incluindo dados estatísticos, análises regionais e recomendações de políticas públicas. O documento apresenta tendências dos últimos 5 anos e projeções futuras.",
                url="https://ipea.gov.br/portal/publicacoes/relatorio-2024",
                source_type="instituto",
                organization="IPEA - Instituto de Pesquisa Econômica Aplicada",
                file_type="pdf",
                published_date=datetime(2024, 2, 15),
                relevance_score=0.91,
                content_type="relatório técnico",
                language="pt",
                tags=[query, "ipea", "políticas públicas", "brasil"]
            ),
            GeneralSearchResult(
                title=f"White Paper: {query} e Desenvolvimento Sustentável",
                summary=f"Documento da Fundação Getúlio Vargas analisando a relação entre {query} e os Objetivos de Desenvolvimento Sustentável da ONU. Inclui casos de estudo e melhores práticas internacionais.",
                url="https://fgv.br/publicacoes/white-paper-2024",
                source_type="fundacao",
                organization="FGV - Fundação Getúlio Vargas",
                file_type="pdf",
                published_date=datetime(2024, 1, 10),
                relevance_score=0.87,
                content_type="white paper",
                language="pt",
                tags=[query, "fgv", "sustentabilidade", "ods"]
            ),
            GeneralSearchResult(
                title=f"Posição da Oxfam sobre {query} no contexto brasileiro",
                summary=f"Documento de posição da Oxfam Brasil sobre {query}, destacando impactos na desigualdade social e propondo ações para promoção da justiça social. Inclui dados de pesquisa própria e recomendações.",
                url="https://oxfam.org.br/posicionamento-2024",
                source_type="ong",
                organization="Oxfam Brasil",
                file_type="pdf",
                published_date=datetime(2024, 3, 5),
                relevance_score=0.83,
                content_type="posicionamento",
                language="pt",
                tags=[query, "oxfam", "desigualdade", "justiça social"]
            )
        ]
        
        return institutional_results
    
    async def _search_technical_documents(
        self,
        query: str,
        file_types: List[str] = None
    ) -> List[GeneralSearchResult]:
        """
        Busca documentos técnicos específicos
        """
        if file_types is None:
            file_types = ['pdf']
        
        documents = [
            GeneralSearchResult(
                title=f"Manual Técnico: Implementação de {query}",
                summary=f"Manual técnico detalhado para implementação de políticas relacionadas a {query}. Inclui metodologias, indicadores de monitoramento e casos práticos de implementação em municípios brasileiros.",
                url="https://portalconhecimento.gov.br/manual-tecnico-2024.pdf",
                source_type="governo",
                organization="Ministério do Planejamento",
                file_type="pdf",
                published_date=datetime(2024, 2, 20),
                relevance_score=0.89,
                content_type="manual técnico",
                language="pt",
                tags=[query, "manual", "implementação", "municípios"]
            ),
            GeneralSearchResult(
                title=f"Planilha de Indicadores: {query} por Estado",
                summary=f"Planilha com indicadores detalhados sobre {query} organizados por estado brasileiro. Dados atualizados trimestralmente com séries históricas e projeções.",
                url="https://dados.gov.br/planilhas/indicadores-estaduais.xlsx",
                source_type="governo",
                organization="Portal de Dados Abertos",
                file_type="xlsx",
                published_date=datetime(2024, 3, 1),
                relevance_score=0.85,
                content_type="base de dados",
                language="pt",
                tags=[query, "indicadores", "estados", "dados"]
            )
        ]
        
        return documents
    
    async def _search_general_web(
        self,
        query: str
    ) -> List[GeneralSearchResult]:
        """
        Busca geral na web
        """
        web_results = [
            GeneralSearchResult(
                title=f"Observatório de {query} - Dados e Análises",
                summary=f"Portal especializado em monitoramento de {query} no Brasil. Oferece dados atualizados, análises de especialistas e ferramentas interativas para visualização de indicadores.",
                url=f"https://observatorio{query.replace(' ', '')}.org.br",
                source_type="observatorio",
                organization="Observatório Independente",
                file_type="html",
                published_date=datetime(2024, 3, 10),
                relevance_score=0.82,
                content_type="portal especializado",
                language="pt",
                tags=[query, "observatório", "monitoramento", "dados"]
            ),
            GeneralSearchResult(
                title=f"Fórum Nacional sobre {query}: Conclusões e Recomendações",
                summary=f"Documento com as conclusões do Fórum Nacional sobre {query}, realizado em 2024. Reúne contribuições de especialistas, gestores públicos e sociedade civil.",
                url="https://forumnacional.org.br/conclusoes-2024",
                source_type="forum",
                organization="Fórum Nacional",
                file_type="pdf",
                published_date=datetime(2024, 1, 25),
                relevance_score=0.80,
                content_type="relatório de evento",
                language="pt",
                tags=[query, "forum", "especialistas", "recomendações"]
            )
        ]
        
        return web_results
    
    async def search_institutional_content(
        self,
        query: str,
        category: str = None
    ) -> List[GeneralSearchResult]:
        """
        Busca específica em sites institucionais
        """
        return await self._search_institutional_sites(query, [category] if category else None)
    
    async def find_technical_reports(
        self,
        query: str,
        organization_type: str = None
    ) -> List[GeneralSearchResult]:
        """
        Busca relatórios técnicos específicos
        """
        reports = [
            GeneralSearchResult(
                title=f"Relatório Anual 2024: {query} no Brasil",
                summary=f"Relatório anual abrangente sobre o estado de {query} no Brasil, incluindo progressão de indicadores, desafios identificados e recomendações estratégicas para o próximo período.",
                url="https://relatorioanual.org.br/2024",
                source_type="relatorio",
                organization="Instituto Brasileiro de Estudos",
                file_type="pdf",
                published_date=datetime(2024, 1, 15),
                relevance_score=0.93,
                content_type="relatório anual",
                language="pt",
                tags=[query, "relatório anual", "brasil", "indicadores"]
            ),
            GeneralSearchResult(
                title=f"Estudo de Caso: Implementação de {query} em São Paulo",
                summary=f"Análise detalhada da implementação de políticas relacionadas a {query} no município de São Paulo, incluindo desafios, soluções adotadas e resultados alcançados.",
                url="https://estudos.prefeitura.sp.gov.br/caso-2024",
                source_type="estudo_caso",
                organization="Prefeitura de São Paulo",
                file_type="pdf",
                published_date=datetime(2024, 2, 28),
                relevance_score=0.88,
                content_type="estudo de caso",
                language="pt",
                tags=[query, "são paulo", "estudo de caso", "implementação"]
            )
        ]
        
        return reports

# Instância única do serviço
general_service = GeneralSearchService()