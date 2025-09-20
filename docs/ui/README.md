# UI

Language: TypeScript / React + shadcn/ui

## Overview

The UI is a React + TypeScript application using shadcn/ui components. It allows users to create and manage tasks, monitor status, and visualize results produced by the Agents via the Manager.

## Scope (MVP)

- Create and manage tasks
- Show task status and resource utilization (basic)
- Display results, including charts for scraped/processed data

## Architecture (high level)

- Component library: shadcn/ui
- Routing and state management: TBD
- Data access: TBD (GraphQL vs REST). Consider encapsulating data fetching behind adapters to keep UI agnostic.
- Realtime updates: TBD (polling, WebSockets, or SSE)

## Implementation notes (TBD)

- Folder structure and feature modules
- Theming and design tokens
- Accessibility and responsiveness

## Charts and visualization (TBD)

- Charting library choice and integration
- Data shape contracts and formatting utilities

## Open questions to resolve (answer here when decided)

1. Will the UI consume GraphQL or REST?
2. How are real-time updates handled (polling, websockets, SSE)?
3. How are charts and visualizations implemented?
4. What state management approach is used?

## ADRs and references

- Global ADRs: `docs/adr/`
- UI ADRs: `docs/ui/adr/` (to be added)

## Try it (placeholder)

Development setup and commands will be added once the UI scaffold exists.
