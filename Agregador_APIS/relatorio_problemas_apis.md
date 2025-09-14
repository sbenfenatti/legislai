# 🔧 RELATÓRIO DE PROBLEMAS - APIs GOVERNO BRASILEIRO

Gerado automaticamente em: 14/09/2025 13:27:38

## 📊 PORTAL_TRANSPARENCIA

- **Total endpoints**: 62
- **Funcionando**: 26
- **Precisa token**: 0
- **Parâmetros errados**: 32
- **Método errado**: 0

### ❌ Endpoints com Problemas:

- `/despesas/por-orgao`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/despesas/por-funcional-programatica`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/despesas/recursos-recebidos`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/despesas/por-favorecido`: ❌ ERRO 403 - (Forbidden)
- `/servidores`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/servidores/{id}`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/servidores/remuneracao`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/viagens`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/licitacoes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/licitacoes/por-ug-modalidade-numero`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/licitacoes/participantes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/contratos`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/contratos/{id}`: ❌ ERRO 403 - (Forbidden)
- `/convenios`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/novo-bolsa-familia-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/novo-bolsa-familia-sacado-por-nis`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/novo-bolsa-familia-disponivel-por-cpf-ou-nis`: ❌ ERRO 403 - (Forbidden)
- `/bolsa-familia-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/bolsa-familia-sacado-por-nis`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/bpc-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/bpc-por-cpf-ou-nis`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/bpc-beneficiario-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/auxilio-emergencial-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/auxilio-emergencial-por-cpf-ou-nis`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/auxilio-brasil-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/auxilio-brasil-sacado-por-nis`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/peti-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/peti-por-cpf-ou-nis`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/safra-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/safra-codigo-por-cpf-ou-nis`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/seguro-defeso-por-municipio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/seguro-defeso-codigo`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/cartoes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/notas-fiscais`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/notas-fiscais-por-chave`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/coronavirus/auxilio-emergencial`: ❌ ERRO 403 - (Forbidden)

## 📊 BRASIL_API

- **Total endpoints**: 11
- **Funcionando**: 11
- **Precisa token**: 0
- **Parâmetros errados**: 0
- **Método errado**: 0

## 📊 CAMARA_DEPUTADOS

- **Total endpoints**: 27
- **Funcionando**: 5
- **Precisa token**: 0
- **Parâmetros errados**: 14
- **Método errado**: 8

### ❌ Endpoints com Problemas:

- `/deputados/{id}`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/deputados/{id}/despesas`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/deputados/{id}/discursos`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/deputados/relatorioQuadroResumo`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/deputados/emexercicio`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/proposicoes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/proposicoes/{id}`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/proposicoes/{id}/tramitacoes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/proposicoes/{id}/votacoes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/votacoes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/votacoes/{id}`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/plenarinho/votacoes`: ❌ MÉTODO ERRADO - (Method Not Allowed)
- `/frentes/{id}`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/orgaos/{id}/deputados`: ❌ MÉTODO ERRADO - (Method Not Allowed)
- `/comissoes`: ❌ MÉTODO ERRADO - (Method Not Allowed)
- `/comissoes/{id}`: ❌ MÉTODO ERRADO - (Method Not Allowed)
- `/deputados/{id}/frentes`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/deputados/{id}/comissoes`: ❌ MÉTODO ERRADO - (Method Not Allowed)
- `/deputados/{id}/orgaos`: ⚠️ PARÂMETROS ERRADOS - (Bad Request - revisar parâmetros)
- `/referencias/temas`: ❌ MÉTODO ERRADO - (Method Not Allowed)
- `/referencias/siglasPartidos`: ❌ MÉTODO ERRADO - (Method Not Allowed)
- `/referencias/siglasUfs`: ❌ MÉTODO ERRADO - (Method Not Allowed)

## 📊 SENADO_FEDERAL

- **Total endpoints**: 9
- **Funcionando**: 8
- **Precisa token**: 0
- **Parâmetros errados**: 0
- **Método errado**: 0

### ❌ Endpoints com Problemas:

- `/plenario/lista/votacao/{data}`: ❌ NÃO ENCONTRADO - (Endpoint inválido)

## 📊 DADOS_GOV

- **Total endpoints**: 6
- **Funcionando**: 6
- **Precisa token**: 0
- **Parâmetros errados**: 0
- **Método errado**: 0

## 📊 IBGE

- **Total endpoints**: 9
- **Funcionando**: 8
- **Precisa token**: 0
- **Parâmetros errados**: 0
- **Método errado**: 0

### ❌ Endpoints com Problemas:

- `/censos/nomes/{nome}`: ❌ NÃO ENCONTRADO - (Endpoint inválido)

## 📊 BANCO_CENTRAL

- **Total endpoints**: 3
- **Funcionando**: 1
- **Precisa token**: 0
- **Parâmetros errados**: 0
- **Método errado**: 0

### ❌ Endpoints com Problemas:

- `/CotacaoMoedaDia(moeda=@moeda,dataCotacao=@data)`: 💥 ERRO SERVIDOR - (Internal Server Error)
- `/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinal)`: 💥 ERRO SERVIDOR - (Internal Server Error)

