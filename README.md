# MohZarg Telegram Self AI

Free and open-source self-hosted AI assistance and authorized Telegram automation toolkit.

> Development status: core primitives are implemented and entering CI validation. Telegram Bot API, MTProto login/2FA, background workers, and a production-ready authenticated dashboard are not implemented yet.

## Principles
- Free and open source under MIT; personal and commercial use permitted.
- No paid edition, license key, mandatory subscription, paywall, or artificial feature restrictions.
- Donations are optional and never unlock features.
- Never commit credentials, Telegram sessions, AI keys, databases, backups, or private user data.

## Implemented in the current feature branch
- FastAPI dashboard and non-sensitive health/status endpoints.
- Basic security response headers and environment validation.
- Declarative automation rules with allowlisted triggers, conditions, and actions; no user-supplied code execution.
- SQLite one-shot job store with due-job lookup and lifecycle status.
- Fernet authenticated encryption vault for serialized session bytes.
- SQLite audit trail with conservative secret redaction.
- Provider-independent AI interface, disabled fallback, and Ollama adapter.
- Docker foundation, CI for Python 3.11/3.12, and tests for the core primitives.

## Still pending
- Telegram Bot API admin bot; MTProto login, 2FA, connect/disconnect/revoke, and device audit.
- Background scheduler worker, job locking, retries, cancellation, and graceful shutdown.
- Permission/RBAC layer and authenticated operational dashboard.
- AI supervisor, intent detection, action planner, and approval for consequential actions.
- Telegram event integrations, profile/message automation, and complete Persian/English RTL/LTR UI.
- Security/dependency audit and clean-install verification.

See docs/ROADMAP.md and docs/ARCHITECTURE.md.

## Requirements and local run
- Python 3.11 or 3.12; pip and a virtual environment.
- Clone this repository, check out feat/project-foundation, then install with: python -m pip install -e ".[dev]"
- Start with: uvicorn app.main:app --host 127.0.0.1 --port 8000
- Dashboard: http://127.0.0.1:8000 ; API docs: http://127.0.0.1:8000/api/docs
- Tests: python -m compileall -q app tests && python -m pytest

## Module boundaries
- Automation engine: evaluates typed rules and delegates to explicitly registered handlers; it does not send Telegram messages itself.
- Scheduler store: persists jobs but does not run a worker or execute due jobs yet.
- Session vault: encrypts serialized bytes; the key must remain outside the repository. This is not Telegram login or session revocation.
- AI adapter: Ollama local HTTP support and safe failure results; AI does not directly execute sensitive account actions.

## Deployment and safety
The default Compose setup binds to loopback. Do not expose this development foundation publicly before authentication, authorization, worker controls, and production hardening are implemented. Operate only accounts and channels you are authorized to manage. Do not spam or bypass Telegram limits. Never send session data or encryption keys to an AI provider.

## Security and license
Review SECURITY.md and CONTRIBUTING.md. MIT License. Donations may optionally support development but never unlock functionality.

Maintainer: MohZarg — https://github.com/MohZarg
Repository: https://github.com/MohZarg/MohZarg-Telegram-Self-AI
