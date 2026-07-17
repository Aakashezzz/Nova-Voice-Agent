#!/usr/bin/env bash
# One-time setup for backend + frontend.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Setting up backend..."
cd "$ROOT_DIR/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
deactivate

echo "==> Setting up frontend..."
cd "$ROOT_DIR/frontend"
npm install

echo ""
echo "Setup complete."
echo "Next: pull an Ollama model and download a Piper voice — see docs/INSTALLATION.md"
echo "Then run: scripts/run_backend.sh and scripts/run_frontend.sh (in separate terminals)"
