# Release Status — GhYiAb Self

**Assessment date:** 2026-10-26  
**Release state:** Private development/staging only. Not approved for public production deployment.  
**Cloud state:** No provider selected; no server, domain, DNS, TLS certificate, or deployment secrets provisioned.

## Verified in GitHub CI

- Python source compiles and unit tests pass on Python 3.11 and 3.12.
- Docker Compose configuration validates and the Docker image builds.
- Container smoke test confirms /api/health is reachable and /api/status requires valid production credentials.
- Runtime dependency audit passes after upgrading the cryptography constraint to >=50.0.0,<51.0.
- SQLite backup/restore tests verify database integrity, job preservation, atomic replacement behavior, and explicit overwrite protection.
- Telegram polling tests use fake transports and validate the exact admin user/chat allowlist. No real bot token or live Telegram account was used in CI.

Relevant merged work:
- [PR #8 — Admin login throttling](https://github.com/MohZarg/MohZarg-Telegram-Self-AI/pull/8)
- [PR #9 — Restricted Telegram Bot API polling](https://github.com/MohZarg/MohZarg-Telegram-Self-AI/pull/9)
- [PR #10 — Worker operations and SQLite backup/restore](https://github.com/MohZarg/MohZarg-Telegram-Self-AI/pull/10)
- [PR #11 — Production credential checks and release CI](https://github.com/MohZarg/MohZarg-Telegram-Self-AI/pull/11)

## Implemented scope

- Production HTTP Basic authentication for administrative routes; weak/malformed credentials fail closed.
- Conservative failed-login throttling: five failures in a 60-second window trigger a 60-second cooldown. This limiter is per process only.
- Bot API startup identity check and restricted long polling. Only /help, /start, and /status are accepted, and only from the configured user in the configured chat.
- Optional standalone scheduler worker with graceful SIGINT/SIGTERM shutdown and one explicit admin-notification job handler.
- Persistent named Compose volume, container healthcheck, and SQLite backup/restore CLI.
- Repository and Docker build-context ignore rules exclude local secrets, runtime databases, backups, and session files.

## Release blockers

1. RBAC and shared/distributed login throttling for multi-worker deployments.
2. Trusted TLS reverse proxy, firewall review, and deployment-specific secret provisioning.
3. Real Telegram Bot API validation with a dedicated test bot/account and explicit authorization. Keep TELEGRAM_MODE=disabled until ready.
4. MTProto, login/2FA, session lifecycle, and revocation are not implemented; mtproto and both modes fail closed.
5. Target-host backup/restore drill, key rotation, incident response, and operational alerting.
6. Full Git-history secret review and local-host clean-install verification.
7. A deliberate provider decision. The zero-cost recommendation remains local Docker for now; Oracle Always Free is only a candidate for private staging if the account and region have capacity. No remote resource is guaranteed or provisioned.

## Safe local verification

```bash
cp .env.example .env
python -m pip install -e ".[dev]"
python -m compileall -q app tests
python -m pytest
```

Docker validation is run in CI. For local Compose use, keep the published host port bound to loopback and do not expose port 8000 publicly. Restore only while the app and worker are stopped. Never commit .env, databases, backups, Telegram sessions, or encryption keys.

This document records test evidence and remaining blockers. It is not a production approval or a claim that a cloud deployment exists.
