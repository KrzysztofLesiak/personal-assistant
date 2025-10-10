# Task Service — Specification & Development Tickets (C# .NET)

**Created:** 2025-10-09

---

## Summary

Standalone **Task Service** microservice implemented in **C# (.NET 8)**. Provides REST API for creating, updating, querying, and automating tasks. AI integration is planned but out of scope for initial implementation. No Project/Feature service placeholders will be included.

This document contains:

- High-level architecture
- Data model and DB schema
- REST API contract (endpoints + sample payloads)
- Non-functional requirements
- Implementation tickets with acceptance criteria and technical notes
- Open questions and next steps

---

## Goals (MVP)

1. Core task lifecycle: create, read, update, delete tasks and subtasks
2. Typed relations between tasks (depends_on, blocks, duplicates, relates_to, documents)
3. Attachments (file metadata) and checklists
4. Comments and change-history audit log
5. Calendar API for fetching tasks in date ranges
6. Ability to assign AI as an assignee (logical — integration later)
7. Expose a clean REST API and OpenAPI documentation

---

## Tech Stack

- Language: **C# (.NET 8)**
- Web: ASP.NET Core Web API
- ORM: **Entity Framework Core** (PostgreSQL provider)
- Database: **PostgreSQL**
- Caching: **Redis** (for calendar/queries caching)
- Migrations: **EF Core Migrations**
- Tests: **xUnit**
- Logging: **Serilog** (structured logging)
- Containerization: **Docker**
- CI/CD: (placeholder) GitHub Actions

---

## High Level Architecture

- `TaskService.API` — REST controllers, validation, request/response models
- `TaskService.Core` — domain entities, business logic, domain services
- `TaskService.Infrastructure` — EF Core DbContext, repositories, file storage adapters
- `TaskService.AIAdapter` — empty adapter interface for later AI integrations
- `TaskService.Tests` — unit/integration tests

Inter-service communication is out of scope for the MVP.

---

## Data Model (simplified)

### Tables / Entities

#### Task

- `Id` (UUID PK)
- `Title` (varchar)
- `Description` (text)
- `Type` (varchar) — enum: `Epic`, `Story`, `Task`, `Bug` (string-backed)
- `Status` (varchar) — enum: `Todo`, `InProgress`, `Blocked`, `Done`, `Cancelled`
- `Priority` (varchar) — `Low`, `Medium`, `High`, `Critical`
- `AssigneeId` (UUID, nullable) — could reference users or string `AI:assistant`.
- `StartDate` (timestampz, nullable)
- `EndDate` (timestampz, nullable)
- `TimeEstimateMinutes` (int, nullable)
- `TimeTrackedMinutes` (int, default 0)
- `Tags` (jsonb) — array of strings
- `CreatedAt` (timestampz)
- `UpdatedAt` (timestampz)
- `CreatedBy` (UUID)
- `IsDeleted` (bool)

#### Subtask Extends Task

- `ParentId` -(UUID FK -> Task.Id)

#### Attachment

- `Id` (UUID PK)
- `TaskId` (UUID FK)
- `FileName`, `MimeType`, `Url`, `SizeBytes`, `UploadedAt`

#### ChecklistItem

- `Id` (UUID PK)
- `TaskId` (UUID FK)
- `Title`, `IsDone`, `OrderIndex`

#### Relation

- `Id` (UUID PK)
- `SourceTaskId` (UUID FK)
- `TargetTaskId` (UUID FK)
- `Type` (varchar) — enum: `DependsOn`, `Blocks`, `Duplicates`, `RelatesTo`, `Documents`
- `CreatedAt`

#### Comment

- `Id` (UUID PK)
- `TaskId` (UUID FK)
- `AuthorId` (string)
- `Message` (text)
- `CreatedAt`
-

#### ChangeHistory

- `Id` (UUID PK)
- `TaskId` (UUID FK)
- `ActorId` (string)
- `FieldName` (varchar)
- `OldValue` (text)
- `NewValue` (text)
- `CreatedAt`

Notes:

- Use JSONB for flexible fields (tags, custom metadata) when needed.
- Support soft delete with `IsDeleted` (boolean) on Task if required later.

---

## REST API (selected endpoints)

Base path: `/api/v1/tasks`

### Create Task

```
POST /api/v1/tasks
Content-Type: application/json
{
  "title": "Implement calendar view",
  "description": "Calendar-based view for tasks",
  "type": "Task",
  "status": "Todo",
  "priority": "Medium",
  "assigneeId": null,
  "startDate": "2025-10-20T09:00:00Z",
  "endDate": "2025-10-21T17:00:00Z",
  "timeEstimateMinutes": 240,
  "tags": ["ux","calendar"]
}
```

Response: `201 Created` with Location header and created task JSON.

### Get Task

`GET /api/v1/tasks/{id}` — returns Task + subtasks + attachments + relations + comments + history (optionally via `include` query param)

### Update Task

`PATCH /api/v1/tasks/{id}` — Partial updates with JSON Patch or a lightweight DTO. Record changes to ChangeHistory.

### Delete Task

`DELETE /api/v1/tasks/{id}` — soft delete or hard delete depending on config.

### Create Relation

`POST /api/v1/tasks/{id}/relations`

```
{ "targetTaskId": "uuid", "type": "DependsOn" }
```

### Add Attachment metadata

`POST /api/v1/tasks/{id}/attachments` — accepts metadata; file upload may be direct-to-storage (S3) with presigned URL strategy.

### Add Comment

`POST /api/v1/tasks/{id}/comments` — create comment

### Calendar query

`GET /api/v1/tasks/calendar?from=2025-10-01&to=2025-10-31`

- Returns tasks with start/end falling inside range or tasks overlapping range.
- Response optimized for calendar client (start, end, title, id, colorTag)

---

## Non-functional Requirements

- **Performance:** Calendar queries must respond under 300ms for typical org size (<= 5K tasks).
- **Scalability:** DB indices on `StartDate`, `EndDate`, `AssigneeId`, `Status`.
- **Security:** JWT-based auth (placeholder); validate file uploads and sanitize inputs.
- **Observability:** Structured logging and metrics (Prometheus-friendly counters).
- **Data retention:** History kept indefinitely for MVP.

---

## Implementation Tickets (detailed)

### Ticket 001 — Project skeleton and CI

**Type:** Setup  
**Estimate:** 1d  
**Description:** Create repo, folder structure (`API`, `Core`, `Infrastructure`, `Tests`), Dockerfile, basic GitHub Actions CI that runs tests and builds.  
**Acceptance criteria:** Repo created; CI passes for build and tests (empty tests acceptable).

---

### Ticket 002 — Database schema & migrations

**Type:** Backend  
**Estimate:** 2d  
**Description:** Implement EF Core models and initial migration for Task, Subtask, Attachment, ChecklistItem, Relation, Comment, ChangeHistory.  
**Acceptance:** Migration runs and creates tables in PostgreSQL. Seed minimal test data.

---

### Ticket 003 — Task CRUD API

**Type:** Backend  
**Estimate:** 3d  
**Description:** Implement controllers, services, and repositories for Task entity. Support create, get (single), list (paged), patch update, delete.  
**Acceptance:** Endpoints working; integration tests cover basic flows; changes recorded in ChangeHistory on updates.

---

### Ticket 004 — Subtasks & Checklists

**Type:** Backend  
**Estimate:** 2d  
**Description:** Implement nested subtasks and checklist endpoints. Subtasks are lightweight tasks linked to parent.  
**Acceptance:** Can create/modify/delete subtasks; parent task aggregates subtask completion status.

---

### Ticket 005 — Relations (typed)

**Type:** Backend  
**Estimate:** 2d  
**Description:** Implement relation entity, endpoints to add/remove relations, validation to prevent circular `DependsOn` chains (basic detection).  
**Acceptance:** Relations can be created; API prevents direct circular dependency insertion.

---

### Ticket 006 — Attachments

**Type:** Backend  
**Estimate:** 2d  
**Description:** Implement attachment metadata endpoints with presigned upload flow (for future S3). For MVP, store file metadata and accept a `url` field.  
**Acceptance:** Attachments can be linked and retrieved.

---

### Ticket 007 — Comments + Change History

**Type:** Backend  
**Estimate:** 2d  
**Description:** Implement comment creation and persistent change history capturing field-level changes.  
**Acceptance:** Comments persisted; change history shows actor, timestamp, old/new values.

---

### Ticket 008 — Calendar API

**Type:** Backend  
**Estimate:** 2d  
**Description:** Implement `/calendar` endpoint returning tasks in date range with minimal projection. Add caching with Redis.  
**Acceptance:** Calendar endpoint returns expected payload; caching reduces DB load for repeat queries.

---

### Ticket 009 — AI Assignee placeholder & Context builder interface

**Type:** Infra/Design  
**Estimate:** 1d  
**Description:** Add `AssigneeType` enum and allow `AssigneeId` values like `AI:assistant`. Implement pluggable interface `IContextBuilder` that can be implemented later.  
**Acceptance:** Tasks can be assigned to AI string; `IContextBuilder` interface present and unit-tested with a dummy impl.

---

### Ticket 010 — API docs & OpenAPI

**Type:** Docs  
**Estimate:** 1d  
**Description:** Add Swagger/OpenAPI generation with representative examples for major endpoints.  
**Acceptance:** Swagger UI available in `Development` environment.

---

### Ticket 011 — Tests and QA

**Type:** QA  
**Estimate:** 3d  
**Description:** Unit tests for domain logic (status transitions, relation checks), integration tests for API endpoints, DB cleaning between tests.  
**Acceptance:** Coverage target (e.g., 60% backend logic); CI runs tests and fails on regressions.

---

### Ticket 012 — Logging, metrics, and health endpoints

**Type:** Infra  
**Estimate:** 1d  
**Description:** Add Serilog, `/health` and basic Prometheus metrics endpoint stubs.  
**Acceptance:** Logs structured; `/health` returns `200 OK`.

---

### Ticket 013 — Deployment (Docker) & local dev guide

**Type:** DevOps  
**Estimate:** 1d  
**Description:** Docker Compose for local dev (Postgres + Redis + API). README with run instructions.  
**Acceptance:** Developers can `docker-compose up` and run API locally.

---

## Acceptance Criteria (system-level)

- Tasks CRUD works and stores in DB.
- Subtasks, relations, attachments, comments, and history are available and linked.
- Calendar endpoint returns tasks within a date range and is reasonably performant.
- All endpoints documented via OpenAPI.

---

## Security & Auth (MVP)

- Implement a simple auth middleware stub that accepts a bearer token and sets `ActorId` on requests. Real auth (RBAC, OAuth) planned later.

---

## Open Questions (deferred)

1. Do we need multi-tenant support? (currently single-tenant)
2. Owner/organization model for tasks — where to store membership/ACLs? (deferred)
3. File storage choice (S3, Azure Blob) — deferred; MVP uses URLs.
4. Retention and GDPR delete flows — future work.

---

## Next steps / Suggested immediate priorities

- [ ] Approve spec and ticket list.
- [ ] Create repository and implement Ticket 001–003 in first sprint (sprint = 1 week suggested).
- [ ] Specify UI design
- [ ] When ready, specify AI integration details (LLM provider, vector DB, auth model).

---
