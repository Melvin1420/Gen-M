# Gen-M Frontend Design

## Approach

One app shell (sidebar nav + top bar + content area), not four separate
frontends per role. Navigation and visible actions are driven by the
`role` field from `GET /api/v1/auth/me` at load time - same HTML/JS
codebase, different rendered state. Plain HTML/CSS/JS per the project's
stated stack; no framework, no build step.

The JWT from login is stored in `sessionStorage` (not `localStorage`) -
cleared when the tab closes, reducing the window a stolen token stays
valid if a device is left unlocked. Every fetch to the API attaches it
as `Authorization: Bearer <token>`. A 401 response anywhere redirects
to the login page and clears the stored token.

## Screens

| Screen | Employee | IT Agent | Manager | Admin |
|---|---|---|---|---|
| Login | Y | Y | Y | Y |
| Ticket queue | own tickets only | assigned + unassigned in dept | dept-wide | all |
| Ticket detail + messages | edit title/desc while `open`; post messages | full edit (status/priority/assignment) | full edit | full edit |
| New ticket | Y | Y | Y | Y |
| Asset list | assigned to me only | full CRUD | view dept only, no edit | full CRUD |
| Department management | - | - | - | Y only |
| User management | - | - | - | Y only |

## Screen -> API mapping

- **Login** -> `POST /api/v1/auth/login`, then `GET /api/v1/auth/me` to
  get the role and populate the shell.
- **Ticket queue** -> `GET /api/v1/tickets` (server already filters by
  role - no client-side role logic needed for visibility).
- **Ticket detail** -> `GET /api/v1/tickets/{id}`,
  `GET /api/v1/tickets/{id}/messages`,
  `POST /api/v1/tickets/{id}/messages`,
  `PATCH /api/v1/tickets/{id}` (form fields shown depend on role: an
  Employee sees title/description only while status is `open`; staff
  see status/priority/department/assignment).
- **New ticket** -> `GET /api/v1/departments` (populate a dropdown),
  `POST /api/v1/tickets`.
- **Asset list** -> `GET /api/v1/assets` (role-filtered server-side);
  `POST`/`PATCH /api/v1/assets` only rendered for Agent/Admin.
- **Department management** -> full CRUD against `/api/v1/departments`,
  Admin-only nav item.
- **User management** -> full CRUD against `/api/v1/users`, Admin-only
  nav item; includes the password-reset action from GEN-8.

## Build order

1. Login page + token storage
2. App shell with role-aware nav (static, no real data yet)
3. Ticket queue (read-only) - proves the shell can call an
   authenticated endpoint and render a list
4. New ticket form
5. Ticket detail + message thread
6. Asset list, then Department/User admin screens last, since they're
   Admin-only and lowest-traffic
