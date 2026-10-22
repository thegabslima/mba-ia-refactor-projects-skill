================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0, marshmallow, requests, python-dotenv (as 3 últimas não são usadas)
Domain:        API de Task Manager (tasks, usuários, categorias, relatórios)
Architecture:  Em camadas, com violações - existem models/routes/services/utils, mas as rotas concentram queries e regras e não há controllers nem config
Source files:  15 files analyzed (~1160 lines)
DB tables:     tasks, users, categories (SQLAlchemy / SQLite)
Entry point:   app.py / `python app.py` (porta 5000; `python seed.py` antes)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask (Flask-SQLAlchemy)
Files:   15 analyzed | ~1160 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 7 | LOW: 4

## Findings

### [CRITICAL] AP-01 Hardcoded Credentials
File: app.py:13
File: services/notification_service.py:7-10
Description: `SECRET_KEY = 'super-secret-key-123'` e credenciais SMTP (`taskmanager@gmail.com` / `senha123`) no código.
Impact: Segredos expostos no repositório.
Recommendation: P1 - config/settings.py lendo do ambiente.

### [CRITICAL] AP-05 Exposição de dados sensíveis
File: models/user.py:16-25
File: routes/user_routes.py:33, 85, 129, 209
Description: `User.to_dict()` inclui o campo `password` (hash) e é devolvido por `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
Impact: Hash de senha vaza em quatro endpoints (confirmado em execução).
Recommendation: P6 - remover `password` do serializador.

### [CRITICAL] AP-06 Debug mode em 0.0.0.0
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)`.
Impact: Debugger do Werkzeug exposto na rede permite execução remota de código.
Recommendation: P1 - debug e host vindos da config (padrão seguro).

### [HIGH] AP-07 Lógica de negócio e queries dentro das rotas (sem controllers)
File: routes/task_routes.py:12-63, 85-154, 156-223, 273-299
File: routes/user_routes.py:153-183
File: routes/report_routes.py:12-101, 103-155
File: routes/report_routes.py:157-223
Description: Os arquivos de rotas validam, consultam o banco, calculam estatísticas (overdue, taxas) e serializam; o CRUD de categorias está dentro de `report_routes.py`. `services/` existe mas nunca é usado.
Impact: Regras não testáveis sem HTTP; camadas misturadas.
Recommendation: P3 e P4 - criar controllers por domínio; rotas só mapeiam URLs.

### [HIGH] AP-09 Hash fraco (MD5) e token falso
File: models/user.py:29, 32
File: routes/user_routes.py:210
Description: Senhas com `hashlib.md5` sem salt; o login devolve `'fake-jwt-token-' + id`.
Impact: Senhas quebráveis em segundos; qualquer um forja um token.
Recommendation: P6 - `generate_password_hash` e token assinado (itsdangerous).

### [MEDIUM] AP-12 Queries N+1
File: routes/task_routes.py:41-57
File: routes/user_routes.py:22
File: routes/report_routes.py:55-68, 163
Description: `User.query.get` e `Category.query.get` por task; `len(u.tasks)` por usuário; consulta de tasks por usuário e `count()` por categoria nos relatórios.
Impact: Cresce linearmente com o volume.
Recommendation: P7 - joinedload e agregações com GROUP BY.

### [MEDIUM] AP-13 Código duplicado
File: routes/task_routes.py:30-39, 71-80, 283-287
File: routes/user_routes.py:171-180
File: routes/report_routes.py:34-43, 132-135
File: models/task.py:50-60
File: routes/task_routes.py:17-28 (duplica `Task.to_dict`)
File: routes/user_routes.py:61, 106 e utils/helpers.py:19-23
Description: A regra "atrasada" aparece em 7 lugares apesar de existir `Task.is_overdue()` (não usado); listas de status/roles e regex de e-mail repetidas.
Impact: Correção precisa ser feita em vários pontos.
Recommendation: P10 - usar `Task.is_overdue()` e constantes únicas.

### [MEDIUM] AP-14 Validação incompleta
File: routes/task_routes.py:113, 182
File: routes/task_routes.py:261, 264
File: routes/report_routes.py:196-197
File: routes/user_routes.py:103, 125
Description: `priority < 1` com string gera 500; `int(priority)` sem tratamento; `PUT /categories/<id>` sem body quebra; `name` e `active` sem validação.
Impact: 500 em entradas inválidas.
Recommendation: P12 - validadores nos controllers.

### [MEDIUM] AP-15 Except genérico e sem handler central
File: routes/task_routes.py:62, 137, 204, 236
File: routes/user_routes.py:130, 149
File: routes/report_routes.py:186, 207, 221
File: utils/helpers.py:46, 49, 88
Description: `except:` sem tipo engole qualquer erro; não há error handler no app.
Impact: Falhas escondidas e respostas inconsistentes.
Recommendation: P8 - handler central.

### [MEDIUM] AP-16 Integridade ao excluir categoria/usuário
File: routes/report_routes.py:211-223
File: models/task.py:13-14
File: routes/user_routes.py:140-145
Description: Excluir categoria deixa tasks com `category_id` pendurado; exclusão de usuário apaga tasks manualmente na rota em vez de cascade no model.
Impact: Referências inválidas.
Recommendation: P11 - cascade/ON DELETE SET NULL no model.

### [MEDIUM] DEP-1 API deprecated: `Query.get()` (SQLAlchemy 2.x)
File: routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227
File: routes/user_routes.py:29, 94, 136, 155
File: routes/report_routes.py:105, 192, 213
Description: `Model.query.get(id)` é legado no SQLAlchemy 2.
Impact: Warnings hoje, remoção futura.
Recommendation: P15 - `db.session.get(Model, id)`.

### [MEDIUM] DEP-2 API deprecated: `datetime.utcnow()` (Python 3.12+)
File: models/category.py:11
File: models/task.py:15-16, 52
File: models/user.py:14
File: routes/task_routes.py:31, 72, 215, 285
File: routes/user_routes.py:172
File: routes/report_routes.py:35, 42, 45, 71, 133
File: services/notification_service.py:35
File: utils/helpers.py:38
Description: `utcnow()` está deprecated desde o Python 3.12.
Impact: DeprecationWarning e datetimes naive ambíguos.
Recommendation: P15 - `datetime.now(timezone.utc)` via helper único.

### [LOW] AP-18 Magic numbers / strings
File: routes/task_routes.py:96-100, 110, 113, 177, 182
File: routes/user_routes.py:64, 71, 115, 120
File: utils/helpers.py:110-116 (constantes definidas e nunca usadas)
Description: Prioridade 1-5, tamanhos de título, tamanho mínimo de senha, listas de status/roles inline.
Impact: Regras duplicadas e inconsistentes.
Recommendation: P14 - config/constants.

### [LOW] AP-19 Nomes e idiomas ruins
File: routes/task_routes.py:16, 141, 210
File: utils/helpers.py:57-108
Description: `t`, `cat`, `p`, `s`; `type(x) == list` em vez de `isinstance`.
Impact: Leitura e robustez.
Recommendation: P14.

### [LOW] AP-20 print em vez de logger
File: routes/task_routes.py:149, 153, 219, 234
File: routes/user_routes.py:83, 89, 147
File: services/notification_service.py:21, 24
File: utils/helpers.py:39-41
Description: Logs operacionais com `print`.
Impact: Sem níveis.
Recommendation: P14 - `logging`.

### [LOW] AP-21 Código morto e imports não usados
File: routes/task_routes.py:7
File: routes/user_routes.py:6
File: routes/report_routes.py:7-8
File: app.py:7
File: utils/helpers.py:2-7, 9-108
File: services/notification_service.py:1-48
File: requirements.txt:4-6
Description: `json, os, sys, time`, `format_date`, `calculate_percentage`, `process_task_data` etc. nunca usados; `NotificationService` nunca instanciado; marshmallow/requests/python-dotenv sem uso.
Impact: Ruído e superfície de manutenção.
Recommendation: P14 - remover o que nada referencia.

## Deprecated APIs
DEP-1 e DEP-2 acima.

================================
Total: 16 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
