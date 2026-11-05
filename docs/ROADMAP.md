# Gravion roadmap — 13 phases

A phase is complete only after its exit criteria and tests pass. This is a plan, not a claim that every feature already exists.

| Phase | Scope | Exit criteria |
|---:|---|---|
| 1 | Four-product definitions, threat models and monorepo | Names, boundaries, docs and baseline tests agreed |
| 2 | Shared tooling and CI | Repeatable clean install and all unit tests pass |
| 3 | Localshare CLI | Quick and named tunnel paths tested on supported OSes |
| 4 | Localshare relay/session protocol | Authenticated reverse-tunnel integration tests pass |
| 5 | Localshare access and branded domains | Expiry, revocation, TLS, DNS, Access and abuse controls reviewed |
| 6 | Localshare beta | Installers, security review, release signing and monitoring complete |
| 7 | Privacyflow WireGuard/provider adapters | Supported Linux target connects/disconnects with recovery |
| 8 | Privacyflow rotation and leak protection | Transactional rotation, kill switch and DNS/IPv6 tests pass |
| 9 | Agent Browser search connectors | Provider attribution, quotas and domain policies validated |
| 10 | Agent Browser task planner | Bounded tasks, approvals, cancellation and human handoff work |
| 11 | Gravion Trainner evaluation quality | Rubric graders and fixed holdout detect known regressions |
| 12 | Gravion Trainner optimization experiments | Approved candidate beats or matches baseline without safety regression |
| 13 | Integrated release and review | Independent security review, operational runbooks and supported release matrix |

## Current bundle status

- **Localshare:** Quick Tunnel and configured Named Tunnel CLI starter; no Gravion-hosted relay service.
- **Privacyflow:** profile validator and rotation-plan dry run; no privileged route manipulation.
- **Agent Browser:** visible allow-listed browser snapshot; no autonomous general-purpose task planner.
- **Gravion Trainner:** OpenAI-compatible evaluation runner; no universal model training.
