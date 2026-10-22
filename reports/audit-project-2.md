================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express ^4.18.2
Dependencies:  express, sqlite3 ^5.1.6
Domain:        LMS API com fluxo de checkout (cursos, matrículas, pagamentos, relatório financeiro)
Architecture:  Monolítica - uma classe `AppManager` cria schema, registra rotas e executa regras de negócio
Source files:  3 files analyzed (~180 lines)
DB tables:     users, courses, enrollments, payments, audit_logs (SQLite em memória)
Entry point:   src/app.js / `npm start` (porta 3000)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 5 | LOW: 4

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: src/utils.js:1-7
Description: `config` guarda `dbUser`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_..."` e `smtpUser` no código-fonte.
Impact: Chave de pagamento live e senhas expostas a qualquer pessoa com acesso ao repositório.
Recommendation: P1 - mover para variáveis de ambiente em src/config/settings.js.

### [CRITICAL] AP-05 Dados sensíveis em log
File: src/AppManager.js:45
Description: `console.log` imprime o número completo do cartão e a chave do gateway a cada checkout.
Impact: Violação de PCI-DSS e vazamento de segredo em logs.
Recommendation: P6 - logar apenas os 4 últimos dígitos e nunca a chave.

### [CRITICAL] AP-03 God Class (AppManager)
File: src/AppManager.js:4-139
Description: Uma classe cria o banco (10-23), registra rotas (25-137), implementa checkout (28-78), relatório financeiro (80-129) e exclusão de usuário (131-137).
Impact: Impossível testar em isolamento; qualquer mudança afeta todos os fluxos.
Recommendation: P3 - models, controllers, views e composition root separados.

### [CRITICAL] AP-04 Endpoints sensíveis sem autenticação
File: src/AppManager.js:80-129
File: src/AppManager.js:131-137
Description: `GET /api/admin/financial-report` expõe nomes e valores pagos de todos os alunos e `DELETE /api/users/:id` apaga usuários, ambos sem nenhuma verificação.
Impact: Vazamento de dados financeiros e exclusão de contas por qualquer cliente.
Recommendation: P13 - exigir token de admin vindo da config.

### [HIGH] AP-07 Regras de negócio dentro do handler da rota
File: src/AppManager.js:28-78
File: src/AppManager.js:104-122
Description: O handler de checkout valida, decide o pagamento (`cc.startsWith("4")`), cria usuário, matrícula, pagamento e auditoria; o relatório calcula receita dentro da rota.
Impact: Regras não reaproveitáveis nem testáveis sem HTTP.
Recommendation: P4 - controller fino e serviço de pagamento.

### [HIGH] AP-08 Estado global mutável
File: src/utils.js:9-10, 12-15, 25
File: src/AppManager.js:59
Description: `globalCache` é mutado por `logAndCache` e exportado; `totalRevenue` é global e nunca usado.
Impact: Estado compartilhado imprevisível entre requisições.
Recommendation: P5 - remover o estado global (ou injetá-lo no composition root).

### [HIGH] AP-09 Criptografia caseira e senha padrão
File: src/utils.js:17-23
File: src/AppManager.js:68
File: src/AppManager.js:18
Description: `badCrypto` repete base64 10 mil vezes e trunca em 10 caracteres; senha ausente vira `"123456"`; usuário seed com senha `'123'` em texto puro.
Impact: Senhas triviais de quebrar e contas com senha previsível.
Recommendation: P6 - `crypto.scrypt` com salt; exigir senha.

### [HIGH] AP-10 Acoplamento forte
File: src/AppManager.js:5-8
File: src/AppManager.js:25-26
File: src/app.js:8-10
Description: O construtor cria o próprio banco `:memory:`; `setupRoutes(app)` guarda `self = this` e registra rotas dentro da classe de dados.
Impact: Sem injeção de dependência; impossível trocar o banco.
Recommendation: P3 e P5 - banco injetado nos models.

### [HIGH] AP-11 Callback hell
File: src/AppManager.js:37-77
File: src/AppManager.js:83-128
Description: Até 7 níveis de callbacks aninhados e contadores manuais (`coursesPending`, `enrPending`) para juntar chamadas assíncronas.
Impact: Fluxo de erro esquecido, ordem de resposta não determinística.
Recommendation: P9 - promisify + async/await.

### [MEDIUM] AP-12 Queries N+1
File: src/AppManager.js:83-126
Description: Para cada curso consulta matrículas e, para cada matrícula, usuário e pagamento.
Impact: Número de queries cresce com cursos x matrículas.
Recommendation: P7 - uma query com JOIN.

### [MEDIUM] AP-14 Validação de entrada fraca
File: src/AppManager.js:29-35
File: src/AppManager.js:132
Description: Só verifica presença dos campos; sem formato de e-mail, sem tipo de `c_id`, sem validar `:id`.
Impact: Dados inválidos gravados.
Recommendation: P12 - validação no controller.

### [MEDIUM] AP-15 Tratamento de erros ignorado ou disperso
File: src/AppManager.js:57-61, 93, 104-106, 133-136
File: src/app.js:1-14
Description: Erros de `audit_logs`, `enrollments`, `users`, `payments` e do DELETE são ignorados; respostas de erro são strings soltas; sem middleware de erro.
Impact: Falhas silenciosas e `TypeError` quando `enrollments` vem indefinido.
Recommendation: P8 - middleware de erro central.

### [MEDIUM] AP-16 Dados órfãos ao excluir usuário
File: src/AppManager.js:131-137
Description: `DELETE FROM users` não remove matrículas/pagamentos (a própria resposta admite "ficaram sujos").
Impact: Relatório mostra "Unknown" e totais corrompidos.
Recommendation: P11 - exclusão em cascata.

### [MEDIUM] AP-17 Checkout sem transação
File: src/AppManager.js:50-61
Description: Matrícula, pagamento e auditoria são gravados em passos independentes.
Impact: Matrícula sem pagamento se um passo falhar.
Recommendation: P11 - sequência com tratamento de erro único.

### [LOW] AP-18 Magic numbers / strings
File: src/AppManager.js:46, 108
File: src/utils.js:19, 22
Description: `"4"`, `'PAID'`, `'DENIED'`, `10000` e `substring(0, 10)` inline.
Impact: Regras escondidas.
Recommendation: P14 - constantes nomeadas.

### [LOW] AP-19 Nomes ruins
File: src/AppManager.js:29-33
Description: `u`, `e`, `p`, `cid`, `cc` e campos `usr`, `eml`, `pwd`, `c_id`; classe `AppManager`.
Impact: Leitura difícil.
Recommendation: P14 - renomear internamente, mantendo as chaves do payload.

### [LOW] AP-20 console.log em vez de logger
File: src/AppManager.js:45
File: src/utils.js:13
File: src/app.js:13
Description: Logs operacionais com `console.log`.
Impact: Sem níveis nem controle.
Recommendation: P14 - logger simples.

### [LOW] AP-21 Código morto
File: src/utils.js:2-5, 10, 25
File: src/AppManager.js:2
Description: `dbUser`, `dbPass`, `smtpUser` nunca usados; `totalRevenue` importado e não usado.
Impact: Ruído e segredos desnecessários.
Recommendation: P14 - remover.

## Deprecated APIs
No deprecated APIs detected (checked: new Buffer, createCipher, url.parse, fs.exists, request, body-parser, var).

================================
Total: 18 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
