# Telegram Self AI — Roadmap

A checklist item is complete only when code exists and relevant automated checks pass.

## Phase 0 — Repository foundation
- [x] Public repository and write access confirmed.
- [x] Feature branch and initial documentation/configuration established.
- [x] FastAPI dashboard, health/status endpoints, Docker, and CI added.
- [x] Basic test suite passes on Python 3.11 and 3.12 in CI.

## Phase 1 — Core primitives
- [x] Typed declarative automation rule schema and allowlisted action engine.
- [x] SQLite one-shot job store with due-job lookup and lifecycle states.
- [x] Fernet-encrypted session-byte vault with restrictive file permissions.
- [x] Provider-independent AI interface, disabled fallback, and Ollama adapter.
- [x] Unit tests for these primitives added; CI confirmation pending after latest commit.
- [ ] Structured audit events with redaction and durable storage.
- [ ] Authentication, RBAC, rate limiting, and CSRF-safe dashboard operations.

## Phase 2 — Telegram integration
- [ ] Admin bot via Telegram Bot API.
- [ ] User-authorized MTProto client and login/2FA flow.
- [ ] Session connect/disconnect/revoke/status lifecycle and device audit.
- [ ] Telegram-aware rate limits, flood-wait handling, retries, and cancellation.
- [ ] Profile scheduling (bio/name) with validation and user-controlled presets.
- [ ] Message rules with allowlists/denylists, quiet hours, and safe opt-in replies.

## Phase 3 — AI and content
- [ ] Provider configuration and tested fallback chain (local first where configured).
- [ ] Intent detection and action planner separated from execution.
- [ ] Policy/permission gate before every consequential action.
- [ ] Message summarization, suggested replies, limited user-controlled memory, and personal FAQ.
- [ ] Content drafting, review, approval, and compliant publishing adapters.

## Phase 4 — Automation and operations
- [ ] Worker loop, job claiming/locking, retries, dead-letter handling, cancellation, and graceful shutdown.
- [ ] Event bus and trigger integrations for message/profile events supported by the selected API.
- [ ] Monitoring, redacted logs, audit trail, and operational alerts.
- [ ] Safe file/media batch tools only where Telegram APIs support the requested operation.

## Phase 5 — GhYiAb platform integration (separate confirmed repository/source required)
- [ ] Audit the actual GhYiAb V2 repository and its Master Spec, STATUS, and implementation-gap report.
- [ ] Reuse existing RBAC, wallet/orders, referrals, i18n, support, 3x-ui, backup, and provider adapters where present.
- [ ] Define API contracts between GhYiAb Bot, Web, Self, AI, Commerce, and Automation.
- [ ] Avoid duplicating platform logic or inventing undocumented APIs.

## Phase 6 — Web, localization, commerce, advertising
- [ ] Authenticated dashboard and account-management UI.
- [ ] Complete Persian/English localization and RTL/LTR behavior.
- [ ] Optional product/tier metadata, wallet/orders/referral adapters only after platform audit.
- [ ] Campaign creation, AI review, scheduling, consent-aware audience selection, and analytics.
- [ ] Use official platform APIs; no auto-like/follow/comment or spam-like broadcast automation.

## Phase 7 — Release readiness
- [ ] Run all tests and dependency/security audits.
- [ ] Verify clean local and Docker installation.
- [ ] Review Git history for secrets and verify ignore rules.
- [ ] Document backup/recovery, limitations, deployment profiles, and key rotation.
- [ ] Publish a versioned release only after integration tests and security review.

## Non-negotiable principles
- Free and open source under MIT; personal and commercial use permitted.
- No paywall, license key, mandatory subscription, or feature gating.
- Donations remain optional.
- Never publish credentials, sessions, databases, backups, or private data.
- Automation is for authorized use and must not spam or bypass platform limits.
