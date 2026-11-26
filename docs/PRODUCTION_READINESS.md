# Production readiness and release gates

This document distinguishes shipped scaffolding from controls that must be completed before handling real candidate or employee data. A passing build is not a production security or fairness certification.

## Current status

| Area | Status | Notes |
|---|---|---|
| Responsive web landing/workspace | Implemented | Glass UI, role selection, API-backed create/list |
| Role presets | Implemented | Six initial roles; validate skills/rubrics with SMEs |
| FastAPI CRUD interview workflow | Starter implemented | Review endpoint authorization and error handling |
| PostgreSQL + Alembic | Implemented | Backups/restore drills are operator responsibilities |
| Gemini/OpenAI adapter | Implemented | Provider keys and model access must be configured |
| Docker Compose | Implemented | Local development, not production topology |
| Kubernetes manifests | Scaffold implemented | Ingress, HPA, probes, resources; adapt to cluster |
| GitHub Actions | Scaffold implemented | CI build/test + GHCR + rollout; configure secrets and protected branch |
| Authentication / SSO | **Not implemented — blocker** | Add OIDC/OAuth2, MFA for privileged roles, session lifecycle |
| RBAC and tenant isolation | **Not implemented — blocker** | Enforce recruiter/candidate/admin scopes server-side on every object |
| Consent and privacy workflow | **Not implemented — blocker** | Candidate notice, purpose limitation, opt-in voice, withdrawal, data export/deletion |
| Audit logging | **Not implemented — blocker** | Append-only events for access, edits, exports, evaluation and admin actions |
| Rate limiting / abuse controls | **Not implemented — blocker** | Per-user/IP quotas, payload limits, bot and abuse protection |
| Voice transport | **Not implemented** | Select and secure WebRTC/STT/TTS vendor; provide text alternative |
| Full mobile experience | **Not implemented** | Expo shell only; implement auth, interview room, reports, offline/error states |
| Production monitoring | **Not implemented** | Metrics, traces, structured logs, alerting, SLOs, incident runbooks |
| AI assessment validation | **Not implemented — blocker for hiring use** | Job-analysis-backed rubrics, calibration, adverse-impact testing, human review |

## Mandatory launch gates

1. **Identity and authorization**
   - Integrate an established OIDC provider; do not invent password storage/session cryptography.
   - Define candidate, recruiter, hiring-manager, reviewer and administrator roles.
   - Enforce tenant and object-level authorization in every API endpoint; add negative tests proving cross-tenant access is denied.
   - Use short-lived sessions/tokens, secure cookies where applicable, CSRF protection, MFA for privileged accounts and account recovery controls.

2. **Candidate privacy and consent**
   - Publish a clear privacy notice and retention schedule before collecting data.
   - Obtain explicit, revocable consent for audio recording/transcription; offer equivalent text participation.
   - Implement export, correction, deletion, legal hold and withdrawal workflows.
   - Encrypt data in transit and at rest; use managed KMS for keys and rotate secrets.
   - Avoid sending unnecessary identifiers or sensitive personal data to model providers; document provider retention/training settings and subprocessors.

3. **AI safety, fairness and human oversight**
   - Define role-specific competencies from a documented job analysis and validate them with qualified subject-matter experts.
   - Score only observable, job-related evidence. Never infer or score protected traits, accent, appearance, emotion or personality.
   - Show evidence, uncertainty, missing evidence and model limitations; allow human review and correction.
   - Do not auto-reject or make autonomous hiring decisions. Benchmark for disparate impact and monitor drift before and during use.
   - Version prompts, models and rubrics; preserve evaluation provenance and provide rollback.

4. **Reliability and security engineering**
   - Add request IDs, structured redacted logs, tracing, metrics, dashboards and actionable alerts.
   - Add API rate limiting, request timeouts, retries with bounded backoff, circuit breakers and provider cost/token budgets.
   - Add dependency/container scanning, SBOM, image signing, secret scanning, patch cadence and penetration testing.
   - Use private networking, network policies, non-root containers, least-privilege service accounts, pod disruption budgets and resource quotas.
   - Test restore from database backups and define RPO/RTO. Configure managed Postgres HA/PITR and Redis HA if used.
   - Move Alembic migrations to a single release Job before scaling API replicas.

5. **Release validation**
   - Unit, integration, contract, browser E2E, accessibility, load, resilience and security tests pass.
   - Staging deployment and smoke tests pass; rollback is rehearsed.
   - Legal/privacy/security review is complete for target jurisdictions and employment use cases.

## Operational note

Do not set a public DNS record or route real candidate traffic to the current unauthenticated API until the blockers above are addressed. Kubernetes resources here are a baseline to adapt, not a substitute for threat modelling or a deployment review.
