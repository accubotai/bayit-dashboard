# Contributing — Agent Workflow Guide

This document defines the **mandatory** workflow for all agents (human or AI) contributing to the Bayit Dashboard project. These rules are programmatically enforced via CI/CD and pre-commit hooks.

## The Golden Rule

**No agent may commit directly to `main`.** Every change goes through a Pull Request.

## Workflow: Step by Step

### 1. Start in an Isolated Worktree

Every agent works in a git worktree — an isolated copy of the repository on its own branch.

```bash
# Create a worktree for your task
git worktree add ../bayit-{agent-type}-{task} -b {agent-type}/{task-description}

# Examples:
git worktree add ../bayit-frontend-map -b frontend/map-component
git worktree add ../bayit-backend-parcels -b backend/parcels-api
git worktree add ../bayit-data-ingest -b data-eng/ingest-geohub
```

### 2. Branch Naming Convention (ENFORCED)

Format: `{prefix}/{short-description}`

| Agent Type | Branch Prefix | Directory Scope |
|---|---|---|
| Frontend Developer | `frontend/` | `frontend/` only |
| Backend Architect | `backend/` | `backend/`, `sql/` |
| Data Pipeline Engineer | `data-eng/` | `backend/sync/`, `scripts/`, `sql/` |
| DevOps Automator | `devops/` or `devsecops/` | `.github/`, `docker-compose*`, `Dockerfile*` |
| UX Architect | `ux/` | `frontend/src/components/`, `docs/` |
| Testing agents | `testing/` | `backend/tests/`, `frontend/tests/` |
| Documentation | `docs/` | `docs/`, `*.md` |
| Hotfix (emergency) | `hotfix/` | Any (requires justification) |

### 3. Directory Scope Enforcement

Each agent type has a designated directory scope. Agents SHOULD NOT modify files outside their scope unless absolutely necessary and documented in the PR.

### 4. Commit Standards (ENFORCED by CI)

Every commit must follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `refactor`, `test`, `docs`, `ci`, `chore`, `perf`, `security`
**Scopes:** `frontend`, `backend`, `pipeline`, `db`, `infra`, `ci`, `docs`

**Examples:**
```
feat(backend): add /api/parcels endpoint with spatial filtering
fix(pipeline): handle ArcGIS pagination offset overflow
test(frontend): add FilterPanel component tests
ci(infra): add PostGIS service to test workflow
```

### 5. Environment Setup (uv)

This project uses `uv` as its Python package manager, `ruff` for linting/formatting, and `ty` for type checking.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (from pyproject.toml)
uv sync --dev

# Run pre-commit hooks (one-time setup)
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

### 6. Create a Pull Request

```bash
git push -u origin frontend/map-component

gh pr create \
  --title "feat(frontend): implement Mapbox GL map with parcel polygons" \
  --body "$(cat <<'EOF'
## Summary
- Implement interactive map component with Mapbox GL JS
- Add parcel polygon rendering with color coding

## Phase & Task Reference
- Phase: Phase 2
- Task: 2.3 Build frontend application

## Quality Checklist
- [x] Code follows CLAUDE.md conventions
- [x] Tests added and passing
- [x] Linting passes
- [x] No secrets in code
- [x] All geometry is EPSG:4326
EOF
)"
```

### 7. CI Must Pass

These gates must ALL pass before merge:
1. **Commit Lint** — conventional commit format
2. **Security Scan** — no secrets, no vulnerable patterns
3. **Backend Quality** — ruff lint, ruff format, ty check, pytest (via uv)
4. **Frontend Quality** — eslint, tsc, vitest
5. **Data Integrity** — SRID consistency, outSR validation
6. **PR Format** — title format, body completeness
7. **Gemini Code Assist Review** — automated AI code review

### 9. Respond to PR Review Comments

**Gemini Code Assist** automatically reviews every PR. Before merge:
- All review conversations must be **resolved**
- Every review comment must receive a **one-line reply** describing what was done to address it
- If a comment is dismissed, reply with the reason for dismissal
- No PR may be merged with unresolved review threads (enforced by GitHub branch protection)

### 8. Clean Up Worktree After Merge

```bash
git worktree remove ../bayit-frontend-map
git branch -d frontend/map-component
```

## Quality Standards

### Python (Backend & Pipeline)
- **Use `uv` for everything** — `uv sync`, `uv add`, `uv run`
- **Lint/format with `ruff`** — `uv run ruff check`, `uv run ruff format`
- **Type check with `ty`** — `uv run ty check`
- Type annotations on all functions
- Pydantic models for all API request/response schemas
- `async`/`await` for all database operations
- Parameterized SQL queries only — NO f-strings in SQL
- Tests with pytest + pytest-asyncio (`uv run pytest`)

### JavaScript/TypeScript (Frontend)
- React functional components with hooks
- Props typed with TypeScript interfaces
- Custom hooks for data fetching (React Query)
- Component tests with vitest + testing-library

### SQL (Database)
- Spatial indexes (GIST) on all geometry columns
- All geometry in EPSG:4326
- Materialized views for complex joins
- Migration files in `sql/migrations/` with sequential numbering

### GIS Data
- Always request `outSR=4326` from ArcGIS REST APIs
- Validate PID format: `^\d{3}-\d{3}-\d{3}$`
- Lot area in square meters (m²)
- Use `ST_Intersects` for spatial joins, `ST_Centroid` for point-in-polygon
