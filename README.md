# MohZarg Telegram Self AI

**Free and open-source self-hosted AI assistant and Telegram automation project.**

Telegram Self AI is being built as a self-hosted toolkit combining a web dashboard, Telegram administration bot, authorized Telegram account integration (MTProto), AI assistance, channel content workflows, automation, scheduling, monitoring, and Persian/English support.

> **Development status: Early foundation.** This branch establishes project policies and planning documents. The application runtime and user-facing features are not implemented yet; planned capabilities below must not be considered available until code and tests are added.

## Principles

- Free and open source, with the complete source available publicly.
- No paid edition, license key, mandatory subscription, paywall, or artificial feature restrictions.
- Personal and commercial use permitted under the [MIT License](LICENSE).
- Optional donations only. Donations never unlock features or affect functionality.
- Self-hosted configuration and user control.
- Secure handling of Telegram credentials, MTProto sessions, AI keys, and private data.

## Planned capabilities

- [ ] Web dashboard
- [ ] Telegram admin bot
- [ ] Authorized Telegram account integration via MTProto
- [ ] AI assistant with configurable provider
- [ ] AI-assisted channel content creation and review
- [ ] Automation engine
- [ ] Scheduler and job queue
- [ ] Monitoring and health checks
- [ ] Persian and English interface (FA/EN), including RTL/LTR
- [ ] Docker-based deployment
- [ ] Automated tests and CI workflows

See [docs/ROADMAP.md](docs/ROADMAP.md) for implementation phases and acceptance goals.

## Current setup

The application runtime is not implemented yet. Installation and run commands will be added after the implementation stack is selected and an executable application has been implemented and tested.

### Configuration template

When local development begins, copy `.env.example` to `.env` and populate credentials locally. Never commit `.env` or real secrets.

## Telegram account and safety

Use only accounts and channels you own or are authorized to operate. Do not use this project for unsolicited bulk messaging, spam, unauthorized access, or bypassing Telegram restrictions. MTProto session files are credentials: keep them private, restrict filesystem access, and never upload them to GitHub.

## Optional support

### ❤️ Support Development

This project is intended to remain free and open source. If it helps you, you may optionally support development.

**Donate:** Donation link to be configured.

Donations are optional and do not unlock features. No donation URL has been configured yet.

## Security

Please review [SECURITY.md](SECURITY.md). Do not post tokens, session files, or exploitable vulnerability details in public issues.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

Released under the [MIT License](LICENSE), allowing personal and commercial use, modification, and redistribution subject to its terms.

---

**Maintainer:** [MohZarg](https://github.com/MohZarg)  
**Repository:** [MohZarg-Telegram-Self-AI](https://github.com/MohZarg/MohZarg-Telegram-Self-AI)
