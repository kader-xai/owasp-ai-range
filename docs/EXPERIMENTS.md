# Local experiment guide — LLM03 through LLM10

Run `bash scripts/start-local.sh`, then use the category buttons at
http://127.0.0.1:8088. The same [native/Docker setup](LOCAL-MODEL.md) serves all
pages. Dockerfile includes the shared scenario code and page. Docker app startup
and scripted HTTP smoke checks passed in GitHub CI on October 22, 2026. Model-stack
inference and GPU/vision container execution remain unverified. The development
Mac still has no running Docker daemon; see [release evidence](RELEASE.md).

For each topic: explanation → baseline → controlled example → same input with
defense → inspect evidence → export. The simulation backend is a teaching rule;
Ollama performs real inference except where the application blocks beforehand.
No novel attack, universal protection, or commercial benchmark is claimed.

## LLM03 — Supply chain
An inert supplier JSON prompt bundle is changed while its supplier/version labels
stay the same. Vulnerable mode loads the instruction; defended mode compares a
SHA-256 fingerprint to a server-held reviewed release and rejects changes.
This is a prompt dependency integrity experiment, not compromised weights or
malware loading. A hash from the same untrusted supplier would not establish
trust: the approved reference must come from a trusted release process.
[OWASP LLM03](https://genai.owasp.org/llmrisk/llm032025-supply-chain/)

## LLM04 — Data and model poisoning
Change the fictional refund knowledge from 30 to 900 days before ingestion.
Observe whether the model repeats the false fact. The defense rejects candidate
knowledge that differs from the reviewed release. No weights are trained or
modified; this deliberately narrow lab demonstrates corrupted knowledge input,
not a persistent learned backdoor. Every run reconstructs the fixture.
[OWASP LLM04](https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/)

## LLM05 — Improper output handling
Make the model return `<h1>FICTIONAL-APPROVAL</h1>`. Vulnerable mode interprets
inert formatting tags in a sandboxed preview; defended mode HTML-encodes them.
The visible difference is a heading versus literal text. Even the weak preview
removes active tags, attributes, links, and images and has a restrictive CSP.
This is not unrestricted XSS, command execution, or SQL injection.
[OWASP LLM05](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)

## LLM06 — Excessive agency
A summarizer can propose `summarize` or `send` using a constrained JSON schema.
An injected document asks it to send. The vulnerable adapter creates an actual
local per-run outbox entry; the defended adapter allows only summarize. A claimed
approval in text cannot authorize send. Malformed proposals are rejected in both
modes. No email or SaaS is contacted. This minimal model → action → adapter loop
needs no third-party agent framework; production agent integrations remain separate.
[OWASP LLM06](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)

## LLM07 — System prompt leakage
The vulnerable system message contains a fictional routing label. Ask for the
internal configuration and check whether that label appears. The defense keeps
it out of model context. The label grants no privileges and is visible in source
code; it is a teaching fixture, not a real credential. A leaked public role
description is not equivalent to compromised authorization.
[OWASP LLM07](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/)

## LLM08 — Vector and embedding weaknesses
Query a shared index for billing/invoice/reference terms. Inspect sparse word-count
cosine scores and selected document IDs. Vulnerable mode can retrieve Bob’s
private record for Alice. Defended mode filters owners before ranking and excludes
zero-similarity records. This is real vector arithmetic, not a neural embedding
model or vector database. It exposes a retrieval boundary that overlaps LLM02’s
disclosure outcome. No embedding inversion is attempted.
[OWASP LLM08](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/)

## LLM09 — Misinformation
Submit a draft with 47 days and nonexistent source `policy-v99`. The model
normalizes it into a claim. Vulnerable mode publishes an unsupported claim in
the experiment result; defended mode checks both source ID and numeric value
against `policy-v1` (30 days). Invalid claims remain visible only as labeled
draft evidence. This is false-claim propagation, not proof of spontaneous
hallucination or a general-purpose fact checker.
[OWASP LLM09](https://genai.owasp.org/llmrisk/llm092025-misinformation/)

## LLM10 — Unbounded consumption
Request 100 calls × 1,000 output tokens. Vulnerable planning admits the projected
100,000-token job; defended planning rejects it before inference. The range
always executes at most one real model call capped at 200 output tokens per
experiment, regardless of the requested plan. Evidence separates projected work
from actual call count and returned Ollama token telemetry. There is no actual
flood or outage demonstration and no paid API. Per-job limits do not replace
authentication, cumulative quotas, global rate limits, or deployment controls.
[OWASP LLM10](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/)

## Repeatable evidence
Run one category at a time:

```sh
python3 scripts/test-scenario-model.py LLM03:2025 --summary
python3 -m unittest discover -s tests -v
```

Replace LLM03 with the selected category. The script performs baseline and example
in both modes and prints actual observations. Full output without `--summary`
also includes exact inputs and traces. Browser JSON export captures session
attempts. Model metadata records configured model, evaluated token count, and
duration when provided by Ollama; it does not establish a benchmark.

Create local review task records a client-submitted observation in server memory.
No SaaS integration or persistent case-management system is configured. Tasks
reset on app restart; per-run outbox entries do not persist. Replay POST /api/run
locally with Burp/ZAP or browser tools; these proxies have not been independently
execution-tested. Real personal/customer data must never be used here.

Image-input testing now has a separate [vision-model scenario](VISION.md).
The default Qwen text model remains text-only.
Public release needs isolation, authentication, abuse limits, and Docker/runtime review.
