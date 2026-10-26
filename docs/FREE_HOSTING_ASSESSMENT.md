# Free Hosting Assessment

**Decision: no provider selected. No infrastructure was provisioned. This assessment is for private development/staging only, not production.**

## Requirements that matter for GhYiAb Self

The current repository uses FastAPI, a scheduler/worker foundation, SQLite, and an encrypted session vault. A viable target must be evaluated against all of these, not just whether it can serve HTTP:

- Persistent writable storage for SQLite and encrypted session data, or a deliberate move to a managed database with tested migrations.
- A continuously running worker if scheduled jobs must execute on time.
- Controlled restart/shutdown and a way to inspect logs.
- Secure runtime secrets that never enter Git, build logs, images, or chat.
- Network egress to the Telegram API when integration is enabled.
- Private-by-default access until dashboard authentication/RBAC and operational controls are implemented.

## Shortlist for a $0-only phase

| Option | What the official documentation says | Suitability for current project |
|---|---|---|
| **Render Free Web Service** | Free web services spin down after 15 minutes without inbound traffic; local filesystem changes are lost on restart, redeploy, or spin-down; free services cannot attach persistent disks. Free Postgres is limited and expires after 30 days. | Suitable only for a disposable demo that stores no durable local state and does not require an always-on worker. **Not suitable for the current SQLite/session workload as-is.** |
| **Oracle Cloud Always Free Compute** | Oracle documents eligible Always Free VM shapes, including up to two AMD micro VMs and an Arm allocation within stated monthly resource limits. Instances must be created in the tenancy's home region; capacity errors can occur. | Potentially the closest $0 option for a self-managed private test VM if the account and home-region capacity permit it. Requires Linux administration, firewalling, patching, backups, monitoring, and careful billing/usage controls. Not a guaranteed capacity or production SLA. |
| **Local development / Docker** | Uses existing local hardware; no cloud account or public endpoint required. | **Safest immediate zero-cost option** while authentication, worker lifecycle, and persistence behavior are being completed. Not remotely available unless separately secured. |
| **Other free web-app tiers** | Free allowances vary and may sleep, expire, omit persistent disks, or require a paid plan/credit after trial. | Do not select without rechecking current official limits for persistent storage, long-running workers, and billing. |

Official references (recheck before any account or deployment decision):
- Render free services and filesystem limitations: https://render.com/docs/free
- Oracle Always Free resources and home-region/capacity limitations: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

## Recommended path under the $0 constraint

1. **Now:** keep development and CI on GitHub and use local Docker for runtime smoke tests. Do not create a public deployment.
2. **If remote testing is necessary:** evaluate Oracle Always Free as a candidate for a private VM only after checking account eligibility, home-region capacity, and billing controls. Do not assume it is available until the console confirms it.
3. **Do not use Render Free for the current stateful deployment** unless the architecture is changed so that no durable state is written to its ephemeral filesystem and no always-on worker is required. A temporary demo must contain no real Telegram sessions or sensitive user data.
4. **Do not bypass idle limits** with keep-alive pings. Design to provider terms and accept sleep where applicable.
5. **Do not enable Telegram automation** on a public or unprotected instance. Authentication/RBAC, command authorization, lifecycle controls, production settings validation, and secret provisioning remain release gates.

## Self-managed vs managed

- **Self-managed free VM:** potentially supports persistent storage and a long-running worker, but transfers security and operations responsibility to the project operator. It is only appropriate for a private test after firewall and SSH hardening.
- **Managed free web service:** reduces server administration but commonly imposes sleep, ephemeral storage, and worker limits. It is useful for stateless demos, not automatically for this project's current architecture.
- **Local Docker:** least external risk and no hosting cost while core security and lifecycle work continues.

## Acceptance gates before any remote test

- [ ] Confirm provider account eligibility and exact free resource quotas in its console.
- [ ] Configure budget alerts/quotas where supported; understand any billing exposure before adding a payment method.
- [ ] Keep inbound access private; do not expose port 8000 or unauthenticated API docs.
- [ ] Store secrets through a secure runtime mechanism, never in Git or container image layers.
- [ ] Verify persistence and restore behavior with disposable test data.
- [ ] Confirm graceful restart, worker cancellation, health checks, and log redaction.
- [ ] Keep real Telegram sessions disabled until auth/RBAC and integration safety checks pass.

This document does not authorize deployment and does not claim that any free resource has been provisioned.
