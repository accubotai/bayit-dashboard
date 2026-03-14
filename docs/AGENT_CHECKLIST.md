# Agent Pre-Flight Checklist

Before starting ANY task, every agent must complete this checklist.

## Before Writing Code

- [ ] Read CLAUDE.md (project rules)
- [ ] Read PROJECT.md section relevant to your Phase/Task
- [ ] Confirm branch follows naming convention: `{prefix}/{description}`
- [ ] Confirm you are in an isolated worktree (NOT on main)
- [ ] Confirm changes are within your directory scope
- [ ] Run `uv sync --dev` to install dependencies

## Before Committing

- [ ] Pre-commit hooks pass: `uv run pre-commit run --all-files`
- [ ] Python: `uv run ruff check backend/` passes
- [ ] Python: `uv run ruff format --check backend/` passes
- [ ] Python: `uv run ty check backend/` passes
- [ ] Frontend: `npx eslint src/` passes (if applicable)
- [ ] Tests pass: `uv run pytest` / `npx vitest run`
- [ ] No secrets in code
- [ ] No SQL string interpolation
- [ ] All geometry uses SRID 4326
- [ ] Commit message follows conventional commits

## Before Creating PR

- [ ] PR title: `type(scope): description`
- [ ] PR body uses template
- [ ] Phase and Task referenced
- [ ] Test evidence included
- [ ] Breaking changes documented

## After PR Review (Gemini Code Assist + human)

- [ ] Every review comment has a one-line reply describing the action taken
- [ ] Dismissed comments have a reply explaining why
- [ ] All review conversations are resolved
- [ ] All CI checks are green

## After PR Merged

- [ ] Clean up worktree: `git worktree remove <path>`
- [ ] Delete local branch: `git branch -d <branch>`
