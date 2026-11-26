#!/usr/bin/env bash
set -Eeuo pipefail

NAMESPACE="ai-interview-agent"

command -v kubectl >/dev/null 2>&1 || { echo "Error: kubectl is required." >&2; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo "Error: openssl is required to generate a secure password." >&2; exit 1; }

kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || {
  echo "Namespace '$NAMESPACE' does not exist. Run this first:" >&2
  echo "  kubectl apply -f infra/kubernetes/base/namespace.yaml" >&2
  exit 1
}

if kubectl -n "$NAMESPACE" get secret postgres-secrets >/dev/null 2>&1 || \
   kubectl -n "$NAMESPACE" get secret interview-secrets >/dev/null 2>&1; then
  echo "Refusing to overwrite existing database/application secrets in '$NAMESPACE'." >&2
  echo "If this is an existing database, keep its current password. Rotate it deliberately instead." >&2
  exit 1
fi

# Hex output is URL-safe, so it can be embedded in DATABASE_URL without encoding.
DB_PASSWORD="$(openssl rand -hex 32)"
GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"

kubectl -n "$NAMESPACE" create secret generic postgres-secrets \
  --from-literal=POSTGRES_DB=interview_agent \
  --from-literal=POSTGRES_USER=interview \
  --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl -n "$NAMESPACE" create secret generic interview-secrets \
  --from-literal=DATABASE_URL="postgresql+psycopg://interview:${DB_PASSWORD}@interview-postgres:5432/interview_agent" \
  --from-literal=GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --from-literal=OPENAI_API_KEY='' \
  --dry-run=client -o yaml | kubectl apply -f -

unset DB_PASSWORD

echo "Created postgres-secrets and interview-secrets in namespace '$NAMESPACE'."
echo "The database password was generated securely and was not printed."
echo "Set GOOGLE_API_KEY before running this script, or update interview-secrets later with your Gemini API key."
