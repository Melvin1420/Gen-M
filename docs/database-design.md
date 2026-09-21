# Gen-M — Database Design

## Entity Relationship Overview

Department (1) ───< (many) User
User (1) ───< (many) Ticket [as requester]
Department (1) ───< (many) Ticket [auto-routed queue]
User (1) ───< (many) Ticket [as assigned_agent, nullable]
Ticket (1) ───< (many) TicketMessage
User (1) ───< (many) TicketMessage [as sender]
User (1) ───< (0..1) Asset [assigned_to, nullable]

## Tables

### roles
| Column | Type | Constraints |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(50) | UNIQUE, NOT NULL (e.g. "employee", "agent", "manager", "admin") |

### departments
| Column | Type | Constraints |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(100) | UNIQUE, NOT NULL |
| created_at | DATETIME | NOT NULL, server default now |

### users
| Column | Type | Constraints |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| full_name | VARCHAR(150) | NOT NULL |
| email | VARCHAR(150) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| role_id | INT | FK -> roles.id, NOT NULL |
| department_id | INT | FK -> departments.id, NOT NULL |
| is_active | BOOLEAN | NOT NULL, default TRUE |
| created_at | DATETIME | NOT NULL, server default now |

### assets
| Column | Type | Constraints |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| asset_tag | VARCHAR(50) | UNIQUE, NOT NULL |
| type | VARCHAR(50) | NOT NULL (e.g. "Laptop", "Monitor", "Phone") |
| model | VARCHAR(100) | NULL |
| serial_number | VARCHAR(100) | NULL |
| status | ENUM | "in_use", "in_storage", "retired" |
| assigned_to | INT | FK -> users.id, NULL |
| purchased_at | DATE | NULL |
| created_at | DATETIME | NOT NULL, server default now |

### tickets
| Column | Type | Constraints |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| ticket_number | VARCHAR(50) | UNIQUE, NOT NULL |
| title | VARCHAR(200) | NOT NULL |
| description | TEXT | NOT NULL |
| category | VARCHAR(50) | NOT NULL (drives auto-routing) |
| status | ENUM | "open", "in_progress", "resolved", "closed" |
| priority | ENUM | "low", "medium", "high", "critical" |
| requester_id | INT | FK -> users.id, NOT NULL |
| department_id | INT | FK -> departments.id, NOT NULL |
| assigned_agent_id | INT | FK -> users.id, NULL |
| created_at | DATETIME | NOT NULL, server default now |
| updated_at | DATETIME | NOT NULL, auto-update on change |

### ticket_messages
| Column | Type | Constraints |
|---|---|---|
| id | INT | PK, AUTO_INCREMENT |
| ticket_id | INT | FK -> tickets.id, NOT NULL |
| sender_id | INT | FK -> users.id, NOT NULL |
| message | TEXT | NOT NULL |
| created_at | DATETIME | NOT NULL, server default now |

## Design notes
- `assigned_agent_id` is nullable because a ticket starts in a department
  queue unassigned to any specific person — matches the auto-route-then-
  manually-reassign flow from requirements.md.
- `roles` is its own table (not a hardcoded enum on `users`) so new roles
  can be added later without a schema migration — small cost now, saves
  a migration later.
- All FKs use `ON DELETE RESTRICT` by default (decided during GEN-4) so
  deleting a Department/User with existing tickets fails loudly instead
  of silently orphaning records.