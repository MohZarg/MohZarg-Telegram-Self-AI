# GhYiAb Self — by MohZarg

GhYiAb Self is a free, open-source foundation for authorized Telegram account automation, developed and maintained publicly under the MohZarg brand.

> Development status: core primitives, a bounded scheduler worker, Telegram configuration validation, and a restricted Bot API client are implemented. MTProto is not implemented. Public cloud deployment is blocked until authentication, authorization, and production hardening are implemented.

## Brand and sustainable open source
- Product: **GhYiAb Self**. Creator and public development brand: **MohZarg**.
- The dashboard includes a clearly disclosed, optional MohZarg creator promotion linking to https://MohZarg.ir. It is not targeted advertising, does not track users, and never unlocks or restricts features.
- Optional donations and creator promotions support visibility and development; neither is required to use the software.
- The product remains free and open source under MIT, with no license key, mandatory subscription, or paywall.

## Principles
- Free and open source under MIT; personal and commercial use permitted.
- No paid edition, license key, mandatory subscription, paywall, or artificial feature restrictions.
- Donations are optional and never unlock features.
- Never commit credentials, Telegram sessions, AI keys, databases, backups, or private user data.

## Implemented
- FastAPI dashboard and non-sensitive health/status endpoints.
- Basic security response headers and environment validation.
- Declarative automation rules with allowlisted triggers, conditions, and actions; no user-supplied code execution.
- SQLite job store with timezone-normalized timestamps, atomic due-job claiming, attempt tracking, bounded retries, and stale worker-lease recovery.
- Explicit-handler scheduler worker with bounded exponential backoff and sanitized error handling.
- Fernet authenticated encryption vault for serialized session bytes.
- SQLite audit trail with conservative secret redaction.
- Provider-independent AI interface, disabled fallback, and Ollama adapter.
- Telegram mode configuration validator for `disabled`, `bot`, `mtproto`, and `both`; missing/invalid selected-mode settings fail closed and secrets are excluded from the settings representation.
- Restricted async Telegram Bot API adapter with `getMe`, plain-text messaging only to the configured admin chat, injectable fake transport for tests, and sanitized error messages.
- Cloud deployment safety gate, dual Telegram integration boundary, Docker foundation, CI for Python 3.11/3.12, and unit tests for implemented primitives.

## Still pending
- Bot API update polling/webhook, admin identity verification beyond the configured destination, operational lifecycle, rate limits, and application startup wiring.
- MTProto client, login, 2FA, connect/disconnect/revoke, session lifecycle, and device audit.
- Authentication, RBAC, rate limiting, and protected operational dashboard.
- Worker process packaging, cancellation, operational controls, and end-to-end scheduler operations.
- AI supervisor, intent detection, action planner, and approval for consequential actions.
- Telegram event integrations, profile/message automation, and complete Persian/English RTL/LTR UI.
- GhYiAb V2 source audit and integration; no separate V2 repository or Master Spec/STATUS/gap report has been identified.
- Security/dependency audit and clean-install verification.

## Requirements and local run
- Python 3.11 or 3.12; pip and a virtual environment.
- Clone this repository's `main` branch, then install with: `python -m pip install -e ".[dev]"`
- Start with: `uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Dashboard: http://127.0.0.1:8000 ; API docs: http://127.0.0.1:8000/api/docs
- Tests: `python -m compileall -q app tests && python -m pytest`

## Module boundaries
- Automation engine evaluates typed rules and delegates to explicitly registered handlers; it does not send Telegram messages itself.
- Scheduler store atomically claims due jobs; `JobWorker` invokes only explicitly registered handlers and applies bounded retry delays. Handlers must be idempotent. Recovery is at-least-once and may repeat an external side effect after a crash.
- Session vault encrypts serialized bytes; the key must remain outside the repository. This is not Telegram login or session revocation.
- Bot API adapter only exposes identity lookup and sends plain text to one configured admin chat; it does not poll updates or authorize arbitrary chat targets.
- Telegram configuration validation is a standalone boundary and is not wired into application startup.
- AI adapter provides local Ollama HTTP support and safe failure results; AI does not directly execute sensitive account actions.

## Administrative access
- In `APP_ENV=production`, HTTP Basic authentication protects the dashboard, status API, API root, OpenAPI schema, and interactive API docs. `/api/health` remains a minimal liveness probe.
- Set `ADMIN_USERNAME` and a long, unique `ADMIN_PASSWORD` through the host's secret configuration. If either is missing, protected routes fail closed with HTTP 503.
- Development mode intentionally keeps local routes accessible for development. Do not use development mode on an internet-facing deployment.
- This is a single-admin authentication baseline, not multi-user RBAC, session management, CSRF protection, or rate limiting. Use HTTPS before any remote access; do not expose port 8000 directly.

## Cloud deployment and safety
The default Compose setup binds to loopback. Do not expose this development foundation publicly before authentication, authorization, worker controls, and production hardening are implemented. See [Cloud Deployment Readiness](docs/CLOUD_DEPLOYMENT.md) for release blockers and the safe deployment checklist. See [Telegram Integration Boundary](docs/TELEGRAM_INTEGRATION.md) for the dual-adapter plan. Operate only accounts and channels you are authorized to manage. Do not spam or bypass Telegram limits. Never send session data or encryption keys to an AI provider.

## Security and license
Review SECURITY.md and CONTRIBUTING.md. MIT License. Donations may optionally support development but never unlock functionality.

Product: GhYiAb Self · Creator/Maintainer: MohZarg — https://MohZarg.ir · https://github.com/MohZarg
Repository: https://github.com/MohZarg/MohZarg-Telegram-Self-AI
