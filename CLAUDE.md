# CLAUDE.md — Bayit Dashboard Agent Rules

## Repository Rules (ENFORCED — violations will be rejected)

### Branch Policy
- **NEVER commit directly to `main`**. All work MUST go through a Pull Request.
- Every agent MUST work in an isolated git worktree with its own branch.
- Branch naming: `{prefix}/{short-description}`
- Allowed prefixes: `frontend/`, `backend/`, `data-eng/`, `devops/`, `devsecops/`, `ux/`, `testing/`, `docs/`, `hotfix/`

### Commit Standards
- All commits follow Conventional Commits: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `ci`, `chore`, `perf`, `security`
- Scopes: `frontend`, `backend`, `pipeline`, `db`, `infra`, `ci`, `docs`
- Commits MUST include Co-Authored-By trailer
- No secrets, credentials, API keys, or .env files may be committed

### Python Toolchain
- **Package manager**: `uv` — use `uv sync` to install, `uv add` to add deps, `uv run` to execute
- **Linter/formatter**: `ruff` — configured in `pyproject.toml`
- **Type checker**: `ty` — configured in `pyproject.toml`
- **Never use pip, mypy, or virtualenv directly** — always go through `uv`

### Code Quality Gates (must pass before PR merge)
- Python: `uv run ruff check` and `uv run ruff format --check` must pass
- Python: `uv run ty check` on all backend code (type annotations required)
- JavaScript/TypeScript: `eslint` must pass
- All new code must have tests (`uv run pytest` for Python, vitest for frontend)
- No `# type: ignore` without an explanatory comment
- No `eslint-disable` without an explanatory comment
- No TODO/FIXME without a linked GitHub issue number

### PR Review Policy (ENFORCED by GitHub branch protection)
- **Gemini Code Assist** automatically reviews every PR
- All CI checks must pass before merge
- All review conversations must be resolved before merge
- Every review comment must receive a one-line reply describing what was done to address it, or why it was dismissed
- No PR may be merged with unresolved review threads

### Security
- All SQL queries MUST use parameterized queries — NO string interpolation
- All user input MUST be validated with Pydantic models (backend) or zod (frontend)
- All API endpoints MUST validate bbox within Richmond bounds: lng [-123.30, -123.00], lat [49.10, 49.22]
- CORS must be configured explicitly — never `allow_origins=["*"]` in production
- Dependencies managed via `uv` and pinned in `uv.lock`

### Data Integrity
- All geometry MUST be EPSG:4326 (WGS84) — verify with ST_SRID() checks
- PID format validated: 9 digits, XXX-XXX-XXX
- Lot area in square meters (m²) — never square feet
- All ArcGIS REST queries MUST include `outSR=4326`

### File Organization
```
bayit-dashboard/
├── backend/          # FastAPI application
│   ├── routers/      # API endpoint modules
│   ├── sync/         # Data ingestion scripts
│   ├── models.py     # Pydantic models
│   ├── db.py         # Database connection
│   └── tests/        # pytest tests
├── frontend/         # React + Vite application
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── utils/
│   └── tests/        # vitest tests
├── sql/              # Database migrations and schema
├── scripts/          # Utility scripts
├── .github/          # CI/CD workflows, PR templates
└── docs/             # Documentation
```

### Agent Workflow (MANDATORY)
1. Read CLAUDE.md and PROJECT.md before starting any work
2. Create a branch following the naming convention
3. Work ONLY in your designated directory (frontend agents touch only frontend/, etc.)
4. Write tests for all new functionality
5. Run quality gates locally before committing
6. Create a PR with the template — never push to main
7. Wait for CI to pass and review approval before merge

### PR Requirements
- Title: `type(scope): description` (same as commits)
- Body must use the PR template
- Must reference Phase and Task from PROJECT.md
- Must include test evidence (screenshots for UI, curl for API, query results for data)

### Directory Scopes per Agent Type
| Agent Type | Prefix | Scope |
|---|---|---|
| Frontend Developer | `frontend/` | `frontend/` |
| Backend Architect | `backend/` | `backend/`, `sql/` |
| Data Pipeline Engineer | `data-eng/` | `backend/sync/`, `scripts/`, `sql/` |
| DevOps Automator | `devops/`, `devsecops/` | `.github/`, Docker files |
| UX Architect | `ux/` | `frontend/src/components/`, `docs/` |
| Testing agents | `testing/` | `backend/tests/`, `frontend/tests/` |
| Documentation | `docs/` | `docs/`, `*.md` |
| Hotfix | `hotfix/` | Any (requires justification) |
