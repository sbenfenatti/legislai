import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from schemas import NewsArticle

class NewsService:
    def __init__(self):
        self.sources = {
            'hegemonica': {
                'Folha de S.Paulo': 'https://www1.folha.uol.com.br/',
                'O Globo': 'https://oglobo.globo.com/',
                'Estado de S.Paulo': 'https://estadao.com.br/',
                'G1': 'https://g1.globo.com/',
                'UOL': 'https://uol.com.br/'
            },
            'esquerda': {
                'Brasil 247': 'https://brasil247.com/',
                'Mídia Ninja': 'https://midianinja.org/',
                'Cart Capital': 'https://cartacapital.com.br/',
                'Brasil de Fato': 'https://brasildefato.com.br/',
                'Rede Brasil Atual': 'https://redebrasilatual.com.br/'
            },
            'direita': {
                'Gazeta do Povo': 'https://gazetadopovo.com.br/',
                'Jovem Pan': 'https://jovempan.com.br/',
                'Terrá Brasil': 'https://terrabrasil.com.br/',
                'Oeste': 'https://revistaoeste.com/',
                'Crítica Nacional': 'https://criticanacional.com.br/'
            },
            'internacional': {
                'Reuters': 'https://reuters.com/',
                'BBC Brasil': 'https://bbc.com/portuguese/',
                'CNN Brasil': 'https://cnnbrasil.com.br/',
                'El País Brasil': 'https://brasil.elpais.com/',
                'Deutsche Welle': 'https://dw.com/pt-br/'
            }
        }
    
    async def search_news(
        self,
        query: str,
        sources: List[str] = None,
        political_spectrum: str = None,
        timeframe: str = "30d",
        max_results: int = 50
    ) -> List[NewsArticle]:
        """
        Busca notícias sobre um tema
        """
        all_articles = []
        
        # Define espectros a buscar
        spectrums_to_search = []
        if political_spectrum:
            if political_spectrum in self.sources:
                spectrums_to_search = [political_spectrum]
        else:
            spectrums_to_search = list(self.sources.keys())
        
        # Busca em cada espectro
        for spectrum in spectrums_to_search:
            articles = await self._search_by_spectrum(query, spectrum, timeframe, max_results)
            all_articles.extend(articles)
        
        # Ordena por data (mais recentes primeiro)
        sorted_articles = sorted(
            all_articles, 
            key=lambda a: a.published_date, 
            reverse=True
        )
        
        return sorted_articles[:max_results]
    
    async def _search_by_spectrum(
        self,
        query: str,
        spectrum: str,
        timeframe: str,
        max_results: int
    ) -> List[NewsArticle]:
        """
        Busca notícias em um espectro político específico
        """
        articles = []
        
        # Mock data baseado no espectro
        if spectrum == 'hegemonica':
            articles = [
                NewsArticle(
                    title=f"{query}: governo anuncia novas medidas para setor",
                    summary=f"O governo federal anunciou hoje um pacote de medidas relacionadas a {query}, incluindo investimentos de R$ 2,5 bilhões e novas regulamentações. A iniciativa visa modernizar o setor e atender demandas da sociedade.",
                    source="Folha de S.Paulo",
                    author="Repórter Político",
                    published_date=datetime.now() - timedelta(hours=6),
                    url="https://folha.uol.com.br/politica/2024/03/governo-anuncia-medidas.shtml",
                    political_spectrum="hegemonica",
                    tags=[query, "governo", "políticas públicas"],
                    sentiment_score=0.65,
                    credibility_score=0.85
                ),
                NewsArticle(
                    title=f"Especialistas avaliam impacto de {query} na economia",
                    summary=f"Economistas ouvidos pela reportagem destacam que as mudanças em {query} podem ter impactos significativos no PIB brasileiro. Projeções indicam crescimento de 0,3% no setor nos próximos 12 meses.",
                    source="O Globo",
                    author="Equipe de Economia",
                    published_date=datetime.now() - timedelta(hours=12),
                    url="https://oglobo.globo.com/economia/noticia/2024/03/especialistas-avaliam.html",
                    political_spectrum="hegemonica",
                    tags=[query, "economia", "especialistas"],
                    sentiment_score=0.72,
                    credibility_score=0.88
                )
            ]
        
        elif spectrum == 'esquerda':
            articles = [
                NewsArticle(
                    title=f"{query}: movimentos sociais criticam falta de participação popular",
                    summary=f"Organizações da sociedade civil denunciam que as políticas relacionadas a {query} foram formuladas sem consulta aos principais afetados. Manifestações estão marcadas para a próxima semana.",
                    source="Brasil 247",
                    author="Movimento Social Reporter",
                    published_date=datetime.now() - timedelta(hours=8),
                    url="https://brasil247.com/brasil/movimentos-sociais-criticam",
                    political_spectrum="esquerda",
                    tags=[query, "movimentos sociais", "participação popular"],
                    sentiment_score=0.35,
                    credibility_score=0.75
                )
            ]
        
        elif spectrum == 'direita':
            articles = [
                NewsArticle(
                    title=f"{query}: setor privado vê oportunidades de investimento",
                    summary=f"Empresas do setor privado manifestam interesse em investir em {query}, especialmente após sinalizações de desburocratização. Estimativas apontam para R$ 5 bilhões em novos investimentos.",
                    source="Gazeta do Povo",
                    author="Editor de Negócios",
                    published_date=datetime.now() - timedelta(hours=4),
                    url="https://gazetadopovo.com.br/economia/setor-privado-oportunidades",
                    political_spectrum="direita",
                    tags=[query, "setor privado", "investimentos"],
                    sentiment_score=0.78,
                    credibility_score=0.80
                )
            ]
        
        elif spectrum == 'internacional':
            articles = [
                NewsArticle(
                    title=f"Brazil's approach to {query} draws international attention",
                    summary=f"International observers analyze Brazil's new policies regarding {query}. Experts from WHO and UN highlight innovative aspects while pointing out implementation challenges.",
                    source="Reuters",
                    author="Brazil Correspondent",
                    published_date=datetime.now() - timedelta(hours=10),
                    url="https://reuters.com/world/americas/brazil-approach-draws-attention",
                    political_spectrum="internacional",
                    tags=[query, "internacional", "políticas"],
                    sentiment_score=0.68,
                    credibility_score=0.92
                )
            ]
        
        return articles
    
    async def get_news_sources(self, spectrum: str = None) -> Dict:
        """
        Lista fontes de notícias por espectro
        """
        if spectrum and spectrum in self.sources:
            return {spectrum: self.sources[spectrum]}
        return self.sources
    
    async def analyze_coverage(
        self,
        query: str,
        days: int = 30,
        compare_spectrum: bool = True
    ) -> Dict:
        """
        Análise da cobertura midiática
        """
        coverage_analysis = {
            "query": query,
            "period": f"{days} dias",
            "total_articles": 156,
            "coverage_by_spectrum": {
                "hegemonica": {
                    "articles": 78,
                    "avg_sentiment": 0.65,
                    "main_angles": ["políticas governamentais", "impacto econômico"]
                },
                "esquerda": {
                    "articles": 34,
                    "avg_sentiment": 0.42,
                    "main_angles": ["críticas sociais", "falta de participação"]
                },
                "direita": {
                    "articles": 29,
                    "avg_sentiment": 0.73,
                    "main_angles": ["oportunidades de mercado", "setor privado"]
                },
                "internacional": {
                    "articles": 15,
                    "avg_sentiment": 0.68,
                    "main_angles": ["comparações internacionais", "análise técnica"]
                }
            },
            "trending_keywords": [
                {"keyword": query, "frequency": 156},
                {"keyword": "políticas públicas", "frequency": 89},
                {"keyword": "investimento", "frequency": 67},
                {"keyword": "sociedade", "frequency": 45}
            ],
            "timeline": {
                "peak_coverage": datetime.now() - timedelta(days=7),
                "coverage_trend": "crescente",
                "major_events": [
                    "Anúncio governamental (7 dias atrás)",
                    "Manifestação social (3 dias atrás)",
                    "Debate no Congresso (1 dia atrás)"
                ]
            }
        }
        
        return coverage_analysis

# Instância única do serviço
news_service = NewsService()