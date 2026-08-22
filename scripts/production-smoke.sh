#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:?BASE_URL is required}"
curl -fsS "$BASE_URL/health"
echo
curl -fsS "$BASE_URL/ready"
echo
