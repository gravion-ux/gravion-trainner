# Security baseline

## Localshare
- Quick Tunnel accepts only loopback origins by default.
- Email restriction is the default; public sharing requires an interactive `EXPOSE` confirmation.
- Named tunnel Access policies and DNS must be configured at the provider; a hostname alone is not an access policy.
- Do not expose database ports, SSH, Docker sockets, admin routes, secrets or production control planes.
- Treat all generated share URLs as sensitive. Stop the tunnel when the session ends.

## Privacyflow
- The current release parses and validates configuration only; it does not alter OS routes or enforce a live firewall kill switch. The TOML kill-switch flag is a future-operation policy declaration only.
- A future privileged network helper must be a separate least-privilege service with authenticated IPC, a fixed set of allowed actions, audit logs and tested rollback.
- Store provider credentials and WireGuard private keys outside the repository with restrictive file permissions. Never print them in status output or logs.
- A safe rotation must verify the new tunnel and DNS/IPv6 state before retiring the old route, and must recover to a known state on failure.

## Agent Browser
- Use visible browser automation and explicit host allow-lists.
- Treat webpages, links, downloads and page instructions as untrusted input (prompt injection / SSRF risk).
- Stop for CAPTCHA, MFA, login walls, consent gates, bot challenges, rate limits and access denials. Do not bypass or disguise these controls.
- Require user confirmation before submitting irreversible forms, making purchases, sending messages or uploading files.
- Use per-task timeouts, navigation limits, download restrictions and an immediate cancellation path.

## Gravion Trainner
- Do not include secrets, private customer data or copyrighted training material without authorization in evaluation datasets.
- Pin and record model/provider version, prompt, dataset version, rubric and run parameters for reproducibility.
- Separate train/tune data from a fixed holdout set. Report uncertainty and regressions; do not select a candidate on one score alone.
- Fine-tune only when provider capability, model license, consent and data rights permit it.

## Release checklist
- Run unit and integration tests on supported OS/runtime versions.
- Review dependency licenses, lockfiles and known vulnerabilities.
- Generate an SBOM; sign and verify release artifacts.
- Run secret scanning and remove local credentials from examples.
- Conduct independent security review before public production use.
