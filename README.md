# Orbit Interview — AI Interview Agent

A local-first AI interview platform scaffold with a Next.js web client, an Expo mobile shell, a FastAPI backend, PostgreSQL persistence, configurable AI providers, Docker Compose, and Kubernetes deployment manifests for k3s with Traefik.

> **Project status and deployment safety**
>
> This repository is a development and deployment foundation, not a production-ready or validated hiring decision system. The current backend does not yet provide complete authentication, role-based access control (RBAC), tenant isolation, candidate consent and retention workflows, audit logging, or a production voice transport. The mobile app is a starter shell. Do not expose the service to real candidate data or use automated scores as hiring decisions until the launch gates in [`docs/PRODUCTION_READINESS.md`](docs/PRODUCTION_READINESS.md) are implemented, reviewed, and tested.

## Contents

- [Features and current scope](#features-and-current-scope)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Run locally with Docker Compose](#run-locally-with-docker-compose)
- [Run components without Docker](#run-components-without-docker)
- [Configure the AI provider](#configure-the-ai-provider)
- [Role templates](#role-templates)
- [Deploy to k3s with Traefik](#deploy-to-k3s-with-traefik)
  - [1. Check the cluster](#1-check-the-cluster)
  - [2. Configure the hostname and storage](#2-configure-the-hostname-and-storage)
  - [3. Create namespace and secrets](#3-create-namespace-and-secrets)
  - [4. Deploy PostgreSQL and Redis](#4-deploy-postgresql-and-redis)
  - [5. Run database migrations](#5-run-database-migrations)
  - [6. Deploy the application](#6-deploy-the-application)
  - [7. Configure HTTPS and DNS](#7-configure-https-and-dns)
  - [8. Verify the deployment](#8-verify-the-deployment)
  - [9. Update after a new GitHub build](#9-update-after-a-new-github-build)
- [GitHub Actions pipeline](#github-actions-pipeline)
- [API workflow](#api-workflow)
- [Operations and troubleshooting](#operations-and-troubleshooting)
- [Security, fairness, and production launch gates](#security-fairness-and-production-launch-gates)
- [Known implementation boundaries](#known-implementation-boundaries)

## Features and current scope

- Interview modes: individual practice and recruiter-led recruitment workflows.
- Interview categories: technical, behavioral/HR, managerial/leadership, and mixed.
- Session target: 30 minutes.
- Interaction choice: text and voice selection in the interface. The real-time voice transport is not yet implemented.
- Role-oriented starter templates for DevOps Engineer, Site Reliability Engineer, Production Support Engineer, Cloud Engineer, Backend Engineer, and Technical Support Engineer.
- Configurable AI provider abstraction: Gemini is the default; OpenAI is optional.
- FastAPI, SQLAlchemy, Alembic, and PostgreSQL.
- Next.js web application and an Expo/React Native starter shell.
- Redis service configured for future cache/queue integration. Current API request processing does not depend on Redis.
- Docker Compose for local development.
- Kubernetes resources for PostgreSQL, Redis, API, web, Ingress, HPA, and a separate migration Job.
- GitHub Actions for tests, web build, container image publishing to GHCR, and updating Kubernetes image tags in Git.

## Architecture

```text
Browser / Expo mobile shell
          |
       Next.js web
          |
    Traefik Ingress (HTTPS)
       /          \
  /api/v1          /
    |              |
 FastAPI         Next.js
    |
 PostgreSQL

 Redis: deployed/configured for future cache and queue features
 AI provider: Gemini (default) or OpenAI (optional)
```

## Repository layout

```text
.
├── .github/workflows/ci-cd.yml
├── backend/
│   ├── app/                    # FastAPI application
│   ├── migrations/             # Alembic migration environment
│   ├── tests/
│   ├── alembic.ini
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── web/                    # Next.js web client
│   └── mobile/                 # Expo / React Native starter
├── infra/kubernetes/
│   ├── base/                   # Application, DB, Redis, Traefik Ingress
│   ├── migration/              # Separate Alembic migration Kustomize target
│   ├── create-secrets.sh       # Securely generates DB password and secrets
│   ├── DATABASE-REDIS-SETUP.md
│   └── TRAefik-README.md
├── docs/
│   ├── PRODUCTION_READINESS.md
│   ├── RELEASE_CHECKLIST.md
│   └── CI_CD_BOUNDARY.md
├── docker-compose.yml
└── .env.example
```

## Prerequisites

### Local development

- Docker Engine and Docker Compose plugin.
- Node.js 26 LTS for the web client.
- Python 3.12+ for running the backend directly.
- A Gemini API key or OpenAI API key for model-generated interview content.

### k3s deployment

- A working k3s cluster and `kubectl` configured for that cluster.
- Traefik Ingress Controller installed (the manifests use `ingressClassName: traefik` and the `websecure` entrypoint).
- A DNS name pointing to the Traefik ingress endpoint.
- A TLS certificate stored in a Kubernetes secret named `interview-tls` in namespace `ai-interview-agent`, or a certificate workflow that creates that secret.
- A StorageClass named `local-path` (common in k3s), or an appropriate replacement configured in the PostgreSQL and Redis manifests.
- Metrics Server for the HorizontalPodAutoscaler.
- GitHub Container Registry (GHCR) access from the cluster. If the packages are private, configure an image pull secret for the application workloads.
- OpenSSL on the machine used to run `create-secrets.sh`.

## Run locally with Docker Compose

1. Clone the repository and enter its root directory:

   ```bash
   git clone https://github.com/singhgauravlinux-coder/ai-interview-agent.git
   cd ai-interview-agent
   ```

2. Create the local environment file:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set at least one provider key:
   - Gemini: set `AI_PROVIDER=gemini` and `GOOGLE_API_KEY=...`.
   - OpenAI: set `AI_PROVIDER=openai` and `OPENAI_API_KEY=...`.

   The sample database credentials in `.env.example` and `docker-compose.yml` are for local development only. Do not reuse them in a deployed environment.

4. Build and start the stack:

   ```bash
   docker compose up --build -d
   ```

5. Check containers and logs:

   ```bash
   docker compose ps
   docker compose logs -f api
   ```

6. Open the local services:

   | Service | URL |
   |---|---|
   | Web application | http://localhost:3000 |
   | FastAPI OpenAPI docs | http://localhost:8000/docs |
   | API health (liveness) | http://localhost:8000/health |
   | API readiness (database check) | http://localhost:8000/ready |

7. Stop the stack:

   ```bash
   docker compose down
   ```

   To also delete the local PostgreSQL volume and all local database data:

   ```bash
   docker compose down -v
   ```

   **Warning:** `down -v` permanently removes the local database volume.

## Run components without Docker

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Set the required environment variables in your shell or load them from the repository-root `.env`. Ensure PostgreSQL is running and `DATABASE_URL` points to it. Apply migrations and start FastAPI:

```bash
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run backend tests from `backend/`:

```bash
python -m pytest -q
```

### Web frontend

In another terminal:

```bash
cd frontend/web
npm install
cp .env.local.example .env.local
```

Edit `.env.local` so `NEXT_PUBLIC_API_URL` points to the API address reachable by the browser. Then run:

```bash
npm run dev -- --hostname 0.0.0.0
```

For access from another device, do not use `localhost` as the API hostname. Use the machine's LAN IP or resolvable DNS name and add the web origin to `CORS_ORIGINS` in the backend environment. Restart the API after changing CORS settings.

### Mobile starter

```bash
cd frontend/mobile
npm install
```

Set `EXPO_PUBLIC_API_URL` to an API address reachable from the physical device or emulator, then run:

```bash
npx expo start
```

The mobile project is currently a starter shell; it does not yet contain the full interview room, voice, and report experience.

## Configure the AI provider

### Gemini (default)

```env
AI_PROVIDER=gemini
GOOGLE_API_KEY=your_google_ai_studio_key
GEMINI_MODEL=gemini-flash-latest
```

### OpenAI (optional)

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
```

Provider selection is environment-driven. Confirm the selected model is available to your provider account and region. Never commit API keys to Git or place them in frontend source code.

## Role templates

| Role | Starter competency areas |
|---|---|
| DevOps Engineer | Linux, Docker, Kubernetes, CI/CD, Terraform, monitoring |
| Site Reliability Engineer | SLO/SLI, incident response, Prometheus, capacity, distributed systems |
| Production Support Engineer | Linux, SQL, networking, logs, ITIL, root-cause analysis |
| Cloud Engineer | Cloud platforms, IAM, networking, Terraform, containers, security |
| Backend Engineer | Python, APIs, PostgreSQL, caching, testing, system design |
| Technical Support Engineer | Troubleshooting, networking, ticketing, communication, escalation |

These are starter competency lists, not validated job-analysis instruments. Adapt them to each role and have subject-matter experts validate the questions and scoring rubrics.

## Deploy to k3s with Traefik

The following sequence deploys the in-cluster PostgreSQL and Redis services first, runs the Alembic migration Job, and only then deploys the API and web application. Run commands from the repository root.

### 1. Check the cluster

```bash
kubectl get nodes -o wide
kubectl get storageclass
kubectl get pods -n kube-system
```

Confirm:
- Your k3s nodes are Ready.
- Traefik is installed and running.
- A StorageClass named `local-path` exists.

If your storage class has a different name, edit `storageClassName` in:
- `infra/kubernetes/base/database.yaml`
- `infra/kubernetes/base/redis.yaml`

The bundled PostgreSQL StatefulSet and Redis Deployment are single-instance starter services. `local-path` volumes are node-local and do not provide high availability or backups. For production-critical workloads, use a suitable CSI storage system or managed database/cache service.

### 2. Configure the hostname and storage

Before deploying, replace `interview.example.com` with your real DNS hostname in:

- `infra/kubernetes/base/ingress.yaml` (both TLS host and rule host).
- `infra/kubernetes/base/configmap.yaml` (`CORS_ORIGINS`, including the `https://` scheme).

For example, if the application hostname is `interview.yourdomain.com`, set:

```yaml
# ingress.yaml
spec:
  tls:
    - hosts:
        - interview.yourdomain.com
      secretName: interview-tls
  rules:
    - host: interview.yourdomain.com
```

And in `configmap.yaml`:

```yaml
data:
  CORS_ORIGINS: https://interview.yourdomain.com
```

Keep `NEXT_PUBLIC_API_URL: /api/v1` for same-host browser requests through the Ingress.

### 3. Create namespace and secrets

Create the namespace:

```bash
kubectl apply -f infra/kubernetes/base/namespace.yaml
```

The helper script creates:
- `postgres-secrets` containing the PostgreSQL database name, user, and generated password.
- `interview-secrets` containing a matching SQLAlchemy `DATABASE_URL`, the Gemini key, and the optional OpenAI key.

It generates a cryptographically random 256-bit password using `openssl rand -hex 32`. The password is URL-safe and is not printed to the terminal.

Optionally provide the Gemini key securely at the prompt:

```bash
read -rsp 'Gemini API key (press Enter to skip): ' GOOGLE_API_KEY
echo
export GOOGLE_API_KEY

bash infra/kubernetes/create-secrets.sh

unset GOOGLE_API_KEY
```

If you intend to use OpenAI instead, the helper creates an empty `OPENAI_API_KEY`; update the secret with your real OpenAI key and set `AI_PROVIDER: openai` in the ConfigMap before deploying the application.

If you skipped the Gemini key, add it before using Gemini:

```bash
read -rsp 'Gemini API key: ' GOOGLE_API_KEY
echo

kubectl -n ai-interview-agent create secret generic interview-secrets \
  --from-literal=DATABASE_URL="$(kubectl -n ai-interview-agent get secret interview-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d)" \
  --from-literal=GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --from-literal=OPENAI_API_KEY='' \
  --dry-run=client -o yaml | kubectl apply -f -

unset GOOGLE_API_KEY
```

The helper deliberately refuses to overwrite either secret. This is important: changing the Kubernetes password secret does not change the password inside an already-initialized PostgreSQL data directory. Do not delete and recreate secrets casually, and do not run the generator again against an existing database.

**Secret handling:** Kubernetes Secrets are not automatically a full secret-management solution. Restrict RBAC access, enable encryption at rest for Kubernetes Secrets, and use SOPS, External Secrets Operator, or your platform's secret manager for production. Do not commit generated secret YAML or passwords.

### 4. Deploy PostgreSQL and Redis

Apply the application ConfigMap and the data services:

```bash
kubectl apply -f infra/kubernetes/base/configmap.yaml
kubectl apply -f infra/kubernetes/base/database.yaml
kubectl apply -f infra/kubernetes/base/redis.yaml
```

Wait for PostgreSQL and Redis:

```bash
kubectl -n ai-interview-agent rollout status statefulset/interview-postgres --timeout=300s
kubectl -n ai-interview-agent rollout status deployment/interview-redis --timeout=180s
kubectl -n ai-interview-agent get pods,pvc,svc
```

Do not continue until the PostgreSQL pod is Ready and the PostgreSQL and Redis PVCs are Bound.

### 5. Run database migrations

The migration is a separate Kubernetes Job. It must complete successfully before the API deployment is rolled out.

```bash
kubectl -n ai-interview-agent delete job interview-db-migrate --ignore-not-found
kubectl apply -k infra/kubernetes/migration
kubectl -n ai-interview-agent wait \
  --for=condition=complete \
  job/interview-db-migrate \
  --timeout=300s
kubectl -n ai-interview-agent logs job/interview-db-migrate
```

If the Job fails, inspect it before proceeding:

```bash
kubectl -n ai-interview-agent describe job interview-db-migrate
kubectl -n ai-interview-agent get pods -l job-name=interview-db-migrate
kubectl -n ai-interview-agent logs job/interview-db-migrate
```

Do not deploy the API until the migration has succeeded.

### 6. Deploy the application

The GitHub Actions workflow updates the Kustomize image tags after a successful push to `main`. Pull the latest repository changes before applying:

```bash
git pull origin main
```

Then apply the base:

```bash
kubectl apply -k infra/kubernetes/base
```

Wait for the application rollouts:

```bash
kubectl -n ai-interview-agent rollout status deployment/interview-api --timeout=300s
kubectl -n ai-interview-agent rollout status deployment/interview-web --timeout=300s
```

### 7. Configure HTTPS and DNS

The Ingress expects:
- Traefik's `websecure` entrypoint.
- A DNS record for the hostname pointing to the Traefik ingress endpoint.
- A TLS secret named `interview-tls` in namespace `ai-interview-agent`.

If you already have a TLS certificate and key, create the secret:

```bash
kubectl -n ai-interview-agent create secret tls interview-tls \
  --cert=/path/to/fullchain.pem \
  --key=/path/to/privkey.pem
```

Replace the paths with your actual certificate files. Do not put private keys in Git.

If you use cert-manager, configure an appropriate `Certificate` resource and issuer so it creates the `interview-tls` secret. cert-manager is not installed or configured by this repository.

### 8. Verify the deployment

```bash
kubectl -n ai-interview-agent get pods,svc,pvc,ingress,hpa
kubectl -n ai-interview-agent get events --sort-by=.lastTimestamp
kubectl -n ai-interview-agent logs deployment/interview-api --tail=100
kubectl -n ai-interview-agent logs deployment/interview-web --tail=100
```

Check the public endpoints after DNS and TLS are configured:

- `https://YOUR_HOSTNAME/` — web application.
- `https://YOUR_HOSTNAME/health` — API liveness.
- `https://YOUR_HOSTNAME/ready` — API readiness; this checks PostgreSQL.
- `https://YOUR_HOSTNAME/docs` is not routed by the current Ingress. Use port-forwarding if you need the API docs:

  ```bash
  kubectl -n ai-interview-agent port-forward svc/interview-api 8000:8000
  ```

  Then open `http://localhost:8000/docs`.

### 9. Update after a new GitHub build

For every push to `main`, the GitHub Actions workflow:
1. Runs backend tests and frontend checks/build.
2. Builds the API and web Docker images.
3. Pushes each image to GHCR with an immutable commit-SHA tag and a `latest` tag.
4. Updates `infra/kubernetes/base/kustomization.yaml` and `infra/kubernetes/migration/kustomization.yaml` with the new SHA tags and commits those changes to `main`.

The workflow does **not** connect to k3s and does **not** apply Kubernetes manifests. After the workflow succeeds, update the cluster manually:

```bash
git pull origin main

# Run the migration Job using the newly tagged API image.
kubectl -n ai-interview-agent delete job interview-db-migrate --ignore-not-found
kubectl apply -k infra/kubernetes/migration
kubectl -n ai-interview-agent wait \
  --for=condition=complete \
  job/interview-db-migrate \
  --timeout=300s

# Apply updated API/web images and other base resources.
kubectl apply -k infra/kubernetes/base

kubectl -n ai-interview-agent rollout status deployment/interview-api --timeout=300s
kubectl -n ai-interview-agent rollout status deployment/interview-web --timeout=300s
```

For a more robust ongoing deployment process, configure a GitOps controller (for example, Flux or Argo CD) to watch the manifests repository/path and reconcile changes. That controller is not included or configured here.

## GitHub Actions pipeline

Workflow file: [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).

### What it does

| Trigger | Actions |
|---|---|
| Pull request | Backend dependency install, compile, tests; frontend install, type-check, production build |
| Push to `main` | Runs the same checks, builds API and web images, pushes SHA and `latest` tags to GHCR, updates Kustomize image references in Git |

### Repository configuration

1. In GitHub, open **Settings → Actions → General → Workflow permissions**.
2. Enable **Read and write permissions** so the workflow can push the manifest update commit.
3. Ensure the repository's GitHub Actions token is allowed to publish packages to GHCR.
4. After the first successful build, open the repository's **Packages** page and check the API and web packages.
5. If the packages are private, configure Kubernetes `imagePullSecrets` for the API, web, and migration workloads. Alternatively, make the packages publicly pullable if that is appropriate for your project.
6. Protect `main` with pull-request review and required status checks.

No `KUBE_CONFIG` secret is required by this workflow because it does not deploy to the cluster. It only publishes images and commits updated manifest tags.

## API workflow

The backend exposes the following interview lifecycle endpoints:

1. `POST /api/v1/interviews` — create an interview.
2. `POST /api/v1/interviews/{id}/start` — start an interview.
3. `POST /api/v1/interviews/{id}/answer` — submit an answer.
4. `POST /api/v1/interviews/{id}/complete` — complete an interview.
5. `GET /api/v1/interviews/{id}/report` — retrieve the report.

Use the generated FastAPI OpenAPI documentation at `/docs` to inspect the current request and response schemas.

## Operations and troubleshooting

### Check Kubernetes resources

```bash
kubectl -n ai-interview-agent get all
kubectl -n ai-interview-agent get pvc
kubectl -n ai-interview-agent get ingress
kubectl -n ai-interview-agent get events --sort-by=.lastTimestamp
```

### PostgreSQL pod does not become Ready

```bash
kubectl -n ai-interview-agent describe statefulset interview-postgres
kubectl -n ai-interview-agent get pods
kubectl -n ai-interview-agent logs statefulset/interview-postgres
kubectl -n ai-interview-agent get pvc
```

Check that:
- `postgres-secrets` exists and contains the expected keys.
- The storage class exists and the PVC is Bound.
- The node has sufficient disk and memory.
- The database password secret has not been changed after the data directory was initialized.

### API readiness fails

The `/ready` endpoint checks PostgreSQL connectivity. Inspect the API logs and verify the `DATABASE_URL` secret and PostgreSQL Service:

```bash
kubectl -n ai-interview-agent logs deployment/interview-api --tail=200
kubectl -n ai-interview-agent get secret interview-secrets
kubectl -n ai-interview-agent get svc interview-postgres
kubectl -n ai-interview-agent get pods
```

Do not print or paste decoded secret values into tickets or chat.

### Ingress returns 404 or TLS errors

Check the Ingress class, host, Traefik pods, DNS record, and TLS secret:

```bash
kubectl -n ai-interview-agent describe ingress interview-ingress
kubectl -n ai-interview-agent get secret interview-tls
kubectl -n kube-system get pods
```

Confirm that the hostname in the Ingress matches the DNS name and certificate SAN.

### GHCR image pull fails

Check that the image name and SHA tag exist in GitHub Packages. If the package is private, create an image pull secret and reference it from the relevant pod specs. Ensure the cluster can reach `ghcr.io`.

### HPA shows unknown metrics

Check that Metrics Server is installed and healthy:

```bash
kubectl -n kube-system get deployment metrics-server
kubectl top nodes
kubectl top pods -n ai-interview-agent
```

The HPA is not useful until resource metrics are available.

### Local Next.js hot reload WebSocket fails on LAN

Run the dev server bound to all interfaces:

```bash
npm run dev -- --hostname 0.0.0.0
```

Use a reachable LAN IP/DNS in the browser and in `NEXT_PUBLIC_API_URL`. If using a reverse proxy in development, it must forward WebSocket upgrade requests. The production Kubernetes path uses Traefik; Traefik supports WebSocket upgrades without a separate WebSocket-specific Ingress route.

## Security, fairness, and production launch gates

Read [`docs/PRODUCTION_READINESS.md`](docs/PRODUCTION_READINESS.md), [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md), and [`docs/CI_CD_BOUNDARY.md`](docs/CI_CD_BOUNDARY.md) before exposing the service.

At minimum, complete and test:
- Authentication, RBAC, tenant isolation, and least-privilege service accounts.
- Candidate notice and consent, data minimization, retention, export, and deletion.
- Audit logging and administrative access controls.
- Rate limiting, abuse protection, secure headers, and dependency/image scanning.
- TLS for all external traffic and appropriate database connection protection.
- Tested PostgreSQL backups and restore procedures; point-in-time recovery where required.
- Monitoring, alerting, resource limits, incident response, and disaster recovery.
- Evaluation rubric validation, calibration, bias testing, candidate correction/appeal, and human review.

Do not score accent, appearance, inferred emotion/personality, age, gender, disability, or other protected traits. Evaluate only job-related evidence against validated criteria. Do not use AI output as the sole basis for employment decisions.

## Known implementation boundaries

- Voice is currently a selectable interaction mode; real-time WebRTC/STT/TTS transport is not included.
- The Expo app is a starter shell, not a complete mobile interview product.
- Authentication, RBAC, tenant isolation, consent, retention/deletion, audit trail, rate limiting, and production observability remain implementation gaps.
- Redis is deployed and configured but is not currently used by the API's core request path.
- PostgreSQL and Redis Kubernetes manifests are single-instance starter deployments, not HA configurations.
- The GitHub Actions workflow publishes images and updates Git manifests; it does not deploy to k3s.
- Automated AI evaluation needs validated rubrics, calibration, bias testing, and human oversight before any employment-related use.
