# Agent Pre-Flight Checklist

Before starting ANY task, every agent must complete this checklist.

## Before Writing Code

- [ ] Read CLAUDE.md (project rules)
- [ ] Read PROJECT.md section relevant to your Phase/Task
- [ ] Confirm branch follows naming convention: `{prefix}/{description}`
- [ ] Confirm you are in an isolated worktree (NOT on main)
- [ ] Confirm changes are within your directory scope

## Before Committing

- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] Python: `ruff check backend/` passes
- [ ] Python: `ruff format --check backend/` passes
- [ ] Frontend: `npx eslint src/` passes (if applicable)
- [ ] Tests pass: `pytest` / `vitest run`
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

## After PR Merged

- [ ] Clean up worktree: `git worktree remove <path>`
- [ ] Delete local branch: `git branch -d <branch>`
