#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_KEY_HEADER=""
if [[ -n "${API_KEY:-}" ]]; then
  API_KEY_HEADER=(-H "X-API-Key: ${API_KEY}")
else
  API_KEY_HEADER=()
fi

echo "== Health =="
curl -sS "${BASE_URL}/api/v1/health" | jq .

echo "\n== Verify Single =="
curl -sS -X POST "${BASE_URL}/api/v1/verify" \
  -H "Content-Type: application/json" \
  "${API_KEY_HEADER[@]}" \
  -d '{"email":"user@example.com"}' | jq .

echo "\n== Verify Bulk =="
curl -sS -X POST "${BASE_URL}/api/v1/verify/bulk" \
  -H "Content-Type: application/json" \
  "${API_KEY_HEADER[@]}" \
  -d '{"emails":["user@example.com","support@example.com","fake@mailinator.com"]}' | jq .
