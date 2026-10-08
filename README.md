# AI Range
Independent educational project aligned to the OWASP LLM Top 10:2025.
Not an official OWASP project or endorsement.

## First milestone
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
Install/start Ollama and download a model separately:
```sh
ollama pull qwen2.5:3b
```
Select Ollama in the UI. Docker uses host.docker.internal; native Python uses localhost.
Configure OLLAMA_MODEL and OLLAMA_URL through the environment as needed.
The app never installs or downloads a model on its own.

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
Build and review one lab at a time. LLM02 sensitive information disclosure is next.
See docs/FRAMEWORK.md for sources and scope.

Local development only. Public hosting is a later milestone after isolation,
session access, abuse prevention, and deployment review.

