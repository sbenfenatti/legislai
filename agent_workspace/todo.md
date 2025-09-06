## Tarefas para o Backend

### Fase 1: Análise dos arquivos HTML fornecidos (Concluída)
- [x] Ler e entender os arquivos HTML fornecidos (1.html, 2.html, 3.html, 4.html, 5.html).

### Fase 2: Pesquisa e identificação de APIs do governo brasileiro (Em andamento)
- [x] Pesquisar APIs do governo brasileiro relacionadas a dados legislativos.
- [x] Pesquisar APIs do governo brasileiro relacionadas a dados de saúde (IBGE, DataSUS).
- [ ] Detalhar as APIs relevantes e suas funcionalidades para o projeto.

### Fase 3: Planejamento da arquitetura do backend (Concluída)
- [x] Definir a estrutura do projeto Flask.
- [x] Escolher bibliotecas e ferramentas necessárias.
- [x] Mapear as interações entre o frontend (HTMLs) e o backend.
- [x] Documentar a arquitetura proposta em detalhes.

### Fase 4: Implementação do backend Flask (Em andamento - mudou para FastAPI)
- [x] Configurar o ambiente de desenvolvimento.
- [x] Criar a estrutura básica do aplicativo FastAPI.
- [x] Implementar as rotas e endpoints para cada passo da plataforma.
- [x] Criar modelos Pydantic para validação de dados.
- [x] Implementar endpoints para IBGE, Brasil API, DataSUS (simulado), Portal Conecta (simulado).
- [x] Implementar endpoints para análise legislativa e geração de relatórios.
- [ ] Implementar os serviços de negócio (LegislativeAnalyzer, DataAggregator).
- [ ] Testar os endpoints básicos.

### Fase 5: Integração com APIs do governo
- [ ] Implementar chamadas às APIs do IBGE para dados demográficos/geográficos.
- [ ] Implementar chamadas às APIs do DataSUS para dados de saúde.
- [ ] Implementar chamadas a APIs legislativas (se encontradas e relevantes).
- [ ] Tratar e formatar os dados recebidos das APIs.

### Fase 6: Testes e validação do backend
- [ ] Desenvolver testes unitários e de integração.
- [ ] Testar a comunicação entre frontend e backend.
- [ ] Validar a integração com as APIs externas.

### Fase 7: Documentação e entrega do projeto
- [ ] Documentar o código e a arquitetura do backend.
- [ ] Fornecer instruções para setup e execução do projeto.
- [ ] Preparar um relatório final ou apresentação.



- [x] Detalhar as APIs relevantes e suas funcionalidades para o projeto, com foco na agregação.
  - [x] IBGE: API de Localidades (para obter dados geográficos como estados e municípios).
  - [x] IBGE: API de Agregados/Pesquisas (para dados estatísticos que possam justificar o projeto de lei, como população, dados de saúde, etc.).
  - [x] DataSUS: API CNES (Cadastro Nacional de Estabelecimentos de Saúde) para informações sobre UBS.
  - [ ] DataSUS: APIs relacionadas a agendamento e absenteísmo (se disponíveis - parece que o DataSUS não tem APIs diretas para isso, mas sim sistemas que geram dados que podem ser consumidos).
  - [x] Brasil API: Considerar o uso para CEP, CNPJ, Feriados Nacionais, IBGE (complementar), Taxas.
  - [x] Portal Gov.br/Conecta: Explorar APIs de diversas categorias (Cadastros do Cidadão, Empresas, Agricultura, Ambiental, Saúde, Autenticação Digital, Controle e Transparência, Gestão Administrativa/Financeira/Orçamentária da União, Veículos, etc.) para identificar as mais úteis para um auxiliar legislativo geral.
  - [ ] APIs de Cadastros do Cidadão (CPF, CadÚnico, BPC, ID Jovem, etc.)
  - [ ] APIs de Cadastros de Empresas (CNPJ, CADASTUR, etc.)
  - [ ] APIs de Saúde (CNS, etc.)
  - [ ] APIs de Controle e Transparência (Portal da Transparência, Siconfi, etc.)
  - [ ] APIs de Gestão Administrativa/Financeira/Orçamentária da União (para dados de despesas, receitas, etc.)
  - [ ] APIs de Veículos, Condutores e Infrações (DENATRAN, etc.)
  - [ ] Outras APIs relevantes como Metadados Estatísticos do IBGE, Certidão de Antecedentes Criminais, etc.
  - [ ] Analisar a viabilidade técnica de integrar um grande número de APIs com diferentes formatos e autenticações (necessário um wrapper ou biblioteca para cada tipo de API).


