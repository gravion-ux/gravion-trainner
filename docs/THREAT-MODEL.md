# Threat model

## Assets
- Local development services exposed through Localshare.
- VPN profile metadata, private keys and endpoint information in Privacyflow.
- Browser cookies, user sessions, downloads and task instructions in Agent Browser.
- Prompts, outputs, evaluation data and model/provider credentials in Gravion Trainner.

## Primary threats
- Unintended public exposure of a local admin/service endpoint.
- Theft or disclosure of tunnel credentials, VPN keys or model API keys.
- A malicious webpage attempting prompt injection, SSRF, phishing or unwanted downloads.
- A VPN rotation failure causing traffic to fall back to an unintended network route.
- Evaluation data leakage or model-selection decisions driven by manipulated/poor-quality datasets.
- Supply-chain compromise in dependencies or deployment images.

## Controls

| Threat | Controls |
|---|---|
| Local service exposed to everyone | Loopback-only origin, email gate by default, interactive public-mode confirmation, stop control |
| Tunnel configuration or domain misrouting | Validate local config, require explicit named-tunnel config and provider-side Access policy |
| VPN credential leak | Never log private keys, restrictive permissions, secret-store integration in future service |
| VPN route/kill-switch failure | Dry-run first, isolated privileged helper, transactional switch, rollback and leak tests before release |
| Prompt injection from webpages | Treat page content as data, domain allow-list, action schemas, human approval for consequential operations |
| Browser overreach | Visible browser, task/time/navigation budgets, stop conditions, cancellation and audit log |
| Invalid model evaluation | Versioned dataset/rubric, holdout set, baseline comparison and multi-metric review |
| API key or dataset exfiltration | Local-by-default artifacts, redaction, explicit provider selection and retention controls |

## Residual risks
The starter projects are not independently security-certified. Third-party tunnel providers, VPN providers, browser engines, model APIs, DNS and VPS vendors introduce their own operational and privacy risks. No product promises perfect anonymity or universal access to websites.
