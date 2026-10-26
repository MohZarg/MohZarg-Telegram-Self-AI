# Cloud Deployment Readiness

## Current decision

**Not production-ready for public internet exposure.** A single-admin Basic-auth baseline and per-process login throttle now protect administrative routes in production mode, but RBAC, shared throttling, CSRF/session protections where applicable, production secret validation, and full operational hardening remain incomplete. The Compose profile binds the host port to loopback. Do not publish port 8000 directly.

## Safe next-step deployment profile

1. Use a dedicated Linux VM/container host and a non-root runtime.
2. Keep the application bound to `127.0.0.1:8000`; put a TLS reverse proxy in front only after authentication and authorization are implemented.
3. Store credentials in the host's secret manager or deployment platform's encrypted secrets. Do not commit `.env`, session files, database files, or encryption keys.
4. Use persistent, access-restricted storage for SQLite only for single-instance evaluation. For multi-instance production, first design and test a shared database and distributed job-lease model.
5. Restrict inbound network access to SSH from trusted IPs and HTTPS through the proxy. Do not expose API docs or operational controls publicly.
6. Enable host/container updates, log rotation, backups, restore drills, uptime monitoring, and an incident/key-rotation procedure.
7. Run dependency/security checks and clean-install verification before accepting real Telegram sessions.

## Release blockers

- RBAC, CSRF/session protections where applicable, shared rate limiting for multi-worker deployments, and trusted proxy configuration.
- Explicit production configuration validation and secure secret provisioning.
- Production database/migration and backup/recovery plan.
- Readiness checks, operational alerting, and deployment-level graceful-shutdown verification (worker entry point exists).
- End-to-end tests and dependency/security audit.
- HTTPS/reverse-proxy configuration and deployment-specific network policy.
- Operational alerting and documented incident response.

## Deployment acceptance checklist

- [ ] Authentication and authorization tests pass.
- [ ] Public routes are reviewed; docs and admin actions are not anonymously accessible.
- [ ] No secrets appear in Git history, build logs, API responses, or application logs.
- [ ] Persistent data location and backup/restore are verified in the target deployment.
- [ ] Container runs as non-root and has least-privilege filesystem/network access.
- [ ] TLS, firewall, health checks, log retention, and restart behavior are verified.
- [ ] Clean deployment and rollback have been tested.
- [ ] Telegram integration tests run with a dedicated test account/bot and explicit consent.

This document is a deployment gate, not a claim that a cloud instance has been provisioned. The optional Compose worker requires `TELEGRAM_MODE=bot` and valid host-provided admin bot credentials; keep it stopped until these are configured. No cloud provider, account, domain, DNS, TLS certificate, or deployment secret was supplied in this task.
