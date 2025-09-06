import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from schemas import AcademicPaper

class AcademicService:
    def __init__(self):
        self.repositories = {
            'scielo': 'https://search.scielo.org/api/',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/',
            'repositorio_usp': 'https://repositorio.usp.br/api/',
            'bdtd': 'http://bdtd.ibict.br/api/',
            'capes': 'https://catalogodeteses.capes.gov.br/api/'
        }
        
        self.qualis_levels = {
            'A1': 5, 'A2': 4, 'B1': 3, 'B2': 2, 'B3': 1, 'B4': 0
        }
    
    async def search_papers(
        self,
        query: str,
        repositories: List[str] = None,
        qualis_level: str = "B2",
        max_results: int = 20
    ) -> List[AcademicPaper]:
        """
        Busca artigos acadêmicos
        """
        if repositories is None:
            repositories = ['scielo', 'pubmed']
        
        all_papers = []
        
        # Busca em cada repositório
        for repo in repositories:
            if repo in self.repositories:
                papers = await self._search_repository(repo, query, max_results)
                all_papers.extend(papers)
        
        # Filtra por nível Qualis
        filtered_papers = self._filter_by_qualis(all_papers, qualis_level)
        
        # Ordena por relevância
        sorted_papers = await self._rank_by_relevance(filtered_papers, query)
        
        return sorted_papers[:max_results]
    
    async def _search_repository(
        self, 
        repository: str, 
        query: str, 
        max_results: int
    ) -> List[AcademicPaper]:
        """
        Busca em um repositório específico
        """
        # Mock data por repositório
        if repository == 'scielo':
            return [
                AcademicPaper(
                    title=f"Análise de {query} no contexto brasileiro: uma revisão sistemática",
                    authors=["Silva, J.A.", "Santos, M.B.", "Oliveira, C.D."],
                    abstract=f"Este estudo apresenta uma análise abrangente sobre {query} no Brasil, examinando aspectos sociológicos, econômicos e políticos. A metodologia utilizou revisão sistemática de literatura com análise de 150 artigos publicados entre 2018 e 2024. Os resultados indicam tendências significativas e sugerem direcionamentos para políticas públicas efetivas.",
                    doi="10.1590/S0034-8910.2024001234",
                    repository="Scielo",
                    journal="Revista de Saúde Pública",
                    year=2024,
                    qualis_level="A1",
                    relevance_score=0.92,
                    citation_count=45,
                    keywords=[query, "políticas públicas", "Brasil", "análise"],
                    pdf_url=f"https://scielo.br/pdf/rsp/v58/pt_0034-8910-rsp-58-{query}.pdf",
                    published_date=datetime(2024, 3, 15)
                ),
                AcademicPaper(
                    title=f"Impactos de {query} na sociedade contemporânea",
                    authors=["Costa, A.F.", "Lima, R.S."],
                    abstract=f"Investigação sobre os impactos de {query} utilizando abordagem multidisciplinar. O estudo combina análise quantitativa e qualitativa com amostra de 2.500 participantes. Resultados mostram correlações significativas entre {query} e indicadores de desenvolvimento social.",
                    doi="10.1590/S1413-8123.2024002567",
                    repository="Scielo",
                    journal="Ciência & Saúde Coletiva",
                    year=2024,
                    qualis_level="A2",
                    relevance_score=0.87,
                    citation_count=23,
                    keywords=[query, "impactos sociais", "desenvolvimento"],
                    pdf_url=f"https://scielo.br/pdf/csc/v29n4/pt_1413-8123-csc-29-04-{query}.pdf",
                    published_date=datetime(2024, 1, 20)
                )
            ]
        
        elif repository == 'pubmed':
            return [
                AcademicPaper(
                    title=f"{query} and public health outcomes: a systematic review",
                    authors=["Johnson, A.B.", "Smith, C.D.", "Brown, E.F."],
                    abstract=f"Systematic review examining the relationship between {query} and public health outcomes. Analysis of 89 studies published between 2019-2024. Results demonstrate significant associations with health indicators and suggest evidence-based interventions.",
                    doi="10.1016/j.healthpol.2024.01.234",
                    repository="PubMed",
                    journal="Health Policy",
                    year=2024,
                    qualis_level="B1",
                    relevance_score=0.85,
                    citation_count=67,
                    keywords=[query, "public health", "systematic review"],
                    pdf_url=f"https://pubmed.ncbi.nlm.nih.gov/articles/PMC123456/pdf/{query}.pdf",
                    published_date=datetime(2024, 2, 10)
                )
            ]
        
        return []
    
    def _filter_by_qualis(self, papers: List[AcademicPaper], min_level: str) -> List[AcademicPaper]:
        """
        Filtra artigos por nível Qualis mínimo
        """
        min_score = self.qualis_levels.get(min_level, 2)
        return [
            paper for paper in papers 
            if self.qualis_levels.get(paper.qualis_level, 0) >= min_score
        ]
    
    async def _rank_by_relevance(
        self, 
        papers: List[AcademicPaper], 
        query: str
    ) -> List[AcademicPaper]:
        """
        Ordena artigos por relevância usando IA
        """
        # Simulação de ranking por IA
        # Em implementação real, usaria NLP para analisar abstracts
        return sorted(papers, key=lambda p: p.relevance_score, reverse=True)
    
    async def analyze_paper_relevance(
        self, 
        paper_id: str, 
        focus_keywords: str = None
    ) -> Dict:
        """
        Análise detalhada de relevância de um artigo
        """
        # Mock analysis
        analysis = {
            "paper_id": paper_id,
            "relevance_score": 0.89,
            "key_concepts": [
                "políticas públicas", "indicadores sociais", "análise quantitativa"
            ],
            "methodology": "Revisão sistemática com meta-análise",
            "sample_size": "150 estudos analisados",
            "main_findings": [
                "Correlação positiva significativa (p<0.001)",
                "Evidências consistentes em diferentes contextos",
                "Recomendações para políticas públicas"
            ],
            "limitations": [
                "Heterogeneidade dos estudos inclusos",
                "Variações metodológicas entre pesquisas"
            ],
            "policy_implications": [
                "Necessidade de investimento em ações preventivas",
                "Integração entre diferentes setores governamentais"
            ]
        }
        return analysis
    
    async def get_available_repositories(self) -> List[Dict]:
        """
        Lista repositórios disponíveis
        """
        repositories_info = [
            {
                "name": "Scielo",
                "description": "Biblioteca científica latino-americana",
                "focus": "Saúde, ciências sociais, humanas",
                "coverage": "América Latina, Caribe, Espanha, Portugal"
            },
            {
                "name": "PubMed",
                "description": "Base de dados biomédica internacional",
                "focus": "Medicina, ciências da vida",
                "coverage": "Internacional"
            },
            {
                "name": "BDTD",
                "description": "Biblioteca Digital de Teses e Dissertações",
                "focus": "Todas as áreas do conhecimento",
                "coverage": "Brasil"
            }
        ]
        return repositories_info

# Instância única do serviço
academic_service = AcademicService()