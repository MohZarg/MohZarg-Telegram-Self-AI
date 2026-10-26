# Security Policy

## Scope

Telegram Self AI is intended for authorized use of the operator's own Telegram account, bots, and data. Do not use it for spam, unsolicited bulk messaging, evading Telegram limits, or accessing accounts or data without permission.

## Reporting a vulnerability

Please do not publish credentials, session files, personal data, or an exploitable vulnerability in a public issue. Contact the repository maintainer privately through the contact options on the MohZarg GitHub profile and include:
- A clear description and impact
- Steps to reproduce, using a safe test environment
- Relevant logs with secrets and personal data removed

A private security contact has not yet been configured. Until one is available, avoid including sensitive details in public reports.

## Secrets and session data

Never commit:
- Telegram API hashes, bot tokens, AI provider keys, passwords, cookies, or private keys
- Telegram MTProto session files or exported authentication data
- Production databases, backups, user data, or logs containing sensitive information

If a secret is exposed, revoke or rotate it immediately. Removing a secret in a later commit does not remove it from Git history.
