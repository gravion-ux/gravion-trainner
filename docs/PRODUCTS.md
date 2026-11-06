# Product portfolio

## 01 — Localshare

**Purpose:** Let a developer share a web app running on their own machine by sending another person a URL, without first deploying the project.

**Current MVP:** Node.js CLI that validates a loopback origin and starts either a Cloudflare Quick Tunnel or a configured Named Tunnel. It includes local health checks, tests, a demo app and local/cloud/VPS deployment examples.

**Modes:**
- **Quick Tunnel:** temporary `trycloudflare.com` link for demos, webhook testing and teammate previews.
- **Named Tunnel:** stable hostname routed to an origin on a laptop, workstation or VPS; requires a domain, tunnel credentials/configuration and suitable access policy.
- **Direct VPS hosting:** deploy the app itself to a cloud VM/container and put a reverse proxy/TLS layer in front. The sample deployment uses Docker Compose + Caddy.

**Branding:** The demo project includes an opt-in `Built with graviondev` footer. Localshare does not inject branding into arbitrary proxied sites.

**Future work:** Gravion-hosted relay/control plane, account dashboard, short-lived session credentials, expiry/revocation, audit events, team management, quotas and managed domains. Not implemented in this starter.

## 02 — Privacyflow

**Purpose:** Manage user-authorized VPN profiles and privacy-safe endpoint rotation with predictable fail-closed behavior.

**Current MVP:** TOML config validation, WireGuard profile checks and a rotation-plan dry run.

**Future work:** Isolated Linux networking service, WireGuard adapter, provider adapters for supported accounts/configurations, endpoint health scoring, transactional switching, firewall kill switch, DNS/IPv6 leak tests and reliable recovery. Any actual route change must require explicit user authorization and have rollback behavior.

**Not promised:** impossible traceability, invisible identity, permanent IP masking or remote MAC rewriting. VPN routing reduces exposure of the network path; it does not erase accounts, cookies, browser/device fingerprints or provider logs. MAC randomization is local-link privacy, not public-IP rotation.

## 03 — Agent Browser

**Purpose:** Permission-aware browser agent for bounded research and repetitive workflows on sites the user is authorized to access.

**Current MVP:** Visible Playwright browser, exact host allow-list, URL validation, bounded navigation and page text snapshot.

**Future work:** Search-provider connectors, multi-step planning, source citations, persistent user-owned profiles, approval checkpoints, per-task budgets, audit log, visible stop button, task resume and secure file-download handling.

**Stop conditions:** CAPTCHA, MFA, authentication wall, consent prompt, anti-bot challenge, rate limit or access denial. Agent Browser requests human input or stops rather than evading those controls.

## 04 — Gravion Trainner

**Purpose:** Find and measurably improve model quality using evaluations, diagnosis and supported optimization workflows.

**Current MVP:** JSONL test-dataset runner against an OpenAI-compatible endpoint, starter scoring and JSON report output.

**Future work:** Rubric-based graders, prompt/version experiments, retrieval/tool diagnosis, regression gates, model routing, approved dataset curation and provider-supported fine-tuning/LoRA adapters where available.

**Not promised:** automatic changes to arbitrary closed model weights, guaranteed reasoning gains or genuine human emotions. Any optimization must beat a fixed holdout baseline and pass safety/regression checks.
