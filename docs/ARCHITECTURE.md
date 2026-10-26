# Architecture — Incremental Implementation

## Current executable slice

- **FastAPI** serves a local status dashboard and health/status endpoints.
- **Settings** validates basic environment configuration without returning credentials.
- **Automation engine** evaluates typed, declarative rules using an allowlisted trigger/condition/action model. It never executes user-supplied code and delegates actions to explicitly registered handlers.
- **SQLite job store** persists one-shot scheduled jobs and supports due-job lookup and lifecycle status updates. A background worker, retries, and distributed locking are not implemented yet.
- **Session vault** encrypts/decrypts serialized session bytes using Fernet authenticated encryption. The key must be supplied out of band; Telegram login, session revocation, and MTProto integration are not implemented yet.
- **AI provider adapter** defines a provider-independent interface, a disabled fallback, and an Ollama HTTP adapter with bounded timeout and response handling. No AI operation is exposed as an autonomous account action.
- **CI and tests** cover the app foundation plus automation, scheduler, session vault, and provider fallback.

## Intended module boundaries

- `app/telegram/`: Bot API and user-authorized MTProto clients; session lifecycle and rate-aware operations.
- `app/ai/`: provider adapters, model configuration, prompt handling, and redaction.
- `app/content/`: draft generation, review, and explicit publishing confirmation.
- `app/automation/`: validated rules, permission gates, execution records, cancellation, and audit events.
- `app/scheduler/`: durable jobs, retry policy, worker loop, and safe shutdown.
- `app/security/`: secret redaction, encryption, authorization, and session lifecycle safeguards.
- `app/monitoring/`: health, metrics, and redacted diagnostics.
- `app/dashboard/`: authenticated configuration and operation views.
- Future platform integrations: commerce, support, advertising, and optional n8n bridge should use the same policy-controlled service layer rather than duplicate business logic.

## Security invariants

- No session data, API hashes, bot tokens, AI keys, or private user data in Git, frontend bundles, logs, or API responses.
- AI may propose intents/actions, but a policy and permission layer must validate them before execution.
- Operational dashboard controls must be authenticated and authorized before public deployment.
- Actions must respect Telegram limits and user authorization; no unsolicited bulk messaging or evasion behavior.
- Donation support is optional and never gates functionality.

## Honest implementation boundary

This branch contains infrastructure primitives only. It does **not** yet connect to Telegram Bot API or MTProto, run a scheduler worker, provide account login/2FA, expose a production admin dashboard, implement RBAC/audit persistence, or complete FA/EN localization. Those must remain marked as pending until implemented and tested.
