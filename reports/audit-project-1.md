================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1 (sqlite3 da stdlib, SQL cru, sem ORM)
Domain:        API de E-commerce (produtos, usuários, pedidos, relatório de vendas)
Architecture:  Monolítica - 4 arquivos; rotas no app.py, SQL + regras + formatação no models.py, SQL também nos controllers
Source files:  4 files analyzed (~780 lines)
DB tables:     produtos, usuarios, pedidos, itens_pedido
Entry point:   app.py / `python app.py` (porta 5000)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 6 | HIGH: 4 | MEDIUM: 6 | LOW: 4

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: app.py:7
File: controllers.py:289
Description: `SECRET_KEY` fixa em `"minha-chave-super-secreta-123"` no código e devolvida em texto puro no `/health`.
Impact: Quem lê o repositório conhece a chave de sessão; trocar exige novo deploy.
Recommendation: P1 - ler a chave de variável de ambiente (config/settings.py) e remover do `/health`.

### [CRITICAL] AP-02 SQL Injection (queries montadas por concatenação)
File: models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 157-166, 174, 188, 192, 220, 224, 279-281, 289-297
Description: Todas as queries concatenam valores vindos da requisição (`"... WHERE id = " + str(id)`, `email`/`senha` no login, `termo` no LIKE da busca). Confirmado: `POST /login` com `' OR '1'='1` retorna 200.
Impact: Bypass de autenticação, vazamento e destruição de dados.
Recommendation: P2 - queries parametrizadas (`?`) em todos os models.

### [CRITICAL] AP-03 God File (models.py faz tudo)
File: models.py:1-314
File: database.py:7-86
Description: `models.py` mistura SQL, formatação de resposta, regras de negócio (estoque, total do pedido, desconto do relatório) de 4 domínios. `get_db()` cria conexão, cria schema e popula seed na mesma função.
Impact: Impossível testar isoladamente; qualquer mudança afeta todos os domínios.
Recommendation: P3 - um model por entidade, schema/seed separados, controllers por domínio.

### [CRITICAL] AP-04 Endpoints administrativos sem proteção
File: app.py:47-57
File: app.py:59-78
Description: `POST /admin/reset-db` apaga todas as tabelas e `POST /admin/query` executa SQL arbitrário vindo do body, sem nenhuma autenticação.
Impact: Qualquer cliente apaga ou lê o banco inteiro.
Recommendation: P13 - exigir token de admin vindo da config (desabilitado por padrão) e restringir `/admin/query` a um único SELECT.

### [CRITICAL] AP-05 Exposição de dados sensíveis
File: models.py:79-86, 95-102
File: controllers.py:285-289
File: controllers.py:12, 22, 62, 96, 109, 126, 134, 144, 165, 186, 220, 227, 235, 255, 262, 292
Description: `/usuarios` e `/usuarios/<id>` devolvem a coluna `senha`; `/health` expõe `secret_key`, `db_path` e `debug`; todos os handlers devolvem `str(e)` ao cliente.
Impact: Vazamento de credenciais e detalhes internos.
Recommendation: P6 e P8 - remover campos sensíveis dos serializadores e responder erro genérico.

### [CRITICAL] AP-06 Debug mode ativo em 0.0.0.0
File: app.py:8
File: app.py:88
File: controllers.py:286-288
Description: `DEBUG=True` e `app.run(host="0.0.0.0", debug=True)`; o `/health` ainda declara `"ambiente": "producao"`.
Impact: Debugger interativo do Werkzeug permite execução remota de código.
Recommendation: P1 - debug/host/porta vindos do ambiente, debug desligado por padrão.

### [HIGH] AP-07 Acesso a banco e regras dentro dos controllers
File: controllers.py:3
File: controllers.py:264-292
File: controllers.py:24-62
File: controllers.py:188-220, 237-255
Description: `health_check` executa SQL direto no controller; validações extensas de produto, "notificações" (prints de e-mail/SMS/push) e regras de status vivem no controller.
Impact: Camada de controle acoplada ao banco, regras não reaproveitáveis.
Recommendation: P4 - controllers finos; consultas e regras nos models.

### [HIGH] AP-08 Estado global mutável (conexão única)
File: database.py:4-5, 8-10
Description: `db_connection` e `db_path` são globais de módulo reatribuídos por `get_db()` (`global db_connection`), conexão única compartilhada com `check_same_thread=False`.
Impact: Race conditions entre requisições; testes não isolam estado.
Recommendation: P5 - conexão por requisição (`flask.g`) fechada no teardown.

### [HIGH] AP-09 Senhas em texto puro
File: database.py:75-83
File: models.py:105-111, 122-130
Description: Senhas gravadas e comparadas em texto puro (`WHERE ... senha = '...'`), seeds com `admin123`, `123456`.
Impact: Um vazamento do banco expõe todas as senhas.
Recommendation: P6 - `generate_password_hash` / `check_password_hash`.

### [HIGH] AP-10 Acoplamento forte e rotas dentro do app.py
File: app.py:3-4, 11-78
File: models.py:1-314 (cada função chama `get_db()`)
Description: `app.py` registra rotas, define handlers com SQL e importa `get_db`; todo model busca sua própria conexão global.
Impact: Não dá para trocar ou mockar o banco; entry point mistura responsabilidades.
Recommendation: P3 e P5 - rotas em views/, conexão injetada pelo app context, app.py só compõe.

### [MEDIUM] AP-12 Queries N+1
File: models.py:171-201
File: models.py:203-233
File: models.py:139-146, 154-166
Description: Para cada pedido consulta os itens, e para cada item consulta o nome do produto; `criar_pedido` consulta o produto duas vezes por item.
Impact: Latência cresce linearmente com o volume de pedidos.
Recommendation: P7 - uma query de itens com JOIN em produtos, agrupada em memória.

### [MEDIUM] AP-13 Código duplicado
File: models.py:12-21, 31-40, 304-313
File: models.py:177-200 e 209-232
File: controllers.py:30-50 e 74-90
Description: Mapeamento linha->dict repetido 3x (produtos) e 2x (pedidos); validação de criar/atualizar produto duplicada (e divergente).
Impact: Correção precisa ser aplicada em vários lugares; comportamento inconsistente entre POST e PUT.
Recommendation: P10 - `dict(row)` e um validador único.

### [MEDIUM] AP-14 Validação de entrada ausente ou inconsistente
File: controllers.py:43-46, 87-90
File: controllers.py:118-121
File: controllers.py:169-171, 239-243
File: controllers.py:198-201
File: app.py:61-62
Description: `preco < 0` quebra com string (500); `float(preco_min)` sem tratamento; `login`/`status`/`/admin/query` assumem JSON presente; itens do pedido sem validar `produto_id`/`quantidade`; e-mail sem checagem de formato.
Impact: Erros 500 em entradas inválidas, dados ruins gravados.
Recommendation: P12 - validar presença/tipo/faixa e responder 400.

### [MEDIUM] AP-15 Tratamento de erros espalhado
File: controllers.py:5-292 (try/except em cada handler)
Description: Mesmo `try/except Exception` repetido em 17 handlers, sem handler central.
Impact: Formato de erro inconsistente e vazamento de internals.
Recommendation: P8 - handler de erros centralizado.

### [MEDIUM] AP-16 Sem integridade referencial
File: database.py:36-52
File: models.py:65-70
Description: Tabelas sem FOREIGN KEY; deletar produto não considera `itens_pedido`; e-mail de usuário sem UNIQUE.
Impact: Pedidos órfãos, e-mails duplicados.
Recommendation: P11 - FKs e UNIQUE(email) no schema.

### [MEDIUM] AP-17 Escrita multi-passo sem transação controlada
File: models.py:133-169
Description: Checa estoque, cria pedido, itens e baixa estoque sem rollback em caso de falha; a conexão global fica com transação aberta.
Impact: Pedido parcial e estoque inconsistente.
Recommendation: P11 - transação única com commit/rollback.

### [LOW] AP-18 Magic numbers / strings
File: models.py:257-262
File: controllers.py:47-52, 242
File: app.py:88
Description: Faixas de desconto (10000/5000/1000 e 0.1/0.05/0.02), categorias, status e limites de nome inline.
Impact: Regras difíceis de achar e alterar.
Recommendation: P14 - constantes em config.

### [LOW] AP-19 Nomes ruins
File: controllers.py:14, 64, 98, 136
File: models.py:24, 54, 65, 89
File: models.py:187-191, 219-223
Description: Parâmetro `id` sombreia o builtin; `cursor2`/`cursor3`.
Impact: Leitura confusa.
Recommendation: P14 - renomear (`produto_id`) mantendo as rotas.

### [LOW] AP-20 print em vez de logger
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
File: app.py:56, 83-86
Description: Operação e "notificações simuladas" feitas com `print`.
Impact: Sem níveis, sem controle em produção.
Recommendation: P14 - módulo `logging`.

### [LOW] AP-21 Imports não usados
File: models.py:2
File: database.py:2
Description: `import sqlite3` em models.py e `import os` em database.py nunca usados.
Impact: Ruído.
Recommendation: P14 - remover.

## Deprecated APIs
No deprecated APIs detected (checked: Query.get, utcnow, before_first_request, json_encoder, md5/sha1, Buffer).

================================
Total: 20 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
