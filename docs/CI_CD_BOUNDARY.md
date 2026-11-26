# CI / CD responsibility boundary

## GitHub Actions: CI + image publication + manifest update only
GitHub Actions runs tests and build checks, publishes API/web images to GHCR, and updates Kustomize image tags to the commit SHA. It does not authenticate to or contact Kubernetes.

## CD: separate GitOps/deployment controller
Argo CD, Flux, or another deployment platform watches the manifest repository and performs the actual Kubernetes reconciliation. The deployment controller, not GitHub Actions, owns migration execution, apply/reconcile, rollout status, and cluster health.

## Image tags
- `${GITHUB_SHA}` is the immutable release identifier and is written to manifests.
- `latest` is also pushed for convenience, but manifests should remain pinned to `${GITHUB_SHA}` for reproducibility.
