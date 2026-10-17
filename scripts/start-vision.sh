#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OLLAMA_VISION_MODEL="${OLLAMA_VISION_MODEL:-granite3.2-vision:2b}"
command -v ollama >/dev/null || { echo 'Install Ollama from https://ollama.com/download first.'; exit 1; }
if ! curl -fsS "${OLLAMA_URL:-http://127.0.0.1:11434}/api/tags" >/dev/null; then
  echo 'Start Ollama first with ollama serve, then rerun this script.'
  exit 1
fi
OLLAMA_HOST="${OLLAMA_URL:-http://127.0.0.1:11434}" ollama pull "$OLLAMA_VISION_MODEL"
echo "Open http://127.0.0.1:${PORT:-8088}/vision"
python3 app.py
