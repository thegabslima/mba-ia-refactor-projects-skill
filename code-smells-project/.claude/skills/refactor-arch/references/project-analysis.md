# Project analysis heuristics (Phase 1)

Goal: describe the project from evidence in the files. Cite the file that proves each claim.

## 1. Which files count

Include source files (`.py .js .ts .java .kt .go .rb .php .cs .rs`) and templates. Ignore:
`node_modules/ vendor/ .venv/ venv/ __pycache__/ dist/ build/ target/ .git/ .idea/ *.min.js *.lock`, DB files, and generated code. Count files and lines of what remains ("Source files: N files analyzed").

## 2. Language and framework

Look at manifest files first, then confirm with imports.

| Manifest / marker | Language | Confirm framework by |
|-------------------|----------|----------------------|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python | `flask` / `Flask(__name__)`; `django` + `manage.py`; `fastapi` + `FastAPI()` |
| `package.json` (`dependencies`) | JavaScript / TypeScript (`tsconfig.json` -> TS) | `express` + `express()`; `fastify`; `@nestjs/core`; `koa` |
| `pom.xml`, `build.gradle` | Java / Kotlin | `spring-boot-starter-web`, `@RestController`; Micronaut; Quarkus |
| `go.mod` | Go | `gin-gonic/gin`, `labstack/echo`, `net/http` mux |
| `composer.json` | PHP | `laravel/framework`, `symfony/*`, `slim/slim` |
| `Gemfile` | Ruby | `rails`, `sinatra` |
| `*.csproj` | C# | `Microsoft.AspNetCore` |

Version: read the pinned version in the manifest (`flask==3.1.1`, `"express": "^4.18.2"`). If only a range exists, report the range.
Dependencies: list the runtime ones that shape the design (web framework, ORM, CORS, DB driver, auth libs). Skip dev-only tools.

## 3. Entry point and how it runs

- `package.json` -> `scripts.start` / `main`; Python -> file with `app.run(` / `if __name__ == "__main__"` / `FLASK_APP`; Java -> class with `main` / `@SpringBootApplication`; Go -> `package main`.
- Note the default port and run command (README, `app.run(port=`, `app.listen(`). The refactor must keep this command working.

## 4. Database

| Signal | Meaning |
|--------|---------|
| `sqlite3`, `better-sqlite3`, `sqlite3.connect`, `new sqlite3.Database(` | SQLite (note `:memory:` vs file) |
| `psycopg2`, `pg`, `jdbc:postgresql` | PostgreSQL |
| `mysql`, `mysql2`, `PyMySQL` | MySQL |
| `pymongo`, `mongoose` | MongoDB |
| `flask_sqlalchemy`, `SQLAlchemy`, `db.Model`, `@Entity`, `Sequelize`, `Prisma`, `TypeORM` | ORM (name it) |

List tables/collections from `CREATE TABLE` statements, ORM model classes (`__tablename__`, `@Entity`, `define(`) or schema files.
Also note: raw SQL vs ORM, where the connection is created, where schema/seed runs.

## 5. Domain

Infer from table/model names, route paths and function names (e.g. `produtos, pedidos, itens_pedido` -> e-commerce; `courses, enrollments, payments` -> LMS with checkout; `tasks, categories, users` -> task manager). One short sentence plus the main entities.

## 6. Current architecture level

Map the files to layers (Model = data/persistence/domain rules, View/Routes = URL -> handler mapping/serialization, Controller = request orchestration). Then classify:

| Level | Evidence |
|-------|----------|
| **Monolithic / God file** | One or two files hold routing + SQL + business rules + config (e.g. a class that creates tables, defines routes and processes payments) |
| **Flat, partially split** | Several files but layers are mixed: routes call the DB directly, "models" file is a bag of SQL functions, controllers contain SQL |
| **Layered, with violations** | Folders like `models/ routes/ services/ utils/` exist, but business logic sits in route handlers, models/services are bypassed, helpers duplicated or dead |
| **Clean MVC** | Layers respect the dependency rules of `mvc-architecture.md` |

Write one justification line, e.g. "Monolithic - everything in 4 files, no layer separation".
Also record: global state (module-level mutable variables/connections), where config lives, whether a central error handler exists, whether tests exist.

## 7. Useful searches (tool-agnostic; use the Grep/Glob tools, not shell-specific commands)

- Routes: `@app.route|add_url_rule|Blueprint|app\.(get|post|put|delete)|router\.|@(Get|Post)Mapping`
- SQL: `SELECT |INSERT |UPDATE |DELETE |CREATE TABLE`
- Config/secrets: `SECRET|PASSWORD|PASS|KEY|TOKEN|jdbc:|mongodb://`
- Env usage: `os.environ|os.getenv|process.env|System.getenv`
