# API and module contracts

This bundle currently provides CLIs and library-level interfaces. The following contracts are target shapes for future services, not deployed endpoints.

## Localshare session service (future)
- `POST /v1/sessions` creates an expiring share session after validating origin, access mode and user identity.
- `GET /v1/sessions/{id}` returns metadata only (state, creation time, expiry and access mode), never connector secrets.
- `DELETE /v1/sessions/{id}` revokes a session immediately.
- Connector credentials are short-lived, write-only after creation and scoped to one session.

## Privacyflow local daemon (future)
- `GET /v1/status` returns active profile name and egress/DNS/IPv6 check status, never private keys.
- `POST /v1/rotation-plans` creates a dry-run plan.
- `POST /v1/rotations` starts a user-approved rotation only if kill switch readiness and rollback are verified.

## Agent Browser worker (future)
- `POST /v1/tasks` accepts URL, explicit allowed domains, maximum steps/time and permitted action types.
- `POST /v1/tasks/{id}/cancel` cancels immediately.
- `GET /v1/tasks/{id}/events` streams structured status and human approval requests.
- A task pauses at authentication, CAPTCHA, MFA, consent or access-denial checkpoints.

## Gravion Trainner evaluation service (future)
- `POST /v1/evaluations` accepts model adapter ID, dataset version and rubric version.
- `GET /v1/evaluations/{id}` returns metrics and redacted failure examples.
- Candidate promotion requires fixed holdout evaluation and regression/safety thresholds.

## Cross-product principle
No module receives another module's secrets by default. Localshare sessions cannot invoke browser automation; Agent Browser cannot change VPN routes; Gravion Trainner cannot read Localshare visitor sessions. Any future integration must use published, authenticated, audited and narrowly scoped APIs.
