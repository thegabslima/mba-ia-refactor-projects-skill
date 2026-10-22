# Target architecture: MVC (Phase 3)

## Layers and responsibilities

| Layer | Owns | Must NOT |
|-------|------|----------|
| **Config** | Reads environment (`process.env`, `os.environ`), defaults, constants (statuses, limits, thresholds). Single source of truth. | Contain secrets in code; import other layers. |
| **Models** | Data and persistence: schema, queries (always parameterized), entities, domain rules that depend only on data (totals, overdue, discount tiers), password hashing helpers. Return plain objects/dicts or entities. | Know about HTTP (`request`, `res`, status codes); print/format responses. |
| **Views / Routes** | URL + HTTP verb -> controller function mapping, middleware wiring, response serialization (the JSON contract). | Contain business rules or queries. |
| **Controllers** | Orchestrate one use case: read/validate request input, call models, decide HTTP status, build the response. Thin. | Build SQL; hold global state; know connection details. |
| **Middlewares / error handling** | Central error handler, 404, auth/guard (admin token), request logging. | Contain business rules. |
| **Entry point (composition root)** | Create the app, load config, init DB, build and wire dependencies, register routes and error handler, start the server. | Hold routes or logic. |

Optional `services/` for logic that spans several models or external systems (payment gateway, email). Controllers call services; services call models; models never call services.

## Dependency direction

```
entry point -> views(routes) -> controllers -> models -> database/config
                               controllers -> services -> models
middlewares -> config
```

Allowed: a layer imports only layers to its right. Forbidden: models importing controllers/routes, routes importing models directly, any layer reading `process.env`/`os.environ` except config.
Resources (DB connection, gateway client) are created in the composition root or a factory and **injected** (constructor/argument/app context), never as module-level mutable globals.

## Layouts

Choose by stack; keep the original run command (`python app.py`, `npm start`, ...) working by keeping the entry-point file name/location.

**Python / Flask (raw DB or SQLAlchemy)**
```
app.py                    # entry point: create_app() + run (composition root)
config/settings.py        # env-driven Settings, constants
models/                   # database.py (connection/schema/seed) + one file per entity
views/routes.py           # Blueprint(s) mapping URLs -> controllers   (existing "routes/" folder may be kept as the views layer)
controllers/              # one module per domain
middlewares/error_handler.py
services/                 # optional (notifications, auth tokens)
requirements.txt, .env.example
```

**Node.js / Express**
```
src/app.js                # entry point (npm start): builds app, listens
src/config/settings.js
src/models/               # database.js (connection + schema/seed) + one file per entity
src/views/routes.js       # express.Router wiring
src/controllers/
src/services/             # optional (payment gateway, password hasher)
src/middlewares/errorHandler.js
.env.example
```

**Java / Spring**: `config/`, `model|entity/` + `repository/`, `controller/` (the "view" is the `@RestController` mapping + DTOs), `service/`, `@ControllerAdvice` for errors, constructor injection.
**Go**: `internal/config`, `internal/models`, `internal/handlers` (controllers), `internal/routes`, `cmd/server/main.go` as composition root.
**PHP / Laravel**: already MVC-shaped - keep `app/Models`, `routes/`, `app/Http/Controllers`, move rules out of controllers into models/services, config via `config/*.php` + `.env`.

## Adapting to the starting point

- **Monolith / God file**: create every layer; move code by responsibility (P3), then clean each piece.
- **Flat, partially split**: promote existing files into the layers (e.g. `models.py` full of SQL -> `models/<entity>.py`; `controllers.py` -> `controllers/<domain>.py`; routes declared in `app.py` -> `views/routes.py`).
- **Already layered (models/routes/services/utils)**: keep existing folder names. Add what is missing (config, controllers, error handler); thin the route files into pure routing; move logic out of routes into controllers/models; delete dead helpers. Do not rewrite what is already right.

## Definition of done for the structure

- [ ] No secret or environment-specific value in code; `.env.example` documents variables.
- [ ] Every DB access lives in models; all queries parameterized.
- [ ] Routes only map URLs; controllers contain no SQL.
- [ ] One central error handler; consistent error JSON.
- [ ] Single, tiny entry point that wires everything.
- [ ] Public API contract preserved except documented security fixes.
