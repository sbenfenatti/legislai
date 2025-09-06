# Arquitetura do Backend - Auxiliar Legislativo Geral

## Visão Geral

O backend será desenvolvido como um agregador de APIs públicas brasileiras, funcionando como um auxiliar legislativo geral capaz de fornecer dados de diversas áreas para apoiar a criação de projetos de lei em diferentes temas. Com base na análise dos arquivos HTML fornecidos, o sistema deve ser capaz de:

1. **Pesquisar e agregar dados** de múltiplas fontes governamentais
2. **Justificar propostas legislativas** com dados estatísticos e oficiais
3. **Simular a tramitação** de projetos de lei nas comissões relevantes
4. **Gerar relatórios** e documentos estruturados

## Arquitetura Proposta

### 1. Estrutura Modular

O backend será estruturado em módulos especializados para facilitar a manutenção e escalabilidade:

```
backend/
├── app.py                 # Aplicação Flask principal
├── config.py             # Configurações da aplicação
├── requirements.txt      # Dependências Python
├── api_integrations/     # Módulo de integrações com APIs
│   ├── __init__.py
│   ├── ibge_api.py      # Integração com APIs do IBGE
│   ├── datasus_api.py   # Integração com APIs do DataSUS
│   ├── brasil_api.py    # Integração com Brasil API
│   ├── conecta_api.py   # Integração com Portal Conecta
│   └── base_api.py      # Classe base para APIs
├── services/            # Serviços de negócio
│   ├── __init__.py
│   ├── data_aggregator.py    # Agregação de dados
│   ├── legislative_analyzer.py # Análise legislativa
│   └── report_generator.py   # Geração de relatórios
├── models/              # Modelos de dados
│   ├── __init__.py
│   └── data_models.py
├── utils/               # Utilitários
│   ├── __init__.py
│   ├── cache_manager.py # Gerenciamento de cache
│   └── validators.py    # Validadores
└── static/              # Arquivos estáticos (frontend)
    ├── css/
    ├── js/
    └── index.html
```

### 2. Tecnologias e Ferramentas

- **Framework**: Flask (Python)
- **Cache**: Redis ou cache em memória para otimizar chamadas às APIs
- **Banco de Dados**: SQLite para desenvolvimento, PostgreSQL para produção
- **Autenticação**: JWT para APIs que requerem autenticação
- **Documentação**: Swagger/OpenAPI para documentar endpoints
- **Monitoramento**: Logs estruturados para acompanhar uso das APIs

### 3. Endpoints Principais

#### 3.1 Endpoints de Pesquisa de Dados
- `GET /api/v1/search/demographic` - Dados demográficos (IBGE)
- `GET /api/v1/search/health` - Dados de saúde (DataSUS)
- `GET /api/v1/search/economic` - Dados econômicos (Banco Central, IBGE)
- `GET /api/v1/search/education` - Dados de educação
- `GET /api/v1/search/security` - Dados de segurança pública
- `GET /api/v1/search/environment` - Dados ambientais
- `GET /api/v1/search/transport` - Dados de transporte

#### 3.2 Endpoints de Análise Legislativa
- `POST /api/v1/analyze/proposal` - Análise de proposta legislativa
- `GET /api/v1/analyze/similar-laws` - Busca por leis similares
- `POST /api/v1/simulate/tramitation` - Simulação de tramitação

#### 3.3 Endpoints de Geração de Relatórios
- `POST /api/v1/reports/generate` - Geração de relatórios
- `GET /api/v1/reports/{id}` - Recuperação de relatório
- `GET /api/v1/reports/{id}/pdf` - Download em PDF

#### 3.4 Endpoints de Metadados
- `GET /api/v1/apis/available` - Lista de APIs disponíveis
- `GET /api/v1/apis/{api_name}/status` - Status de uma API específica
- `GET /api/v1/health` - Health check do sistema

### 4. Integração com APIs Externas

#### 4.1 IBGE APIs
- **Localidades**: Dados de estados, municípios, distritos
- **Agregados**: Dados estatísticos de pesquisas
- **Malhas Geográficas**: Informações geográficas
- **Nomes**: Dados sobre nomes brasileiros
- **Notícias**: Releases e notícias do IBGE

#### 4.2 DataSUS APIs
- **CNES**: Cadastro Nacional de Estabelecimentos de Saúde
- **CNS**: Cartão Nacional de Saúde
- **SUS Digital**: Dados do sistema de saúde
- **Vacinação**: Dados de campanhas de vacinação

#### 4.3 Brasil API
- **CEP**: Consulta de endereços
- **CNPJ**: Dados de empresas
- **Bancos**: Informações bancárias
- **Feriados**: Feriados nacionais
- **Câmbio**: Taxas de câmbio

#### 4.4 Portal Conecta (Gov.br)
- **Cadastros do Cidadão**: CPF, CadÚnico, BPC
- **Cadastros de Empresas**: CNPJ, CADASTUR
- **Transparência**: Portal da Transparência, Siconfi
- **Veículos**: DENATRAN

### 5. Estratégias de Cache e Performance

#### 5.1 Cache em Múltiplas Camadas
- **Cache de Aplicação**: Redis para dados frequentemente acessados
- **Cache de API**: Cache específico para cada API externa
- **Cache de Relatórios**: Armazenamento temporário de relatórios gerados

#### 5.2 Rate Limiting
- Implementação de rate limiting para evitar sobrecarga das APIs externas
- Diferentes limites para diferentes tipos de APIs
- Retry automático com backoff exponencial

### 6. Tratamento de Erros e Fallbacks

#### 6.1 Estratégias de Fallback
- Múltiplas fontes para o mesmo tipo de dado
- Cache de dados críticos para disponibilidade offline
- Degradação graceful quando APIs estão indisponíveis

#### 6.2 Monitoramento e Alertas
- Logs estruturados para todas as chamadas de API
- Métricas de performance e disponibilidade
- Alertas automáticos para falhas críticas

### 7. Segurança e Autenticação

#### 7.1 Autenticação com APIs Governamentais
- Gerenciamento seguro de chaves de API
- Rotação automática de tokens quando possível
- Armazenamento seguro de credenciais

#### 7.2 Segurança da Aplicação
- CORS configurado adequadamente
- Validação rigorosa de entrada
- Rate limiting para prevenir abuso
- Logs de auditoria para todas as operações

### 8. Escalabilidade e Deploy

#### 8.1 Containerização
- Docker para facilitar deploy e escalabilidade
- Docker Compose para ambiente de desenvolvimento
- Kubernetes para produção (se necessário)

#### 8.2 Deploy
- Suporte para deploy no Vercel/Heroku para desenvolvimento
- Configuração para ambientes de produção
- CI/CD pipeline para automação

## Próximos Passos

1. **Implementação da estrutura base** do Flask
2. **Desenvolvimento dos módulos de integração** com as APIs prioritárias
3. **Implementação do sistema de cache** e tratamento de erros
4. **Desenvolvimento dos endpoints** principais
5. **Testes de integração** com as APIs externas
6. **Documentação** e deploy inicial

Esta arquitetura fornece uma base sólida para um sistema escalável e maintível que pode agregar dados de múltiplas fontes governamentais para auxiliar na criação de projetos de lei em diversas áreas.

