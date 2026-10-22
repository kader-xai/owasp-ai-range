# Challenge workspace

Inspired by https://owasp.org/projects/vulnerableapp and
https://sasanlabs.github.io/VulnerableApp/ . Original interface and code.

Explanation introduces the scenario, objective, weak boundary, and defense.
Challenge mode includes progressive hints, inputs, modes, trace, browser-session
history, and JSON export. Interception view displays actual request and response.

Use Burp's browser or a ZAP-configured browser on http://127.0.0.1:8088.
Ensure loopback traffic uses the proxy. Capture POST /api/run, edit the synthetic
document field, and replay in Repeater or the request editor. No custom extension
is installed. External replays do not update browser history. Conventional scans
and model-safety evaluation are different tasks.

POST /api/tasks accepts mode, backend, boolean attack_observed, and an optional
lab ID (defaults to LLM01:2025). It returns a
local in-memory review task. GET /api/tasks lists tasks. These are client-submitted
observations, not validated security findings. No SaaS calls occur. Restart clears
tasks; capacity is 1000. Real integrations require a chosen provider and scope.

All ten categories have focused experiments. Optional image input uses /vision and
a separately installed local vision model. Scripted
mode is labeled. Ollama requires a real model service. Docker app startup and
scripted smoke tests passed in GitHub CI on October 22, 2026; container-hosted
model inference and GPU/vision execution remain unverified. See RELEASE.md.
