#!/bin/sh
# Read-only Licita API on :8787, using Licita's own Python environment.
cd "$(dirname "$0")/.."
exec uv run --project "${LICITA_HOME:-$HOME/Projects/licita}" python api/server.py
