#!/bin/sh
# Local n8n (2.x needs Node >= 24); state lives in ./.n8n (gitignored).
cd "$(dirname "$0")/.."
export N8N_USER_FOLDER="$PWD/.n8n" N8N_PORT=5678 GENERIC_TIMEZONE=Europe/Madrid TZ=Europe/Madrid \
  N8N_DIAGNOSTICS_ENABLED=false N8N_VERSION_NOTIFICATIONS_ENABLED=false N8N_SECURE_COOKIE=false \
  N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true LICITA_API=http://127.0.0.1:8787
exec npx n8n start
