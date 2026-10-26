# Architecture — Incremental Implementation

## Implemented primitives
- FastAPI serves a local status dashboard and non-sensitive health/status endpoints.
- Typed declarative automation rules use allowlisted triggers, conditions, and actions. Handlers are injected explicitly; arbitrary user code is never evaluated.
- SQLite job store persists one-shot jobs and supports due lookup and lifecycle status changes. A background worker, retries, and job claiming are not implemented.
- Fernet session vault encrypts serialized session bytes at rest. The key must be managed outside Git. Telegram login, 2FA, session revocation, and MTProto are not implemented.
- SQLite audit trail records actor/action/outcome and redacts fields with sensitive names before persistence.
- AI provider interface includes a disabled provider and an Ollama adapter with bounded request timeout and safe failure results.
- CI covers Python 3.11 and 3.12; tests exercise the web foundation and the primitives above.

## Intended module boundaries
- app/telegram/: Bot API and user-authorized MTProto clients, session lifecycle, and rate-aware operations.
- app/ai/: provider adapters, model configuration, prompt handling, and redaction.
- app/content/: draft generation, review, and explicit publishing confirmation.
- app/automation/: validated rules, permission gates, execution records, cancellation, and audit events.
- app/scheduler/: durable jobs, retry policy, worker loop, and safe shutdown.
- app/security/: encryption, authorization, secret redaction, and session lifecycle safeguards.
- Future GhYiAb integrations for commerce, support, advertising, n8n, wallet, and 3x-ui must only be designed after the actual GhYiAb repository and specs are available; do not invent internal contracts.

## Security invariants
- Never commit or return session data, API hashes, bot tokens, AI keys, databases, or private user data.
- AI may propose actions but must not access the database directly or bypass a policy/permission layer.
- Operational dashboard controls require authentication and authorization before public deployment.
- Respect Telegram limits and user authorization; no unsolicited bulk messaging or evasion behavior.
- Donations are optional and never gate functionality.

## Not yet implemented
Telegram Bot API/MTProto connection, login/2FA, background job worker, RBAC, authenticated operations UI, full FA/EN localization, full event monitoring, and end-to-end integration tests remain pending.
