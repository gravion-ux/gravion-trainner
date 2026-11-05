# Gravion four-product architecture

## Design principles

1. Four independently usable products with separate runtime and permission boundaries.
2. Least privilege: each product receives only the permissions it needs.
3. Explicit consent for network exposure, system routing changes, consequential browser actions and retention of prompts/output.
4. Reproducible evaluation and rollback for model changes.
5. Security-relevant operations are logged without recording secrets.
6. AI components do not receive unrestricted shell, root, browser or network-control access.

## High-level map

```text
Developer / User
    |
    +-- Localshare -------- cloudflared -------- edge -------- local/VPS web origin
    |
    +-- Privacyflow ------- profile validator / future isolated network service
    |                                                |
    |                                             WireGuard/provider
    |
    +-- Agent Browser ----- task policy -------- Playwright -------- approved website/search API
    |
    +-- Gravion Trainner -- evaluation dataset -- model adapter --- reports/candidate comparison

Shared optional infrastructure (future): identity, billing, audit metadata and policy APIs.
No product receives another product's secrets by default.
```

## Trust boundaries

- **Localshare:** the tunnel provider is an external network processor. Treat generated URLs as bearer access unless email/Access policy is enabled.
- **Privacyflow:** a future system networking adapter requires elevated privileges and must be isolated from the unprivileged CLI/UI. Never pass raw credentials to logs.
- **Agent Browser:** page text, HTML, downloads and search snippets are untrusted. Page content must not become agent instructions without policy checks. Keep the browser visible and stop at access challenges.
- **Gravion Trainner:** prompts/outputs may be sensitive. Default to local evaluation artifacts, explicit retention and redaction. Do not train on tenant data without opt-in and data rights.

## Deployment topologies

### Localshare Quick Tunnel

`Browser -> HTTPS temporary URL -> tunnel provider edge -> outbound tunnel -> cloudflared on developer PC -> 127.0.0.1:3000`

### Localshare Named Tunnel

`Browser -> preview.example.com -> DNS/Access -> named tunnel -> cloudflared on PC/VPS -> private origin`

### Direct VPS hosting

`Browser -> DNS -> VPS firewall 80/443 -> Caddy/Nginx -> private app container`

### Future cross-product integrations

Products may eventually exchange task metadata through narrow authenticated APIs. Each API must use short-lived user-bound tokens, explicit permissions, idempotency where appropriate, audit events and a revocation path. No generic command-execution API is planned.
