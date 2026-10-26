# Architecture — Incremental Implementation

## Implemented primitives
- FastAPI serves a local status dashboard and non-sensitive health/status endpoints.
- Typed declarative automation rules use allowlisted triggers, conditions, and actions. Handlers are injected explicitly; arbitrary user code is never evaluated.
- SQLite job storage normalizes timezone-aware timestamps to UTC and supports additive migration of attempt, lock, and last-error metadata.
- `JobStore.claim_due` uses a write transaction to claim pending jobs atomically, reducing duplicate execution across competing workers.
- `JobWorker` calls only explicitly registered handlers, tracks completed/retried/failed outcomes, uses bounded exponential retry delays, recovers expired worker leases, and avoids persisting exception messages.
- Fernet session vault encrypts serialized session bytes at rest. The key must be managed outside Git. Telegram login, 2FA, session revocation, and MTProto are not implemented.
- SQLite audit trail records actor/action/outcome and redacts fields with sensitive names before persistence.
- AI provider interface includes a disabled provider and an Ollama adapter with bounded request timeout and safe failure results.
- CI covers Python 3.11 and 3.12; tests cover the web foundation and implemented primitives.

## Scheduler semantics and limitations
- Job handlers are registered by job type; payloads are data only and never executable code.
- Handler exceptions are reduced to the exception class name for persisted failure metadata.
- Retries are bounded by `max_attempts`; retry delay grows exponentially and is capped at five minutes.
- A handler may run more than once if the process crashes after the external side effect but before the job is marked complete. Handlers should therefore be idempotent.
- Expired `running` jobs are requeued when attempts remain and marked failed after the attempt limit. This is at-least-once delivery: a crash after an external side effect may cause the handler to run again, so handlers must be idempotent.
- Distributed leases, job cancellation API, and worker deployment wiring remain pending.

## Intended module boundaries
- `app/telegram/`: Bot API and user-authorized MTProto clients, session lifecycle, and rate-aware operations.
- `app/ai/`: provider adapters, model configuration, prompt handling, and redaction.
- `app/content/`: draft generation, review, and explicit publishing confirmation.
- `app/automation/`: validated rules, permission gates, execution records, cancellation, and audit events.
- `app/scheduler/`: durable jobs, retry policy, worker loop, and safe shutdown.
- `app/security/`: encryption, authorization, secret redaction, and session lifecycle safeguards.
- Future GhYiAb integrations for commerce, support, advertising, n8n, wallet, and 3x-ui must only be designed after the actual GhYiAb repository and specs are available; do not invent internal contracts.

## Security invariants
- Never commit or return session data, API hashes, bot tokens, AI keys, databases, or private user data.
- AI may propose actions but must not access the database directly or bypass a policy/permission layer.
- Operational dashboard controls require authentication and authorization before public deployment.
- Respect Telegram limits and user authorization; no unsolicited bulk messaging or evasion behavior.
- Donations are optional and never gate functionality.

## Not yet implemented
Telegram Bot API/MTProto connection, login/2FA, RBAC, authenticated operations UI, full FA/EN localization, full event monitoring, GhYiAb V2 integration, and end-to-end integration tests remain pending.
