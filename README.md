# GhYiAb Self — by MohZarg

GhYiAb Self is a free, open-source foundation for authorized Telegram account automation, developed and maintained publicly under the MohZarg brand.

> Development status: core primitives and a bounded scheduler worker are implemented. Telegram Bot API, MTProto login/2FA, a production-ready authenticated dashboard, and the GhYiAb V2 integration are not implemented yet.

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

## Implemented in the current feature branch
- FastAPI dashboard and non-sensitive health/status endpoints.
- Basic security response headers and environment validation.
- Declarative automation rules with allowlisted triggers, conditions, and actions; no user-supplied code execution.
- SQLite job store with timezone-normalized timestamps, atomic due-job claiming, attempt tracking, and retry metadata.
- Explicit-handler scheduler worker with bounded exponential backoff and sanitized error handling.
- Fernet authenticated encryption vault for serialized session bytes.
- SQLite audit trail with conservative secret redaction.
- Provider-independent AI interface, disabled fallback, and Ollama adapter.
- Docker foundation, CI for Python 3.11/3.12, and unit tests for the implemented primitives.

## Still pending
- Telegram Bot API admin bot; MTProto login, 2FA, connect/disconnect/revoke, and device audit.
- Stale-job recovery after process crashes, worker process packaging, cancellation, and end-to-end scheduler operations.
- Permission/RBAC layer and authenticated operational dashboard.
- AI supervisor, intent detection, action planner, and approval for consequential actions.
- Telegram event integrations, profile/message automation, and complete Persian/English RTL/LTR UI.
- GhYiAb V2 source audit and integration; its Master Spec, STATUS, and implementation-gap report are not available in this repository context.
- Security/dependency audit and clean-install verification.

See docs/ROADMAP.md and docs/ARCHITECTURE.md.

## Requirements and local run
- Python 3.11 or 3.12; pip and a virtual environment.
- Clone this repository, check out `feat/project-foundation`, then install with: `python -m pip install -e ".[dev]"`
- Start with: `uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Dashboard: http://127.0.0.1:8000 ; API docs: http://127.0.0.1:8000/api/docs
- Tests: `python -m compileall -q app tests && python -m pytest`

## Module boundaries
- Automation engine evaluates typed rules and delegates to explicitly registered handlers; it does not send Telegram messages itself.
- Scheduler store atomically claims due jobs; `JobWorker` invokes only explicitly registered handlers and applies bounded retry delays. Handlers should be idempotent. Stale running-job recovery is not implemented.
- Session vault encrypts serialized bytes; the key must remain outside the repository. This is not Telegram login or session revocation.
- AI adapter provides local Ollama HTTP support and safe failure results; AI does not directly execute sensitive account actions.

## Deployment and safety
The default Compose setup binds to loopback. Do not expose this development foundation publicly before authentication, authorization, worker controls, and production hardening are implemented. Operate only accounts and channels you are authorized to manage. Do not spam or bypass Telegram limits. Never send session data or encryption keys to an AI provider.

## Security and license
Review SECURITY.md and CONTRIBUTING.md. MIT License. Donations may optionally support development but never unlock functionality.

Product: GhYiAb Self · Creator/Maintainer: MohZarg — https://MohZarg.ir · https://github.com/MohZarg
Repository: https://github.com/MohZarg/MohZarg-Telegram-Self-AI
