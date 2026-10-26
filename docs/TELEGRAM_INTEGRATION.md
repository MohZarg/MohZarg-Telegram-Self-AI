# Telegram Integration Boundary — Bot API + MTProto

## User-selected target

The planned product supports both:
- **Bot API** for an administrative bot and bot-authorized workflows.
- **MTProto** for a user-authorized Telegram account session, including explicit login and 2FA handling.

The initial Bot API adapter is implemented as a restricted client with `getMe` and plain-text send to a single configured admin chat. It does not poll updates, register webhooks, start at application boot, or provide a command/authorization system. The standalone `app.telegram.config` module validates mode and required environment values, but configuration is not wired into application startup. MTProto is not implemented.

## Separation of responsibilities

### Bot API adapter
- Owns bot-token configuration, webhook or polling lifecycle, update parsing, and bot API error mapping.
- Restricts administrative commands to configured, verified Telegram user/chat IDs.
- Uses explicit command allowlists and rate limits.
- Never treats a bot token as an MTProto user session.
- Current client only provides `get_me()` and `send_admin_message(text)`; the latter has no caller-supplied chat ID and always targets the configured admin chat.

### MTProto adapter
- Owns API ID/hash configuration, user login, verification code and 2FA flow, session persistence, disconnect/revoke operations, and authorized device status where supported.
- Requires a deliberate user action to start login and to approve consequential operations.
- Encrypts session material at rest; encryption keys stay in a secret manager or protected runtime environment.
- Never logs, returns, commits, or sends session material or API hashes to an AI provider.

### Shared application services
- Convert validated requests into typed domain commands.
- Apply authorization, rate limits, audit logging, cancellation, and approval policy before execution.
- Keep AI in the proposal layer; AI output is not directly executable.
- Make external side-effect handlers idempotent where possible and record operation outcomes without storing secrets.

## Configuration contract (names only; values stay outside Git)

- `TELEGRAM_API_ID`: MTProto application ID from the official Telegram developer portal.
- `TELEGRAM_API_HASH`: MTProto application hash; secret.
- `TELEGRAM_ADMIN_BOT_TOKEN`: Bot API token; secret.
- `TELEGRAM_ADMIN_CHAT_ID`: expected admin chat/user identifier; must be validated and allowlisted.
- `SESSION_ENCRYPTION_KEY`: dedicated Fernet-compatible key managed outside Git, not the same as an API credential.
- `TELEGRAM_MODE`: `disabled`, `bot`, `mtproto`, or `both`. The standalone validator supports these values; clients are not yet wired into application startup.

Do not paste these values into issues, pull requests, chat messages, or source files. Configure them directly in the runtime secret manager after the relevant implementation is ready.

## Required implementation sequence

1. [x] Add typed configuration and fail-closed validation for each selected mode.
2. [x] Add a restricted Bot API client and fake-transport tests.
3. [ ] Add Bot API update polling/webhook, explicit admin identity verification, command allowlist, and lifecycle management.
4. [ ] Add an MTProto client behind a separate adapter interface, plus login/2FA state-machine tests.
5. [ ] Add explicit connect/disconnect/revoke controls and device audit where supported.
6. [ ] Add secret/session encryption, rotation and deletion behavior, and redacted audit events.
7. [ ] Add Telegram-aware flood-wait handling, rate limits, cancellation, retries, and idempotency safeguards.
8. [ ] Add integration tests using a dedicated bot and test account; do not use production credentials in CI.
9. [ ] Connect both adapters to the scheduler only after authorization and policy gates are in place.

## Explicitly out of scope

- Spam, unsolicited bulk messaging, rate-limit evasion, or automated engagement (auto-like/follow/comment).
- Logging or exporting authentication codes, passwords, API hashes, bot tokens, or session strings.
- Letting an AI model execute account actions without a policy check and required user approval.

## Current blockers

The actual GhYiAb V2 repository, Master Spec, STATUS, and implementation-gap report have not been identified or provided. The URL currently supplied points to this Self repository, not a separately identified V2 codebase. Therefore, no internal endpoint, database schema, bot contract, account model, wallet/order logic, or existing adapter can safely be assumed or integrated yet.
