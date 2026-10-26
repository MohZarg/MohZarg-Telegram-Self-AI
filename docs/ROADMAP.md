# GhYiAb Self — Roadmap

A checklist item is complete only when code exists and relevant automated checks pass.

## Phase 0 — Repository foundation
- [x] Public repository and write access confirmed.
- [x] Feature branch, docs, configuration, Docker, and CI established.
- [x] FastAPI dashboard and health/status endpoints implemented.

## Phase 1 — Core primitives
- [x] Typed automation rule schema and allowlisted action engine.
- [x] SQLite durable job store with atomic claiming, bounded retries, and stale-lease recovery.
- [x] Fernet-encrypted session-byte vault with restrictive file permissions.
- [x] Provider-independent AI interface, disabled fallback, and Ollama adapter.
- [x] SQLite audit trail with conservative secret redaction.
- [x] Unit tests for core primitives added; latest PR CI passed before merge.
- [ ] Structured logging, RBAC, authentication, rate limiting, and protected dashboard operations.

## Phase 2 — Telegram integration (Bot API + MTProto)
- [x] Document adapter responsibilities, secret boundaries, and implementation order.
- [ ] Add typed configuration and fail-closed validation for selected Telegram modes.
- [ ] Add Bot API adapter with admin identity allowlist and fake-client tests.
- [ ] Add user-authorized MTProto adapter with login/2FA state-machine tests.
- [ ] Add session connect/disconnect/revoke/status and device audit where supported.
- [ ] Add Telegram-aware rate limits, flood-wait handling, retries, and cancellation.
- [ ] Add profile scheduling and message rules with quiet hours, allowlists/denylists, and explicit opt-in.

## Phase 3 — Cloud security and operations
- [x] Document why public exposure is blocked and define deployment acceptance criteria.
- [ ] Authentication, RBAC, protected operational routes, and rate limiting.
- [ ] Production settings validation and managed secret provisioning.
- [ ] Separate web/worker lifecycle, graceful shutdown, readiness checks, and operational alerts.
- [ ] Persistent storage, backup/restore, rollback, and multi-instance strategy.

## Phase 4 — AI and content
- [ ] Configurable provider chain with local-first option and graceful degradation.
- [ ] Intent detection and action planner separated from execution.
- [ ] Policy/permission gate before consequential actions.
- [ ] Message summaries, suggested replies, controlled memory, and personal FAQ.
- [ ] Content drafting, review, approval, and compliant publishing adapters.

## Phase 5 — Automation and operations
- [x] Synchronous worker loop, job claiming/locking, bounded retries, and expired-lease recovery.
- [ ] Worker process packaging, dead-letter review tools, cancellation, and graceful shutdown.
- [ ] Event bus and triggers for events supported by the selected Telegram API.
- [ ] Monitoring, redacted logs, audit review, and operational alerts.
- [ ] File/media tools only where official APIs support the operation.

## Phase 6 — GhYiAb V2 platform integration
- [ ] Identify and obtain access to the actual GhYiAb V2 repository.
- [ ] Review Master Spec, STATUS, and implementation-gap report.
- [ ] Reuse existing RBAC, wallet/orders, referrals, i18n, support, 3x-ui, backup, and provider adapters only if confirmed in source.
- [ ] Define API contracts among GhYiAb Bot, Web, Self, AI, Commerce, and Automation based on source code.
- [ ] Avoid duplicated platform logic and undocumented endpoints.

## Phase 7 — Web, localization, commerce, advertising
- [ ] Authenticated dashboard and account-management UI.
- [ ] Complete Persian/English localization and RTL/LTR behavior.
- [ ] Optional product/tier metadata, wallet/order/referral adapters after platform audit.
- [ ] Campaign drafting, review, scheduling, consent-aware audience selection, and analytics.
- [ ] Official platform APIs only; no auto-like/follow/comment or spam-like broadcasts.

## Phase 8 — Release readiness
- [ ] Run full tests and dependency/security audits.
- [ ] Verify clean local and Docker installation.
- [ ] Review Git history and ignore rules for secrets.
- [ ] Document backup/recovery, limitations, deployment profiles, and key rotation.
- [ ] Publish a versioned release only after integration tests and security review.

## Non-negotiable principles
- Free and open source under MIT; personal and commercial use permitted.
- No paywall, license key, mandatory subscription, or artificial feature gating.
- Optional donations only.
- Never publish credentials, sessions, databases, backups, or private data.
- Automation is for authorized use and must not spam or bypass platform limits.
