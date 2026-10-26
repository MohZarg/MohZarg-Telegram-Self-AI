# Cloud Provider Evaluation

**Status: evaluation only — no provider selected and no infrastructure provisioned.**

This document narrows the first hosting decision for GhYiAb Self. It is not a deployment authorization. Do not add credentials, API tokens, private keys, session files, or secret values to GitHub or this document.

## Workload and constraints

- Python FastAPI application with a scheduler/worker foundation.
- Current data layer is SQLite; treat it as single-instance only until concurrency, backup/restore, and migration behavior are verified.
- Telegram integration is incomplete; do not accept real user sessions yet.
- No domain is available. A domain is not required for a private staging smoke test, but public HTTPS deployment requires a domain or an explicitly chosen platform URL and proper access controls.
- The dashboard currently lacks authentication/RBAC. Public exposure is blocked independently of provider choice.
- Prefer an EU region only if that matches the operator's data-residency and latency requirements; confirm applicable legal obligations before selecting a region.

## Shortlist

| Option | Why consider it | Trade-offs / checks | Fit for first private staging |
|---|---|---|---|
| **Hetzner Cloud VM** | Straightforward Linux VM; official docs list EU locations including Falkenstein, Nuremberg and Helsinki, plus firewalls, volumes, backups and snapshots. | Self-managed OS patching, firewall, monitoring, restore drills and secret delivery. Backups/snapshots do not include attached volumes, so verify the exact persistence layout. | **Leading low-complexity candidate** if self-management is acceptable. |
| **Scaleway Instance** | EU cloud regions and a Secret Manager service with regional secret storage and versioning. | Confirm the selected instance's persistent storage, backup pricing, operational workflow and secret-manager access model before committing. | Strong alternative if managed secret handling is a priority. |
| **DigitalOcean Droplet** | VM-based deployment with documented backup and restore workflows; approachable operational model. | Verify current region, total cost (VM, backups, storage, bandwidth), and how runtime secrets will be delivered. | Reasonable alternative if the operator prefers its workflow/support ecosystem. |
| **Managed application/container platform** | Can reduce OS maintenance and simplify deploys. | Must explicitly support a persistent writable volume, a long-running worker, reliable restart/shutdown, outbound Telegram API traffic, and secure secrets. Ephemeral filesystem alone is not acceptable for SQLite/session data. | Defer until the worker and persistence architecture are defined. |

Official references:
- Hetzner Cloud locations: https://docs.hetzner.com/cloud/general/locations/
- Hetzner backup/snapshot scope: https://docs.hetzner.com/cloud/servers/backups-snapshots/overview/
- Scaleway Secret Manager: https://www.scaleway.com/en/docs/secret-manager/quickstart/
- DigitalOcean backup/restore: https://docs.digitalocean.com/products/backups/how-to/create-and-restore/

## Recommendation

Start with **Hetzner Cloud as the first candidate to price-check**, not as an approved or selected provider. Compare it against Scaleway before purchase. Select the provider only after confirming:
1. Monthly budget and whether VAT/tax must be included.
2. Required data region and jurisdiction.
3. Persistent storage and a tested backup/restore path for SQLite.
4. Secret delivery without putting secrets in Git, chat, image layers, or logs.
5. Inbound firewall policy, SSH access model, patching, monitoring and recovery ownership.
6. Availability of an isolated staging environment and a clean teardown path.

No current price is stated here; prices, quotas, terms, and feature availability must be checked in each provider's live calculator/console immediately before purchase.

## Deployment gates — still mandatory

Provider choice does **not** remove these release blockers:
- Add and test authentication, authorization/RBAC, rate limiting, and protection for dashboard/API docs.
- Validate production settings fail-closed.
- Separate web and worker lifecycle; implement graceful shutdown and readiness checks.
- Define session/key handling, rotation, backups, restore drills, audit retention and incident response.
- Run dependency/security checks and clean-install/container verification.
- Keep the app private until all public-exposure acceptance criteria in [Cloud Deployment Readiness](CLOUD_DEPLOYMENT.md) pass.

## Operator decision required

The following decisions cannot be inferred safely:
- Monthly hosting budget.
- Preferred data region/jurisdiction.
- Whether the operator is willing to maintain a Linux VM.
- Whether to use a provider-managed secret service or a host-level secret mechanism.

Until those are known, keep the provider **unselected** and do not provision paid resources.
