#Gen-M Backlog

Status values: 'TODO' | 'IN PROGRESS' | 'DONE'

| ID | Title | Status | Depends on |
|---|---|---|---|
| GEN-1 | Project scaffolding (corporate folder structure) | IN PROGRESS | — |
| GEN-2 | Requirements & database design docs | TODO | GEN-1 |
| GEN-3 | Core app skeleton (FastAPI app, config, DB session) | TODO | GEN-2 |
| GEN-4 | User & Role models + Alembic migration | TODO | GEN-3 |
| GEN-5 | Auth service (password hashing, JWT) | TODO | GEN-4 |
| GEN-6 | Ticket model + CRUD endpoints | TODO | GEN-4 |
| GEN-7 | Tests for auth + tickets | TODO | GEN-5, GEN-6 |

## Ticket format
Each ticket, when picked up, should have:
- **Description** — what needs to be built
- **Acceptance criteria** — how we know it's done
- **Branch** — `feature/GEN-<n>-<short-slug>`