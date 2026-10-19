#!/bin/sh
# Freeze the API's answers into static JSON (same shape as the API), so n8n Cloud can read them
# from a public URL. Public PLACSP data only; hospitals are design partners of independent research.
cd "$(dirname "$0")/.."
API=${LICITA_API:-http://127.0.0.1:8787}
for h in ${HOSPITALS:-H-f381}; do
  curl -fsS "$API/radar?hospital=$h&flags=start_now,due_6m,verify&limit=200" > "snapshot/radar_$h.json"
  curl -fsS "$API/deserted?hospital=$h&since=2024-01-01&limit=200" > "snapshot/deserted_$h.json"
done
curl -fsS "$API/health" > snapshot/health.json
ls -la snapshot
