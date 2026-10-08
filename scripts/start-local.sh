#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b}"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"
command -v python3 >/dev/null || { echo 'Install Python 3 first.'; exit 1; }
command -v ollama >/dev/null || { echo 'Install Ollama from https://ollama.com/download first.'; exit 1; }
daemon_pid=''
cleanup() { if [[ -n "$daemon_pid" ]]; then kill "$daemon_pid" 2>/dev/null || true; fi; }
trap cleanup EXIT
if ! curl -fsS "$OLLAMA_URL/api/tags" >/dev/null; then
  if [[ "$OLLAMA_URL" != 'http://127.0.0.1:11434' ]]; then echo 'Start your configured Ollama service first.'; exit 1; fi
  OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 ollama serve &
  daemon_pid=$!
  for attempt in {1..30}; do
    if curl -fsS "$OLLAMA_URL/api/tags" >/dev/null 2>&1; then break; fi
    sleep 1
  done
fi
OLLAMA_HOST="$OLLAMA_URL" ollama pull "$OLLAMA_MODEL"
echo "Open http://127.0.0.1:${PORT:-8088} and choose Real local model."
python3 app.py
