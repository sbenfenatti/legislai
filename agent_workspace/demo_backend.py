#!/usr/bin/env python3
"""
Script de demonstração do Backend do Assistente Legislativo
Integração com APIs Governamentais
"""

import httpx
import asyncio
import json
from typing import Dict, Any

class AssistenteLegislativoDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def verificar_status(self) -> Dict[str, Any]:
        """Verifica o status da API"""
        response = await self.client.get(f"{self.base_url}/health")
        return response.json()
    
    async def buscar_estados_ibge(self) -> Dict[str, Any]:
        """Busca lista de estados do IBGE"""
        response = await self.client.get(f"{self.base_url}/api/v1/ibge/localidades/estados")
        return response.json()
    
    async def buscar_municipios_mg(self) -> Dict[str, Any]:
        """Busca municípios de Minas Gerais"""
        response = await self.client.get(f"{self.base_url}/api/v1/ibge/localidades/municipios?uf=MG")
        return response.json()
    
    async def consultar_cep(self, cep: str) -> Dict[str, Any]:
        """Consulta CEP via Brasil API"""
        response = await self.client.get(f"{self.base_url}/api/v1/brasil-api/cep/{cep}")
        return response.json()
    
    async def buscar_estabelecimentos_saude(self) -> Dict[str, Any]:
        """Busca estabelecimentos de saúde (DataSUS simulado)"""
        response = await self.client.get(f"{self.base_url}/api/v1/datasus/cnes/estabelecimentos?uf=MG")
        return response.json()
    
    async def analisar_proposta_legislativa(self) -> Dict[str, Any]:
        """Analisa uma proposta legislativa"""
        proposta = {
            "objetivo": "Implementar sistema de IA para otimização de agendamentos em UBS",
            "ambito": "Estadual",
            "area_tematica": "Saúde",
            "justificativa": "Reduzir filas e absenteísmo no sistema de saúde",
            "solucao_proposta": "Utilizar inteligência artificial para melhorar a gestão de agendas",
            "resultados_esperados": "Redução de 30% no tempo de espera e 15% no absenteísmo"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/legislative/analyze",
            json=proposta
        )
        return response.json()
    
    async def simular_tramitacao(self) -> Dict[str, Any]:
        """Simula tramitação de projeto de lei"""
        proposta = {
            "objetivo": "Implementar sistema de IA para otimização de agendamentos em UBS",
            "ambito": "Estadual",
            "area_tematica": "Saúde",
            "justificativa": "Reduzir filas e absenteísmo no sistema de saúde",
            "solucao_proposta": "Utilizar inteligência artificial para melhorar a gestão de agendas",
            "resultados_esperados": "Redução de 30% no tempo de espera e 15% no absenteísmo"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/legislative/simulate/tramitation",
            json=proposta
        )
        return response.json()
    
    async def obter_template_projeto(self) -> Dict[str, Any]:
        """Obtém template para projeto de lei"""
        response = await self.client.get(f"{self.base_url}/api/v1/legislative/templates/project")
        return response.json()
    
    async def demonstrar_funcionalidades(self):
        """Executa demonstração completa"""
        print("🚀 DEMONSTRAÇÃO DO BACKEND - ASSISTENTE LEGISLATIVO")
        print("=" * 60)
        
        try:
            # 1. Verificar status
            print("\n1. 🏥 VERIFICANDO STATUS DA API")
            status = await self.verificar_status()
            print(f"Status: {status['status']}")
            print(f"Ambiente: {status['environment']}")
            
            # 2. Testar IBGE
            print("\n2. 🗺️ TESTANDO INTEGRAÇÃO IBGE")
            estados = await self.buscar_estados_ibge()
            print(f"Total de estados: {len(estados['data']['estados'])}")
            print(f"Primeiro estado: {estados['data']['estados'][0]['nome']}")
            
            municipios_mg = await self.buscar_municipios_mg()
            print(f"Municípios em MG: {len(municipios_mg['data']['municipios'])}")
            
            # 3. Testar Brasil API
            print("\n3. 🇧🇷 TESTANDO BRASIL API")
            try:
                cep_bh = await self.consultar_cep("30112000")
                if 'data' in cep_bh and 'endereco' in cep_bh['data']:
                    endereco = cep_bh['data']['endereco']
                    print(f"CEP 30112-000: {endereco['city']}, {endereco['state']}")
                    print(f"Endereço: {endereco['street']}")
                else:
                    print("Resposta da Brasil API:", json.dumps(cep_bh, indent=2)[:200])
            except Exception as e:
                print(f"Erro na consulta CEP: {e}")
            
            # 4. Testar DataSUS
            print("\n4. 🏥 TESTANDO DATASUS (SIMULADO)")
            estabelecimentos = await self.buscar_estabelecimentos_saude()
            print(f"Estabelecimentos encontrados: {len(estabelecimentos['data']['estabelecimentos'])}")
            
            # 5. Análise Legislativa
            print("\n5. ⚖️ TESTANDO ANÁLISE LEGISLATIVA")
            analise = await self.analisar_proposta_legislativa()
            print(f"Área temática: {analise['proposta']['area_tematica']}")
            print(f"Comissões relevantes: {', '.join(analise['comissoes_relevantes'])}")
            print(f"Probabilidade de aprovação: {analise['probabilidade_aprovacao']*100:.1f}%")
            print(f"Fontes utilizadas: {', '.join(analise['fontes_utilizadas'])}")
            
            # 6. Simulação de Tramitação
            print("\n6. 📋 SIMULAÇÃO DE TRAMITAÇÃO")
            tramitacao = await self.simular_tramitacao()
            print(f"Tempo estimado: {tramitacao['data']['simulacao']['tempo_estimado']}")
            print("Comissões:")
            for comissao in tramitacao['data']['simulacao']['comissoes']:
                print(f"  - {comissao['nome']}: {comissao['parecer']} ({comissao['tempo_estimado']})")
            
            # 7. Template de Projeto
            print("\n7. 📄 TEMPLATE DE PROJETO DE LEI")
            template = await self.obter_template_projeto()
            estrutura = template['data']['template']['estrutura']
            print(f"Estrutura disponível: {', '.join(estrutura.keys())}")
            
            print("\n✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
            print("🔗 Para acessar a documentação interativa:")
            print(f"   Swagger UI: {self.base_url}/docs")
            print(f"   ReDoc: {self.base_url}/redoc")
            
        except Exception as e:
            print(f"❌ Erro durante demonstração: {e}")
        
        finally:
            await self.client.aclose()

async def main():
    """Função principal"""
    demo = AssistenteLegislativoDemo()
    await demo.demonstrar_funcionalidades()

if __name__ == "__main__":
    asyncio.run(main())
