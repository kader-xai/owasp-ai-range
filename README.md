# AI Range
Independent educational project aligned to the OWASP LLM Top 10:2025.
Not an official OWASP project or endorsement.

## First milestone
The workspace includes Explanation, Challenge mode, Interception & integrations,
progressive hints, attempt history, JSON export, and a local mock task tool.
See docs/WORKSPACE.md for proxy replay instructions and integration scope.
LLM01 prompt injection: a fictional refund assistant consumes an uploaded document.
Observe a harmless response marker, compare vulnerable and defended source selection,
and inspect the trace. No shell execution, external callbacks, or real private data.

The default backend is explicitly scripted. It teaches the mechanism; it does not
measure real-model robustness. The Ollama backend uses real local inference and may
resist the example. Marker absence is not proof of security.

## Run locally
Requires Python 3.12 or newer. No Python packages needed.
```sh
python3 app.py
```
Open http://127.0.0.1:8088.

## Docker demo
```sh
docker compose up --build -d
```
Open http://127.0.0.1:8088. The published port binds to localhost.
The container runs as a non-root user with a read-only filesystem.

## Optional real local model
Install Ollama from https://ollama.com/download, then start the complete native lab:
```sh
bash scripts/start-local.sh
```
The script downloads the model (about 986 MB on first run), starts Ollama if needed,
and runs the application. Stop an existing app on port 8088 first. Ctrl+C stops
the app and any Ollama daemon started by the script, not a pre-existing daemon.
Select Ollama in the UI. Docker uses host.docker.internal; native Python uses localhost.
Configure OLLAMA_MODEL and OLLAMA_URL through the environment as needed.
The web application itself never installs or downloads a model.
See [local model guide](docs/LOCAL-MODEL.md) for Docker, hardware, and real tests.

## Demo sequence
1. Ordinary document, vulnerable mode: policy summary.
2. Marker document, vulnerable mode: observe whether task redirection occurs.
3. Same document, defended mode: uploaded content is excluded from this narrow task.
4. Explain that architectural source selection prevents this input path, but does
   not solve every prompt-injection scenario or constitute a commercial benchmark.

## Verification
```sh
python3 -m unittest discover -s tests -v
```
Tests cover simulation behavior, validation, and the real backend's source-selection
boundary with a mocked transport. They do not test model robustness.

## Roadmap
All ten categories appear in the UI with explicit planned/implemented status.
Build and review one lab at a time. LLM01 and LLM02 are implemented.
Open http://127.0.0.1:8088/llm02 for the synthetic cross-customer disclosure lab.
See [LLM02 guide](docs/LLM02.md). LLM03 supply chain is next.
See docs/FRAMEWORK.md for sources and scope.

Local development only. Public hosting is a later milestone after isolation,
session access, abuse prevention, and deployment review.
