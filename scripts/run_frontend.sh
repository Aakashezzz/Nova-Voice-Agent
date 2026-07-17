#!/usr/bin/env bash
# Starts the Vite dev server for the frontend.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/frontend"
npm run dev
