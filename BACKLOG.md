#Gen-M Backlog

Status values: 'TODO' | 'IN PROGRESS' | 'DONE'

| ID | Title | Status | Depends on |
|---|---|---|---|
| GEN-1 | Project scaffolding (corporate folder structure) | DONE | — |
| GEN-2 | Requirements & database design docs | DONE | GEN-1 |
| GEN-3 | Core app skeleton (FastAPI app, config, DB session) | DONE | GEN-2 |
| GEN-4 | User & Role models + Alembic migration | DONE | GEN-3 |
| GEN-5 | Auth service (password hashing, JWT) | DONE | GEN-4 |
| GEN-6 | Ticket model + CRUD endpoints | DONE | GEN-4 |
| GEN-7 | Tests for auth + tickets | DONE | GEN-5, GEN-6 |
| GEN-8 | Department & user admin endpoints | DONE | GEN-5 |
| GEN-9 | CI pipeline (GitHub Actions: lint, type-check, tests) | DONE | GEN-7 |
| GEN-10 | Asset CRUD endpoints | DONE | GEN-4 |
| GEN-11 | Frontend design doc (screens, API mapping, build order) | DONE | GEN-10 |
| GEN-12 | Login page | DONE | GEN-11 |
| GEN-13 | Ticket queue page | DONE | GEN-12 |
| GEN-14 | Ticket detail page + message thread | DONE | GEN-13 |
| GEN-15 | Dashboard with needs-attention list | TODO | GEN-14 |
| GEN-16 | Fix timestamp timezone bug (resolved_at vs created_at) | IN PROGRESS | GEN-14 |
| GEN-17 | Return display names in ticket/message API responses | TODO | GEN-14 |
| GEN-18 | New-ticket form | TODO | GEN-13 |
| GEN-19 | Fix frontend timestamp display across timezones | TODO | GEN-16 |

## Ticket format
Each ticket, when picked up, should have:
- **Description** — what needs to be built
- **Acceptance criteria** — how we know it's done
- **Branch** — `feature/GEN-<n>-<short-slug>`
