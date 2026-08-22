#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Health:"
curl -fsS "$BASE_URL/health"

echo
echo "Metrics:"
curl -fsS "$BASE_URL/metrics" || true

echo
echo "Smoke test passed."
