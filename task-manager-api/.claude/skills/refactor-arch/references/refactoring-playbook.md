# Refactoring playbook (Phase 3)

Each pattern: when to apply, **before**, **after**. Examples are Python and JavaScript; apply the same idea in any other language. Keep the public contract (URLs, verbs, status codes, JSON shape) unless the pattern says otherwise.

---

## P1 - Extract config and secrets to environment (AP-01, AP-06)
Create a config module that is the only reader of the environment. Provide `.env.example`; never commit real values. Secrets without a default must either come from env or be generated at boot (`secrets.token_hex`) - never a literal.

```python
# before
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.run(host="0.0.0.0", port=5000, debug=True)
# after  config/settings.py
import os, secrets
class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 5000))
```
```js
// before: const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_..." }
// after   src/config/settings.js
module.exports = {
  port: Number(process.env.PORT) || 3000,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
};
```

## P2 - Parameterize every query (AP-02)
Placeholders for values; whitelist for identifiers (column/order names). For `LIKE`, pass the wildcard inside the parameter.

```python
# before
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
# after
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", (f"%{termo}%",))
```
```js
db.get("SELECT id FROM users WHERE email = ?", [email], cb);   // already safe - keep
```

## P3 - Split a God file/class into MVC layers (AP-03, AP-10)
1. List responsibilities in the file (schema, queries, routes, rules, formatting).
2. Move each to its layer (`mvc-architecture.md`), one entity/domain per file.
3. Replace the class that did everything with a composition root that wires the pieces.

```js
// before: class AppManager { initDb(){...} setupRoutes(app){ app.post('/api/checkout', ...200 lines...) } }
// after
// models/database.js        -> connection + schema + seed
// models/userModel.js ...   -> queries per entity
// controllers/checkoutController.js -> orchestration
// views/routes.js           -> router.post('/api/checkout', checkout.handle)
// app.js                    -> wiring only
```

## P4 - Thin controllers: move rules into models/services (AP-07)
Controller = parse input, call, map to HTTP. Rules that depend only on data go to the model.

```python
# before (inside the route): if faturamento > 10000: desconto = faturamento * 0.1 ...
# after  models/relatorio_model.py
def calcular_desconto(faturamento):
    for limite, taxa in DESCONTO_FAIXAS:      # constants in config
        if faturamento > limite:
            return faturamento * taxa
    return 0
# controller: dados = relatorio_model.vendas(); return jsonify({"dados": dados, "sucesso": True})
```

## P5 - Replace global mutable state with scoped/injected resources (AP-08, AP-10)
```python
# before: db_connection = None ; def get_db(): global db_connection ...
# after (Flask): connection per request, closed on teardown
from flask import g
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(Settings.DB_PATH); g.db.row_factory = sqlite3.Row
    return g.db
def close_db(exc=None):
    db = g.pop("db", None)
    if db: db.close()
# app factory: app.teardown_appcontext(close_db)
```
```js
// before: module-level `let globalCache = {}; let totalRevenue = 0;` mutated by helpers
// after: delete unused state; if a cache is really needed, create it in app.js and pass it in
class Database { constructor(path) { this.db = new sqlite3.Database(path); } }   // injected into models
```

## P6 - Hash passwords, never expose secrets (AP-05, AP-09)
Use the framework/stdlib hasher; compare with the library's verify function; strip `password`/hash/secret keys from serializers; stop logging card numbers/tokens (mask to last 4).

```python
# before: self.password = hashlib.md5(pwd.encode()).hexdigest(); to_dict() returns 'password'
# after
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd): self.password = generate_password_hash(pwd)
def check_password(self, pwd): return check_password_hash(self.password, pwd)
# to_dict(): omit 'password'
```
```js
// before: badCrypto = base64 loop; console.log(`Processando cartão ${cc} na chave ${key}`)
const crypto = require('crypto');
function hashPassword(pwd) {
  const salt = crypto.randomBytes(16).toString('hex');
  return `${salt}:${crypto.scryptSync(pwd, salt, 64).toString('hex')}`;
}
logger.info(`Processando cartão final ${card.slice(-4)}`);
```
Fake tokens (`'fake-jwt-token-' + id`) -> signed tokens (`itsdangerous.URLSafeTimedSerializer(SECRET_KEY)`, `jsonwebtoken`).

## P7 - Remove N+1 with JOIN / eager loading (AP-12)
```python
# before: for pedido in pedidos: cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id=" ...) ; per item: SELECT nome FROM produtos
# after: one query, group in memory
rows = db.execute("""SELECT i.pedido_id, i.produto_id, p.nome AS produto_nome, i.quantidade, i.preco_unitario
                     FROM itens_pedido i LEFT JOIN produtos p ON p.id = i.produto_id""").fetchall()
```
```python
# SQLAlchemy: Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
# counts: db.session.query(Task.user_id, func.count()).group_by(Task.user_id)
```

## P8 - Centralized error handling (AP-15)
Controllers raise typed errors (or return them); one handler converts to JSON and logs; unknown errors give a generic 500 (no `str(e)` to clients).

```python
class AppError(Exception):
    def __init__(self, message, status=400): self.message, self.status = message, status
def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _app(e): return jsonify({"erro": e.message}), e.status
    @app.errorhandler(Exception)
    def _any(e): app.logger.exception(e); return jsonify({"erro": "Erro interno"}), 500
```
```js
app.use((err, req, res, next) => {            // last middleware
  logger.error(err);
  res.status(err.status || 500).send(err.status ? err.message : 'Erro interno');
});
// async controllers: wrap with (fn) => (req,res,next) => fn(req,res).catch(next)
```
Keep the original error body keys (`erro` / `error` / plain text) per project.

## P9 - Callbacks to async/await (AP-11)
Promisify the driver once in the model layer, then write linear code.

```js
// before: db.get(q, [id], (err, course) => { db.get(..., (err, user) => { db.run(..., function(err){ ... }) }) })
const run = (sql, p=[]) => new Promise((ok, ko) => db.run(sql, p, function (e) { e ? ko(e) : ok(this); }));
const get = (sql, p=[]) => new Promise((ok, ko) => db.get(sql, p, (e, r) => e ? ko(e) : ok(r)));
// after
const course = await courseModel.findActive(courseId);
const user = (await userModel.findByEmail(email)) ?? await userModel.create(...);
const { lastID } = await enrollmentModel.create(user.id, course.id);
```
Join parallel reads with `Promise.all` or, better, one JOIN query (P7), not manual counters.

## P10 - Deduplicate repeated logic (AP-13)
One function/method per rule; callers use it. Row mapping: `dict(row)` / `to_dict()`.

```python
# before: the 8-line overdue if/else copied in 5 handlers
# after  models/task.py
def is_overdue(self):
    return bool(self.due_date and self.due_date < utcnow() and self.status not in ("done", "cancelled"))
def to_dict(self, include_overdue=False): ...
```
Create/update validation twins -> one `validate_<entity>(data, partial=False)`.

## P11 - Integrity and atomic writes (AP-16, AP-17)
```python
# multi-step order: one transaction
try:
    db.execute("BEGIN")
    ... insert pedido, itens, update estoque ...
    db.commit()
except Exception:
    db.rollback(); raise
```
```js
// delete parent -> delete children first (same unit of work)
await run("DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)", [id]);
await run("DELETE FROM enrollments WHERE user_id = ?", [id]);
await run("DELETE FROM users WHERE id = ?", [id]);
```
ORM: `relationship(..., cascade="all, delete-orphan")` or FK `ON DELETE CASCADE`.

## P12 - Validate input at the controller boundary (AP-14)
Check presence, type, range; return 400 with the project's error shape instead of crashing with 500.

```python
def parse_produto(d):
    if not isinstance(d, dict): raise AppError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in d: raise AppError(f"{campo.capitalize()} é obrigatório")
    if not isinstance(d["preco"], (int, float)) or d["preco"] < 0: raise AppError("Preço não pode ser negativo")
    ...
```
One validator shared by create and update.

## P13 - Protect or remove dangerous endpoints (AP-04)
Remove anything that executes arbitrary SQL/commands unless it is needed; if the route must stay, require an admin credential from config, default to disabled, and restrict it (read-only, single statement).

```python
def require_admin(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not Settings.ADMIN_TOKEN or request.headers.get("X-Admin-Token") != Settings.ADMIN_TOKEN:
            raise AppError("Acesso negado", 403)
        return f(*a, **kw)
    return wrapper
```
Use `hmac.compare_digest` for the comparison.

## P14 - Constants, names, logging, dead code (AP-18..AP-21)
- Magic values -> named constants in config (`DESCONTO_FAIXAS`, `ORDER_STATUSES`, `PAYMENT_PAID = "PAID"`).
- Rename internals (`u, e, p, cid, cc` -> `name, email, password, courseId, cardNumber`); keep external request/response keys.
- `print`/`console.log` -> `logging` / a small logger; simulated notifications become a log line or a service stub.
- Delete unused imports, functions, exports and services nobody calls (verify with a search first).

## P15 - Replace deprecated APIs (catalog table)
```python
Task.query.get(id)            ->  db.session.get(Task, id)
datetime.utcnow()             ->  datetime.now(timezone.utc)   # use one helper: utcnow() returning naive UTC if DB columns are naive
new Buffer(x)                 ->  Buffer.from(x)
```
Apply mechanically, then run the app: behavior (naive vs aware datetimes, `None` for missing ids) must stay the same.
