# PostgreSQL and Redis on k3s

This adds single-instance PostgreSQL and Redis inside the `ai-interview-agent`
namespace. It is a self-managed starter deployment, not an HA database service.
On a single-node k3s cluster, the `local-path` StorageClass is suitable for a
small initial deployment. For multi-node/production-critical use, use a CSI
storage class with appropriate failure semantics or managed PostgreSQL/Redis,
and configure tested backups/PITR.

## 1. Check storage
```bash
kubectl get storageclass
```
The manifests use `local-path`. If your default storage class has a different
name, change `storageClassName` in `base/database.yaml` and `base/redis.yaml`.

## 2. Create namespace and auto-generate secrets
```bash
kubectl apply -f infra/kubernetes/base/namespace.yaml

# Optional: provide your Gemini key without putting it in the script or Git.
read -rsp 'Gemini API key (press Enter to skip): ' GOOGLE_API_KEY; echo
export GOOGLE_API_KEY
bash infra/kubernetes/create-secrets.sh
unset GOOGLE_API_KEY
```
The script generates a 256-bit random database password using `openssl`, then
creates both `postgres-secrets` and `interview-secrets` with the matching
PostgreSQL password and `DATABASE_URL`. The generated password is URL-safe and
is not printed to the terminal. If you skip the Gemini key, add it to
`interview-secrets` before using Gemini:

```bash
read -rsp 'Gemini API key: ' GOOGLE_API_KEY; echo
kubectl -n ai-interview-agent create secret generic interview-secrets \
  --from-literal=DATABASE_URL="$(kubectl -n ai-interview-agent get secret interview-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d)" \
  --from-literal=GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --from-literal=OPENAI_API_KEY='' \
  --dry-run=client -o yaml | kubectl apply -f -
unset GOOGLE_API_KEY
```
Do not commit real secret values to Git. The script deliberately refuses to
overwrite either secret: changing the Kubernetes password secret does not
change the password inside an already-initialized PostgreSQL data volume. For
production, prefer SOPS/External Secrets or your cloud secret manager.

## 3. Deploy the data services first
```bash
kubectl apply -f infra/kubernetes/base/configmap.yaml
kubectl apply -f infra/kubernetes/base/database.yaml
kubectl apply -f infra/kubernetes/base/redis.yaml

kubectl -n ai-interview-agent rollout status statefulset/interview-postgres --timeout=300s
kubectl -n ai-interview-agent rollout status deployment/interview-redis --timeout=180s
kubectl -n ai-interview-agent get pvc
```

PostgreSQL must be Ready and both PVCs must be Bound before continuing.

## 4. Run schema migration
```bash
kubectl -n ai-interview-agent delete job interview-db-migrate --ignore-not-found
kubectl apply -k infra/kubernetes/migration
kubectl -n ai-interview-agent wait --for=condition=complete job/interview-db-migrate --timeout=300s
kubectl -n ai-interview-agent logs job/interview-db-migrate
```

## 5. Deploy the application
```bash
kubectl apply -k infra/kubernetes/base
kubectl -n ai-interview-agent rollout status deployment/interview-api --timeout=300s
kubectl -n ai-interview-agent rollout status deployment/interview-web --timeout=300s
kubectl -n ai-interview-agent get pods,svc,pvc,ingress,hpa
```

## 6. Notes
- Redis is deployed and configured in `REDIS_URL`; the current application code
  does not yet use Redis in its request path. It is ready for future queue/cache
  features, not a dependency required for interview creation today.
- PostgreSQL StatefulSet has one replica. Do not scale it horizontally.
- Local-path volumes are node-local. A node failure can make data unavailable;
  local-path is not a database backup strategy.
- Back up PostgreSQL using scheduled `pg_dump`/WAL/PITR tooling and test restores.
- The app's `/ready` endpoint checks PostgreSQL, not Redis.
