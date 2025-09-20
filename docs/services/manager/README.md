# Manager Service

Language: Go

## Overview

The Manager is a Go service responsible for scheduling and orchestrating AI Agent tasks based on available CPU/GPU resources. It exposes a service interface for the UI and coordinates the execution lifecycle with the Agents service.

## Responsibilities

- Accept tasks from the UI or other clients
- Schedule and dispatch tasks to Agents based on CPU/GPU availability
- Track task status, progress, and results
- Enforce concurrency/quotas and handle retries
- Collect resource telemetry (CPU, memory, GPU) to inform scheduling decisions

## Architecture (high level)

- API Layer: Exposes Manager endpoints (protocol TBD: REST or gRPC)
- Scheduler Core: Queueing, prioritization, admission control, retries
- Resource Telemetry: CPU and GPU metrics collectors (e.g., OS metrics, NVML)
- Agents Client: Communication with Agents (protocol TBD)
- State/Storage: Task state, logs, artifacts (backend TBD)

> Integration points and protocols are intentionally left TBD to keep the implementation flexible until the ADRs are finalized.

## Interfaces (TBD)

- Manager ↔ UI: TBD (REST/GraphQL via an API gateway or direct REST)
- Manager ↔ Agents: TBD (REST vs gRPC vs MQ)

Define types and contracts in a shared `contracts/` folder once decisions are made, or generate from OpenAPI/protobuf.

## Scheduling policy (TBD)

- Initial heuristic: FIFO with resource-aware checks (CPU/GPU). Extensions may include priorities, fair-share, preemption.
- GPU-awareness: account for VRAM budget per model/agent, avoid oversubscription. RTX 4060 class GPU assumed.

## Resource telemetry (TBD)

- CPU/memory: OS metrics (e.g., Go runtime + platform APIs)
- GPU: NVIDIA NVML or `nvidia-smi` wrappers

## Configuration (TBD)

- Environment variables for ports, scheduler knobs, telemetry intervals
- Limits: max concurrent tasks, max GPU utilization thresholds

## Runbook (TBD)

- Start the service
- Health checks
- Logs and troubleshooting

## Open questions to resolve (answer here when decided)

1. How does the Manager interact with Agents (REST, gRPC, MQ)?
2. What resource telemetry sources are used for CPU/GPU monitoring?
3. How are tasks queued, prioritized, retried, and what are failure policies?
4. What persistence is used for task state and artifacts?
5. How are security/auth and multi-tenant concerns handled (if any)?

## ADRs and references

- Global ADRs: `docs/adr/`
- Manager ADRs: `docs/services/manager/adr/` (to be added as decisions are made)

## Try it (placeholder)

Setup and commands will be added once the implementation and build tooling are in place.
