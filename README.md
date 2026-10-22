# refactor-arch - skill de refatoração para MVC

Skill do Claude Code que analisa um backend, gera um relatório de auditoria e (após confirmação) refatora para MVC, validando que a app continua subindo. Testada em 3 projetos: Flask (2) e Express (1).

## 1. Análise Manual

Fiz uma analize manual do código antes de criar a skill; abaixo a lista resumida. Os relatórios completos (com linha exata) estão em `reports/`.

### Projeto 1 - code-smells-project (Flask, e-commerce)

| Sev. | Problema | Onde | Por que importa |
|------|----------|------|-----------------|
| CRITICAL | SQL Injection por concatenação | `models.py` (todas as queries) | `' OR '1'='1` no `/login` retorna 200 |
| CRITICAL | SECRET_KEY hardcoded e exposta no `/health` | `app.py:7`, `controllers.py:289` | segredo vaza para qualquer cliente |
| CRITICAL | `/admin/query` e `/admin/reset-db` sem auth | `app.py:47-78` | SQL arbitrário e wipe do banco |
| HIGH | Senhas em texto puro | `database.py:75-83` | vazamento expõe todas as contas |
| MEDIUM | N+1 em pedidos | `models.py:171-233` | 1 query por pedido e por item |
| MEDIUM | Validação duplicada e inconsistente (POST x PUT) | `controllers.py:30-90` | comportamento diferente por rota |
| LOW | Magic numbers no desconto | `models.py:257-262` | regra de negócio escondida |
| LOW | `print` no lugar de logger | `controllers.py` | sem níveis de log |

### Projeto 2 - ecommerce-api-legacy (Express, LMS)

| Sev. | Problema | Onde | Por que importa |
|------|----------|------|-----------------|
| CRITICAL | Chave `pk_live` e senhas no código | `utils.js:1-7` | segredos no repositório |
| CRITICAL | Cartão completo e chave do gateway no log | `AppManager.js:45` | vazamento de dado de pagamento |
| CRITICAL | God class (schema + rotas + checkout + relatório) | `AppManager.js:4-139` | nada é testável isolado |
| HIGH | `badCrypto` caseiro e senha padrão `123456` | `utils.js:17-23` | senha trivial de quebrar |
| HIGH | Callback hell com contadores manuais | `AppManager.js:37-128` | erros esquecidos, ordem aleatória |
| MEDIUM | N+1 no relatório financeiro | `AppManager.js:83-126` | queries crescem com curso x matrícula |
| MEDIUM | DELETE de usuário deixa matrículas órfãs | `AppManager.js:131-137` | relatório mostra "Unknown" |
| LOW | Nomes `u, e, p, cid, cc` | `AppManager.js:29-33` | leitura difícil |
| LOW | Estado global não usado (`totalRevenue`) | `utils.js:10,25` | código morto |

### Projeto 3 - task-manager-api (Flask + SQLAlchemy)

| Sev. | Problema | Onde | Por que importa |
|------|----------|------|-----------------|
| CRITICAL | Hash da senha devolvido pela API | `models/user.py:21` | vaza em 4 endpoints |
| CRITICAL | `debug=True` em `0.0.0.0` + secrets no código | `app.py:13,34` | execução remota de código |
| HIGH | MD5 e token falso (`fake-jwt-token-N`) | `models/user.py:29`, `user_routes.py:210` | qualquer um forja login |
| HIGH | Regras e queries dentro das rotas, sem controllers | `routes/*.py` | camadas misturadas |
| MEDIUM | Regra de "atrasada" copiada em 7 lugares | `task_routes.py`, `report_routes.py` | existe `is_overdue()` sem uso |
| MEDIUM | N+1 (`User.query.get` por task) | `task_routes.py:41-57` | lento com volume |
| MEDIUM | `except:` genérico | `task_routes.py:62` e outros | falhas engolidas |
| LOW | Imports e helpers mortos | `utils/helpers.py`, `app.py:7` | ruído |
| LOW | Constantes definidas e nunca usadas | `utils/helpers.py:110-116` | regras duplicadas inline |

## 2. Construção da Skill

**Estrutura** (`.claude/skills/refactor-arch/`):

```
SKILL.md                         # 3 fases + regras (é o "prompt")
references/
  project-analysis.md            # detectar linguagem/framework/banco/arquitetura
  anti-patterns-catalog.md       # 21 anti-patterns + tabela de APIs deprecated
  report-template.md             # formato do relatório da Fase 2
  mvc-architecture.md            # camadas, regras de dependência, layouts por stack
  refactoring-playbook.md        # 15 padrões antes/depois (Python e JS)
```

**Decisões de design**
- O SKILL.md só descreve o método; todo conhecimento de tecnologia fica nas referências, lidas no início de cada fase.
- Fases 1 e 2 são somente leitura. A Fase 2 termina com `[y/n]` e nada é alterado antes do "y".
- Fase 3: salva o relatório, captura baseline dos endpoints, refatora, valida (boot + endpoints + busca dos sinais do catálogo) e lista todo desvio do contrato original.
- O catálogo tem 21 itens (6 CRITICAL, 5 HIGH, 6 MEDIUM, 4 LOW) mais APIs deprecated (`Query.get`, `datetime.utcnow`, `new Buffer`, `mysql_*`...). Escolhi os que apareceram na análise manual e os mais comuns em legados (segurança, God class, N+1, callback hell).
- Cada anti-pattern tem sinais de detecção concretos ("query dentro de loop for", regex de segredos) e aponta para um padrão do playbook (P1-P15).

**Agnóstica de tecnologia**: sinais descritos por conceito primeiro (SQL concatenado, estado global, handler grande), com exemplos em Python/JS/Java/Go/PHP. As heurísticas de stack e os layouts MVC são tabelas por linguagem, e a Fase 3 se adapta ao nível de organização (monolito, parcial, em camadas).

**Desafios**
- Projeto 3 já tinha pastas: a skill precisou *adaptar* (manter `routes/` como views, criar `controllers/`) em vez de recriar tudo. Isso virou regra em `mvc-architecture.md`.
- "App funciona" x correções de segurança: algumas correções mudam respostas (hash sumiu do JSON, `/admin/*` pede token). Criei a regra "preservar o contrato, excessão de segurança, e listar os desvios", porem sem exagerar nas mudanças.
- Verifiquei afirmações do relatório contra o código: corrigi uma (SQLAlchemy já zera `category_id` ao apagar categoria).

## 3. Resultados

Nota: executei as fases seguindo o SKILL.md dentro de uma sessão do Claude Code, não com três chamadas `claude "/refactor-arch"` separadas. A confirmação da Fase 2 foi dada pelo usuario na conversa.

### Findings por severidade

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---------|---------:|-----:|-------:|----:|------:|-----------|
| 1 code-smells-project | 6 | 4 | 6 | 4 | 20 | [audit-project-1](reports/audit-project-1.md) |
| 2 ecommerce-api-legacy | 4 | 5 | 5 | 4 | 18 | [audit-project-2](reports/audit-project-2.md) |
| 3 task-manager-api | 3 | 2 | 7 | 4 | 16 | [audit-project-3](reports/audit-project-3.md) |

### Antes / depois

| Projeto | Antes | Depois |
|---------|-------|--------|
| 1 | `app.py`, `controllers.py`, `models.py`, `database.py` | `app.py` (composição), `config/`, `models/` (database + 1 por entidade), `controllers/` (6), `views/routes.py`, `middlewares/`, `services/` |
| 2 | `src/app.js`, `AppManager.js`, `utils.js` | `src/app.js` (composição), `config/`, `models/` (6), `controllers/` (3), `views/routes.js`, `middlewares/`, `services/` |
| 3 | `models/ routes/ services/ utils/` com lógica nas rotas | + `config/`, `controllers/` (4), `middlewares/`; `routes/` só mapeia URLs; `services/` ganhou `report_service` e `auth_service` |

### Checklist de validação (os 3 projetos)

- [x] Fase 1: linguagem, framework, domínio e nº de arquivos corretos
- [x] Fase 2: segue o template, arquivo:linha, ordenado CRITICAL->LOW, >= 5 findings, deprecated checado (projeto 3 tem 2), pausa com `[y/n]`
- [x] Fase 3: estrutura MVC, config em módulo (sem segredo no código), models, routes/views, controllers, error handler central, entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem (ver logs)

Logs completos (boot, cada endpoint e diff contra a baseline): [projeto 1](reports/validation-project-1.log), [projeto 2](reports/validation-project-2.log), [projeto 3](reports/validation-project-3.log).

### Desvios do contrato (todos de segurança ou robustez)

- P1: `/health` não expõe mais `secret_key`/`db_path`/`debug`; `/usuarios` sem `senha`; login com SQLi agora dá 401; `/admin/*` exige `X-Admin-Token` (403 sem `ADMIN_TOKEN`) e `/admin/query` aceita só um SELECT; e-mail único (409); erros trazem também `sucesso: false`.
- P2: `/api/admin/financial-report` e `DELETE /api/users/:id` exigem `X-Admin-Token`; excluir usuário apaga matrículas e pagamentos; pagamento recusado não cria mais usuário.
- P3: `password` saiu de todas as respostas; token do login agora é assinado; entradas inválidas dão 400 em vez de 500.
- P3: bodies de 11 GETs idênticos ao original (comparados com timestamps normalizados).

### Observações

- No projeto 3 (já em camadas) a skill achou o que era de *conteúdo* (lógica nas rotas, duplicação, deprecated), não só de estrutura. No projeto 2 (monolito) a mudança foi quase total.
- `NotificationService` (projeto 3) continua sem uso: só tirei as credenciais do código.
- O relatório do projeto 3 teve um erro meu (categoria órfã) que só apareceu ao testar; por isso a Fase 3 pede revalidação.

## 4. Como Executar

**Pré-requisitos**: Claude Code instalado e logado; Python 3.10+ (necessario nos projetos 1 e 3); Node 18+ (projeto 2).

```bash
cd code-smells-project      # ou ecommerce-api-legacy / task-manager-api
claude "/refactor-arch"
```

A skill roda a Fase 1, a Fase 2 e para em `Proceed with refactoring (Phase 3)? [y/n]`. Responda `y` para refatorar.

**Rodar as apps refatoradas**

```bash
# projeto 1
cd code-smells-project && pip install -r requirements.txt && ADMIN_TOKEN=segredo python app.py   # :5000
# projeto 2
cd ecommerce-api-legacy && npm install && ADMIN_TOKEN=segredo npm start                           # :3000
# projeto 3
cd task-manager-api && pip install -r requirements.txt && python seed.py && python app.py          # :5000
```

**Validar**: `curl localhost:5000/health` (projetos 1 e 3), `api.http` no projeto 2, e comparar com `reports/validation-project-*.log`. Variáveis de ambiente: veja `.env.example` em cada projeto.
