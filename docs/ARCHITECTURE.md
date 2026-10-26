# Architecture — Initial Implementation

## Current executable slice

- **FastAPI application** in app/main.py serves a small local dashboard and JSON health/status endpoints.
- **Settings loader** in app/config.py validates basic environment configuration without printing or returning credentials.
- **Tests** in tests/test_app.py cover the health API, security headers, status flags, dashboard response, donation URL validation, and port validation.
- **Container** in Dockerfile and docker-compose.yml runs the web service as a non-root user and binds the host port to loopback by default.
- **CI** in .github/workflows/ci.yml runs compile checks and tests on Python 3.11 and 3.12.

## Planned module boundaries

Future modules should be introduced behind small interfaces rather than coupled directly to HTTP handlers:

- telegram/: Bot API and user-authorized MTProto clients; secure session lifecycle.
- ai/: provider interface, model configuration, prompt handling, and redaction.
- content/: draft generation, review, and explicit publishing confirmation.
- automation/: validated rules, execution records, cancellation, and permission checks.
- scheduler/: durable jobs, retry policy, and safe shutdown.
- monitoring/: health, metrics, and redacted diagnostics.
- dashboard/: authenticated configuration and operation views.

These modules are planned, not implemented. No credentials, Telegram session files, or provider keys belong in the repository. Production deployment must add authentication and authorization before exposing operational controls beyond a trusted local environment.
