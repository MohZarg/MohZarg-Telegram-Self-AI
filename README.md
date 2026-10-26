# MohZarg Telegram Self AI

**Free and open-source self-hosted AI assistant and Telegram automation project.**

Telegram Self AI is being built as a self-hosted toolkit combining a web dashboard, Telegram administration bot, authorized Telegram account integration (MTProto), AI assistance, channel content workflows, automation, scheduling, monitoring, and Persian/English support.

> **Development status: Early foundation.** The initial web dashboard and health/status API are implemented. Telegram, MTProto, AI, content engine, scheduler, and automation integrations are planned and are not yet implemented.

## Principles

- Free and open source, with the complete source available publicly.
- No paid edition, license key, mandatory subscription, paywall, or artificial feature restrictions.
- Personal and commercial use permitted under the [MIT License](LICENSE).
- Optional donations only. Donations never unlock features or affect functionality.
- Self-hosted configuration and user control.
- Secure handling of Telegram credentials, MTProto sessions, AI keys, and private data.

## Current features

- [x] Minimal web status dashboard
- [x] Health endpoint at /api/health
- [x] Non-sensitive feature status at /api/status
- [x] Basic security response headers
- [x] Environment settings validation for the application port
- [x] Docker image runs as a non-root user
- [x] GitHub Actions CI for Python 3.11 and 3.12
- [x] Initial automated tests
- [ ] Authenticated operational dashboard
- [ ] Telegram admin bot
- [ ] Authorized Telegram account integration via MTProto
- [ ] AI assistant with configurable provider
- [ ] AI-assisted channel content creation and review
- [ ] Automation engine, scheduler, and job queue
- [ ] Full FA/EN localization and RTL/LTR support

See [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requirements

- Python 3.11 or 3.12
- pip and a virtual environment
- Docker and Docker Compose are optional

## Run locally

Clone the repository and switch to the development branch while the initial implementation is being reviewed:

```bash
git clone https://github.com/MohZarg/MohZarg-Telegram-Self-AI.git
cd MohZarg-Telegram-Self-AI
git checkout feat/project-foundation
python -m venv .venv
```

Activate the virtual environment:

- Linux/macOS: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Install the app and development dependencies, then start the server:

```bash
python -m pip install -e ".[dev]"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the dashboard and http://127.0.0.1:8000/api/docs for the API documentation.

Health check:

```bash
python -c "from urllib.request import urlopen; print(urlopen('http://127.0.0.1:8000/api/health').read().decode())"
```

## Run tests

```bash
python -m compileall -q app tests
python -m pytest
```

GitHub Actions runs these checks on pushes to the main and feature branches and on pull requests.

## Docker

Create a local environment file first:

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env`. Then run:

```bash
docker compose up --build
```

The default Compose configuration binds the service to 127.0.0.1 on the host. Do not expose this development foundation publicly: authenticated access controls and production hardening are still required before adding operational features.

## Configuration

Copy `.env.example` to `.env` for local use. Populate only the values needed by the features you have configured. Never commit `.env`, API hashes, bot tokens, AI keys, Telegram sessions, databases, backups, or logs containing private data.

## Telegram account and safety

Use only accounts and channels you own or are authorized to operate. Do not use this project for unsolicited bulk messaging, spam, unauthorized access, or bypassing Telegram restrictions. MTProto session files are credentials: keep them private, restrict filesystem access, and never upload them to GitHub.

## Optional support

### ❤️ Support Development

This project is intended to remain free and open source. If it helps you, you may optionally support development.

**Donate:** Donation link to be configured.

Donations are optional and do not unlock features. No donation URL has been configured yet.

## Security and contributions

Review [SECURITY.md](SECURITY.md) before reporting security issues, and [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Do not post credentials, session files, or exploitable vulnerability details in public issues.

## License

Released under the [MIT License](LICENSE), allowing personal and commercial use, modification, and redistribution subject to its terms.

---

**Maintainer:** [MohZarg](https://github.com/MohZarg)  
**Repository:** [MohZarg-Telegram-Self-AI](https://github.com/MohZarg/MohZarg-Telegram-Self-AI)
