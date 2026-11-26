# CI and release handoff checklist

## Automated by GitHub Actions (CI only)
- Backend dependency installation, Python compile and pytest
- Web dependency installation, TypeScript check and Next.js production build
- Build API and web OCI images
- Push both images to GHCR using immutable commit-SHA tags and the convenience `latest` tag
- Update both Kustomize image references to the immutable commit SHA
- Commit and push the updated manifests back to the repository

## Explicitly outside GitHub Actions
GitHub Actions does **not** configure kubectl, access a Kubernetes cluster, run migrations, apply manifests, or wait for Deployment rollouts. There is no CD step in this workflow.

Use a separate deployment mechanism to watch/apply the manifest changes, such as Argo CD, Flux, or an independently managed platform release process. That mechanism should:
1. Detect the manifest commit.
2. Apply the migration Job and wait for success.
3. Apply the API and web Deployments.
4. Verify rollout health and run smoke tests.

## Required GitHub configuration
- Enable repository `contents: write` and `packages: write` permissions for the workflow.
- No `KUBE_CONFIG` secret is needed by this CI workflow.
- Ensure GHCR package visibility and pull permissions match your Kubernetes cluster configuration.

## Required Kubernetes configuration (managed separately)
- Create namespace-scoped `interview-secrets` with `DATABASE_URL`, `GOOGLE_API_KEY`, and `OPENAI_API_KEY`.
- Configure `interview-config` for Redis and allowed CORS origins.
- Configure real DNS hostname and TLS secret in the Ingress.
- Configure GHCR imagePullSecrets if packages are private.
- Use managed PostgreSQL with TLS, backups and point-in-time recovery.
- Install NGINX Ingress Controller and Metrics Server, or adapt Ingress/HPA resources.

## Production launch blockers
The current application scaffold still lacks authentication, tenant authorization/isolation, candidate consent/retention/deletion workflow, audit logging, abuse controls and completed voice transport. Mobile is a shell rather than a feature-complete interview app. Do not process real candidate data or make hiring decisions until these are implemented and independently security/fairness tested.
