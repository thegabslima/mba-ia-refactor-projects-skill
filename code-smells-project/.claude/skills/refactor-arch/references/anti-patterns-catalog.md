# Anti-pattern catalog (Phase 2)

Each entry: **ID - name - severity**, detection signals (language-agnostic first, then examples), impact, and the playbook pattern (`P#`) that fixes it.
Severity scale (MVC + SOLID):

- **CRITICAL** - security holes / secrets exposed / total loss of separation of concerns.
- **HIGH** - strong MVC/SOLID violations that block maintenance and testing.
- **MEDIUM** - duplication, standardization problems, moderate performance issues.
- **LOW** - readability, naming, magic numbers.

When one pattern can fit two severities, use the one written here. Report every occurrence (file + lines).

---

## CRITICAL

### AP-01 Hardcoded credentials / secrets - CRITICAL
- Signals: string literals assigned to names matching `secret|password|passwd|pass|pwd|token|api_?key|private_?key|smtp|dbUser|dbPass`; keys with live prefixes (`pk_live_`, `sk_`, `AKIA`); connection strings with user:password; secrets re-exposed in a response.
- Examples: `app.config["SECRET_KEY"] = "abc"`, `config = { dbPass: "..." }`, `self.email_password = 'senha123'`.
- Impact: anyone with repo access owns production; rotating requires a code change.
- Fix: P1.

### AP-02 SQL injection (string-built queries) - CRITICAL
- Signals: SQL keyword inside a string concatenated/interpolated with a variable: `"... WHERE id = " + str(id)`, `f"SELECT ... {x}"`, `` `SELECT ... ${x}` ``, `"%s" % x` inside `execute(`; `LIKE '%" + term + "%'`.
- Impact: auth bypass (`' OR '1'='1`), data theft/destruction.
- Fix: P2.

### AP-03 God class / God file - CRITICAL
- Signals: one file/class that mixes >= 3 of: routing, SQL/schema creation, business rules, validation, config, response formatting, external calls. Typical: a class with `initDb()` + `setupRoutes(app)` + checkout logic; a `models` file with 300 lines of SQL for 4 domains.
- Impact: untestable, every change touches everything.
- Fix: P3 (+ P4).

### AP-04 Unprotected dangerous endpoints - CRITICAL
- Signals: routes like `/admin/*`, `/reset`, `/debug`, `/query`, `/exec` without any auth check; endpoint that executes SQL/commands from the request body; endpoints that delete/wipe data.
- Impact: remote data wipe or arbitrary query by any client.
- Fix: P13.

### AP-05 Sensitive data exposure - CRITICAL
- Signals: password/hash fields serialized in responses (`to_dict` with `password`, `SELECT *` returned raw from a users table); secrets, DB paths or debug flags in `/health`; full card number/PAN, tokens or passwords written to logs; stack traces/`str(e)` returned to clients.
- Impact: credential and PCI data leakage.
- Fix: P6 (+ P8 for error leakage).

### AP-06 Debug mode / dev server exposed - CRITICAL
- Signals: `debug=True`, `DEBUG = True`, `app.run(host="0.0.0.0", debug=True)`, `NODE_ENV` hardcoded to development, hardcoded `"ambiente": "producao"` next to debug on.
- Impact: Werkzeug-style debuggers allow remote code execution.
- Fix: P1.

## HIGH

### AP-07 Business logic in controllers/routes - HIGH
- Signals: route handler > ~30 lines that validates, queries the DB (`Model.query`, `db.session`, `cursor.execute`) and computes rules (discounts, overdue, stock, payment decisions) in the same function; same rule repeated in several handlers.
- Impact: rules cannot be reused or unit-tested; MVC violated.
- Fix: P4.

### AP-08 Global mutable state / hidden singletons - HIGH
- Signals: module-level mutable variable reassigned from functions (`global x`, `let cache = {}` mutated in exports, module-level `db_connection = None`); exported counters (`totalRevenue`) never used consistently; shared in-memory lists in services (`self.notifications = []`).
- Impact: race conditions, order-dependent behavior, impossible to isolate tests.
- Fix: P5.

### AP-09 Weak or missing password hashing / fake auth - HIGH
- Signals: plaintext password stored/compared (`senha = '...'` in WHERE); MD5/SHA1 (`hashlib.md5`, `createHash('md5'|'sha1')`); home-made "crypto" (base64 loops); tokens such as `'fake-jwt-token-' + id`; default password fallback (`pwd || "123456"`).
- Impact: credential cracking, trivial account takeover.
- Fix: P6.

### AP-10 Tight coupling, no dependency injection - HIGH
- Signals: classes/functions that instantiate their own collaborators (`new Database()` in a constructor, `get_db()` called inside every function, `self.db = sqlite3.Database(':memory:')`); handlers reaching into module internals; routes registered inside a data class.
- Impact: cannot swap DB or mock in tests; circular imports.
- Fix: P5 (+ P3).

### AP-11 Callback hell / deeply nested async - HIGH (JS/any callback API)
- Signals: > 3 nested callbacks (`db.get(..., (e, r) => { db.run(..., function(){ ... }) })`), manual counters (`pending--`) to join async work, `res.send` repeated in nested branches.
- Impact: error paths forgotten, ordering bugs (non-deterministic response order), unreadable.
- Fix: P9.

## MEDIUM

### AP-12 N+1 queries - MEDIUM
- Signals: a query executed inside a loop over another query's results (`for row in rows: cursor.execute(...)`, `Model.query.get(t.user_id)` per task, `forEach` + `db.get`, `len(u.tasks)` lazy-loaded per user, `.count()` per category/user).
- Impact: latency grows linearly with data.
- Fix: P7.

### AP-13 Duplicated logic - MEDIUM
- Signals: same block (>= 5 lines) copied in 2+ places: row -> dict mapping, "overdue" nested ifs, validation lists (`['pending','in_progress',...]`), create/update validation twins, identical `try/except` wrappers on every handler.
- Impact: bug fixes must be applied N times; inconsistent behavior.
- Fix: P10.

### AP-14 Missing or inconsistent input validation - MEDIUM
- Signals: handler uses `request.json[...]`/`req.body.x` without checking presence/type; `int(request.args[...])` without try; comparisons on unvalidated types (`priority < 1` when it may be a string); PUT validating less than POST; no length/format checks.
- Impact: 500 errors on bad input, bad data stored.
- Fix: P12.

### AP-15 Swallowed / scattered error handling - MEDIUM
- Signals: bare `except:` / `except Exception: pass`; `try/except` repeated in every handler returning `str(e)`; callbacks ignoring `err`; no central error middleware/`errorhandler`.
- Impact: hidden failures, inconsistent error format, leaks internals.
- Fix: P8.

### AP-16 Missing referential integrity / orphaned data - MEDIUM
- Signals: delete of a parent row without deleting/cascading children (`DELETE FROM users` while enrollments/payments remain); tables without FKs; response admitting dirt ("ficaram sujos").
- Impact: reports show "Unknown", corrupted aggregates.
- Fix: P11.

### AP-17 Non-atomic multi-step writes - MEDIUM
- Signals: several INSERT/UPDATE statements for one business action without a transaction (check stock -> insert order -> decrement stock) or with no rollback on failure.
- Impact: partial orders, inconsistent stock.
- Fix: P11.

## LOW

### AP-18 Magic numbers / strings - LOW
- Signals: numeric thresholds and repeated status/role strings inline (`faturamento > 10000`, `* 0.1`, `'PAID'`, `['pending','done']`, `len(title) < 3`, port numbers).
- Fix: P14.

### AP-19 Poor naming - LOW
- Signals: 1-2 letter names outside tiny loops (`u, e, p, cid, cc`), request fields with cryptic aliases (`usr`, `eml`, `c_id`), generic names (`data`, `tmp`, `Manager`).
- Fix: P14 (rename internally; keep public payload keys unchanged).

### AP-20 print/console.log instead of a logger - LOW
- Signals: `print(`, `console.log(` for operational messages; fake notifications emulated with `print("ENVIANDO EMAIL...")`.
- Fix: P14.

### AP-21 Dead code and unused imports - LOW
- Signals: imports never referenced (`import json, os, sys`), functions with no callers (`process_task_data`, `generate_id`), unused exported variables, duplicated constants not used, services never instantiated.
- Fix: P14.

---

## Deprecated APIs (report as findings; severity as shown)

Detect by searching for the token; recommend the modern equivalent.

| Stack | Deprecated usage | Modern equivalent | Severity |
|-------|------------------|-------------------|----------|
| SQLAlchemy 1.4+/2.x | `Model.query.get(id)` / `Query.get` | `db.session.get(Model, id)` | MEDIUM |
| SQLAlchemy 2.x | `Model.query...` legacy Query API (in new code) | `db.session.execute(db.select(Model)...)` / `db.session.scalars(...)` | LOW |
| Python 3.12+ | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)` | MEDIUM |
| Flask 2.3+ | `@app.before_first_request`, `flask.json.JSONEncoder`, `app.json_encoder` | app-factory init code, `app.json` provider | MEDIUM |
| Flask | `app.config["DEBUG"]=True` / `app.run(debug=True)` for prod | `FLASK_DEBUG` env | CRITICAL (AP-06) |
| Python | `hashlib.md5/sha1` for passwords | `werkzeug.security.generate_password_hash`, `bcrypt`, `argon2` | HIGH (AP-09) |
| Python | `%`-formatting / `+` in SQL | parameterized queries | CRITICAL (AP-02) |
| Node.js | `new Buffer(x)` / `Buffer(x)` | `Buffer.from(x)` / `Buffer.alloc(n)` | MEDIUM |
| Node.js | `crypto.createCipher/createDecipher`, `crypto.createHash('md5')` for secrets | `createCipheriv`, `crypto.scrypt` / `bcrypt` | HIGH |
| Node.js | `url.parse()`, `fs.exists()`, `util.isArray` etc. | `new URL()`, `fs.access`/`existsSync`, `Array.isArray` | LOW |
| Node.js | `request` package, `body-parser` (Express >= 4.16) | `fetch`/`axios`, `express.json()` | LOW |
| Node.js | `var`, callback style fs/db APIs | `const/let`, promises/async-await | LOW |
| Express 4 | `res.send(status)` ordering, `app.del()`, `req.param()` | `res.sendStatus`, `app.delete()`, `req.params/query/body` | LOW |
| Java | `new Date()`, `SimpleDateFormat` (shared), `@Autowired` field injection | `java.time`, constructor injection | LOW |
| PHP | `mysql_*` functions | PDO / mysqli prepared statements | CRITICAL |

Use IDs `DEP-1`, `DEP-2`, ... for deprecated-API findings (one per distinct API, all locations listed).

If the project uses none, state "No deprecated APIs detected (checked: <list of tokens searched>)" in the report.
