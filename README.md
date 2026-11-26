# Orbit Interview — AI Interview Agent

Local-first full-stack interview platform scaffold with a redesigned responsive glass UI, role templates, configurable LLM providers, PostgreSQL persistence, Docker, Kubernetes resources and GitHub Actions CI/CD.

> **Deployment safety:** This repository is a production-oriented foundation, not a certified production hiring system. The current API does not yet implement user authentication, tenant isolation, candidate consent/retention workflows, or a completed voice transport. Do not expose candidate data or the API publicly until the launch gates in `docs/PRODUCTION_READINESS.md` are completed and security-tested. Kubernetes manifests are deployment scaffolding; your cluster, DNS, TLS, managed database, secrets and identity provider are environment-specific.

## Included capabilities

- Interview modes: practice and recruitment.
- Categories: technical, behavioral/HR, managerial/leadership and mixed.
- Interaction selection: text and voice (voice UI selection is present; real-time voice adapter remains to be integrated).
- 30-minute sessions with role-oriented competency sets.
- Role presets: DevOps Engineer, Site Reliability Engineer, Production Support Engineer, Cloud Engineer, Backend Engineer and Technical Support Engineer.
- AI provider abstraction: Gemini default; OpenAI optional; configured via environment variables.
- FastAPI + SQLAlchemy + Alembic + PostgreSQL; Redis connection setting reserved for caching/queue integration.
- Next.js web frontend and Expo mobile shell.
- Docker Compose for local development.
- Kubernetes Deployments, Services, Ingress, HPA and health/readiness probes.
- GitHub Actions workflow for tests, web build, image publication to GHCR and Kubernetes rollout.

## Architecture

```text
Browser / Expo
      |
 Next.js web ------------------------------+
      |                                    |
      +---------- HTTPS / Ingress ----------+
                         |
                 FastAPI /api/v1
                  |          |
              PostgreSQL   Gemini / OpenAI
                  |
             Redis (reserved for cache/queue integration)
```

## Local development

Prerequisites: Docker Engine + Compose, Node.js 26 LTS, Python 3.12+ (Python 3.12 is used in the backend container), and an AI provider API key for live model-generated content.

1. Configure environment:

   ```bash
   cp .env.example .env
   # Edit .env and set GOOGLE_API_KEY for Gemini, or choose AI_PROVIDER=openai.
   ```

2. Start the stack from repository root:

   ```bash
   docker compose up --build
   ```

3. Open:
   - Web: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - API health: http://localhost:8000/health
   - API readiness: http://localhost:8000/ready

   The API container runs Alembic migrations on startup. For a manual backend workflow, use `cd backend`, create a Python 3.12 virtual environment, `pip install -r requirements.txt`, then `alembic upgrade head` and `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

4. For web-only development, use `cd frontend/web && npm install && cp .env.local.example .env.local && npm run dev -- --hostname 0.0.0.0`. The development script uses Webpack HMR and the LAN origin is allowlisted. Edit `.env.local` and set `NEXT_PUBLIC_API_URL` to the backend IP/DNS reachable by the browser. If browsing from another machine, do not use `localhost` in this URL. Also set `CORS_ORIGINS` in the root `.env` to include the web origin, for example `http://192.168.58.139:3000`, then restart the API.

5. Mobile shell: `cd frontend/mobile && npm install && npx expo start`. A real device must be able to reach the API host; configure `EXPO_PUBLIC_API_URL` accordingly.

## AI provider configuration

Gemini (default):

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-flash-latest
```

Optional OpenAI:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4.1-mini
```

The agent calls a shared `AIProvider` interface. Provider selection is environment-driven. Confirm that the model alias is enabled for your provider account and region before deployment.

## Role templates

The web UI includes these initial role templates:

| Role | Focus areas |
|---|---|
| DevOps Engineer | Linux, Docker, Kubernetes, CI/CD, Terraform, monitoring |
| Site Reliability Engineer | SLO/SLI, incident response, Prometheus, capacity, distributed systems |
| Production Support Engineer | Linux, SQL, networking, logs, ITIL, root cause analysis |
| Cloud Engineer | Cloud platforms, IAM, networking, Terraform, containers, security |
| Backend Engineer | Python, APIs, PostgreSQL, caching, testing, system design |
| Technical Support Engineer | Troubleshooting, networking, ticketing, communication, escalation |

These are starter competency lists. Customize them to your job architecture and validate each rubric with subject-matter experts.

## Kubernetes deployment

### Cluster prerequisites

- Kubernetes 1.28+ and `kubectl` with access to the target cluster.
- NGINX Ingress Controller (or adapt `ingress.yaml` to your ingress controller).
- cert-manager or an externally provisioned TLS secret named `interview-tls`.
- Managed PostgreSQL with backups, point-in-time recovery and TLS.
- Managed Redis if queue/cache functionality is enabled. Replace `REDIS_URL` in the ConfigMap with the managed Redis endpoint; the current API does not yet depend on Redis for core request processing.
- Metrics Server for HPA.
- Container registry access to GHCR.
- External Secrets Operator or equivalent secret manager strongly recommended.

### Configure manifests

1. Replace `interview.example.com` in `infra/kubernetes/base/ingress.yaml` and the `CORS_ORIGINS` value in `configmap.yaml` with your real hostname.
2. Replace image placeholders in `api.yaml` and `web.yaml` with your GHCR image names, or let the GitHub workflow update them during deploy.
3. Create the namespace and secrets. Do not commit actual secrets:

   ```bash
   kubectl apply -f infra/kubernetes/base/namespace.yaml
   kubectl -n ai-interview-agent create secret generic interview-secrets \
     --from-literal=DATABASE_URL='postgresql+psycopg://USER:PASSWORD@DB_HOST:5432/DB_NAME' \
     --from-literal=GOOGLE_API_KEY='YOUR_KEY' \
     --from-literal=OPENAI_API_KEY=''
   ```

4. Ensure your DB permits connections from the cluster and uses TLS. The SQLAlchemy URL should include the required SSL parameters for your provider.
5. Apply:

   ```bash
   kubectl apply -k infra/kubernetes/base
   kubectl -n ai-interview-agent get pods,svc,ingress,hpa
   ```

6. Check rollout and logs:

   ```bash
   kubectl -n ai-interview-agent rollout status deployment/interview-api
   kubectl -n ai-interview-agent rollout status deployment/interview-web
   kubectl -n ai-interview-agent logs deployment/interview-api
   ```

**Database migration note:** Database migrations are represented as a dedicated Kubernetes Job manifest. They must be executed by your separate deployment/GitOps process before rolling out application replicas; API replicas do not run migrations during startup.

### GitHub Actions CI/CD

Workflow: `.github/workflows/ci-cd.yml`.

Configure repository settings:

- `KUBE_CONFIG`: base64-encoded kubeconfig for a dedicated deployment identity with namespace-scoped permissions.
- Make GHCR packages accessible to the cluster (or configure `imagePullSecrets` for a private package).
- Update ingress hostname, TLS secret, CORS origin and database/AI secrets in the cluster.
- Protect `main` with required PR checks and review approvals.

On pull requests the workflow compiles/tests the backend and builds the web app. On pushes to `main`, it runs CI, builds and pushes API/web images to GHCR under both immutable commit-SHA tags and `latest`, then commits the immutable SHA tags to the Kubernetes Kustomize manifests. GitHub Actions does not connect to a cluster or deploy anything. A separate GitOps controller or platform deployment process is responsible for applying the updated manifests.

## API workflow

1. `POST /api/v1/interviews`
2. `POST /api/v1/interviews/{id}/start`
3. `POST /api/v1/interviews/{id}/answer`
4. `POST /api/v1/interviews/{id}/complete`
5. `GET /api/v1/interviews/{id}/report`

## Security, fairness and launch gates

Read `docs/PRODUCTION_READINESS.md` before any external deployment. In particular, the current backend endpoints are unauthenticated. The platform must not be used to make autonomous hiring decisions. Do not score accent, appearance, inferred emotion/personality, age, gender, disability or other protected traits. Use job-related evidence, allow candidate correction/appeal, and keep a qualified human decision-maker in control.

## Known implementation boundaries

- Voice is currently a selectable interaction mode only; no WebRTC/STT/TTS provider transport has been shipped.
- Mobile is a starter Expo shell; the full interview room and report flows need implementation.
- Authentication, RBAC, tenant isolation, consent, retention/deletion, audit trail, rate limiting and production observability are launch blockers documented in `docs/PRODUCTION_READINESS.md`.
- Redis is configured but not yet used for background jobs or distributed coordination.
- Automated AI evaluation requires rubric validation, calibration, bias testing and human review before any employment-related use.
