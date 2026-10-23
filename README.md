# AI Range for LLM Security

[![Tests and container smoke](https://github.com/kader-xai/owasp-ai-range/actions/workflows/tests.yml/badge.svg)](https://github.com/kader-xai/owasp-ai-range/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A local, vulnerable-by-design practice range aligned to the **OWASP LLM Top 10:2025**.
Learn the failure, inspect the boundary, apply a focused defense, and retest.

**Maturity:** educational alpha, not feature- or quality-parity with mature OWASP
applications. All ten categories have separate domain workflow modules, isolated
learner workspaces and server-recorded evidence. Each is a bounded slice of a
risk, not exhaustive coverage or a statistically validated benchmark.

> **Intentionally vulnerable. Localhost and synthetic data only.** Do not expose
> this app or Ollama to the Internet. Independent project; not an official OWASP
> project, certification or endorsement.

## Start locally

```sh
git clone https://github.com/kader-xai/owasp-ai-range.git
cd owasp-ai-range
python3 app.py
```

Requires Python 3.12+, with no Python packages required. Open
**http://127.0.0.1:8088**. Offline options execute the named non-model component;
preview performs no inference. Compatibility exercises remain explicitly scripted.
The web app never downloads models.

For real local inference, install [Ollama](https://ollama.com/download), stop the
running app and run `bash scripts/start-local.sh`. The text default is Qwen2.5:1.5b.
LLM08 optionally uses `nomic-embed-text:latest` for real embeddings; the separate
image lab uses granite3.2-vision:2b. See [model setup](docs/LOCAL-MODEL.md).
Models retain their own training and may refuse examples; no model is claimed to
have zero guardrails.

## Ten workflow tracks

| Category | Application workflow | Boundary and limitation |
|---|---|---|
| [LLM01 Prompt Injection](docs/REFUND-WORKFLOW.md) | Saved attachment → model proposal → transactional refund quote | Policy enforcement; image experiment not yet integrated here |
| [LLM02 Sensitive Information Disclosure](docs/LLM02.md) | SQL lookup → assistant → observed disclosure | Customer ownership; fixed synthetic identity, not production login |
| LLM03 Supply Chain | Dependency import → reviewed digest → activation | Inert JSON prompt dependency, not signed model weights |
| LLM04 Data and Model Poisoning | Corpus revision → review/quarantine → context | Runtime knowledge integrity, not training or learned backdoors |
| LLM05 Improper Output Handling | Draft → output → publication | Inert HTML versus encoded text, not unrestricted XSS |
| LLM06 Excessive Agency | Model plan → tool authorization → local outbox | One-step planner, no real email/SaaS calls |
| LLM07 System Prompt Leakage | Configuration → model → label observation | Synthetic label, not a credential or authorization token |
| LLM08 Vector and Embedding Weaknesses | Owned records → vectors → ranking → audit | Sparse or real Ollama embeddings; no inversion |
| LLM09 Misinformation | Claim → source registry → review → publication | Narrow factual contract, not universal fact checking |
| LLM10 Unbounded Consumption | Job plan → cumulative quota → bounded executor | Projected reservations, never actual overload/wallet charges |

Read the [workflow guide](docs/WORKFLOW-GUIDE.md) for simple attack explanations,
baseline/attack/defense checks, proof requirements and category-specific exclusions.
The root catalogue links to `/llm01`, `/llm02` and `/workflows/LLM03`–`LLM10`.
The old `/legacy/llm01` and `/labs/LLM03`–`LLM10` remain compatibility exercises.

## Repeatable learning loop

1. Create a workspace. Save baseline input as an immutable revision.
2. Run the ordinary task; inspect model output and stored application effect.
3. Save a controlled example. Run both modes on that same revision.
4. Compare the authorization/review decision, effect, and server observation.
5. Try a negative case; export evidence and explain what it does **not** prove.

LLM01 preview makes no quote and LLM06 preview makes no agent job. Use Ollama for
actual proposals. Offline paths are real serializers/validators/renderers, not
claims of inference. Refusal and blocked application effects are separate outcomes.

## Docker

App against host Ollama:

```sh
docker compose up --build -d
```

Complete CPU text-model stack:

```sh
docker compose -f compose.local-model.yaml up --build -d
docker compose -f compose.local-model.yaml logs -f model-setup
```

Only the app port binds to localhost. The app container is non-root and read-only.
The complete model stack can be slower than native Metal on Mac. Optional embedding
and vision downloads are documented separately; they are not silently installed.
Docker model inference and GPU container paths require separate environment testing.

## Evidence and verification

```sh
python3 -m unittest discover -s tests -v
python3 scripts/smoke-http.py http://127.0.0.1:8088
```

Tests cover HTTP sessions, invalid input, workspace isolation, real SQLite queries,
atomic effect/evidence rollback, quota admission and mocked inference contracts.
They do not establish model robustness. CI tests Python 3.12/3.13/3.14 and builds
a non-root read-only container for an offline HTTP smoke test.

Default storage is in-memory. For native persistence:

```sh
RANGE_DB=./range-workspaces.db python3 app.py
```

Keep the cookie and database private. Workspace bearer tokens provision a fixed
demo customer, not production authentication. No public hosting is supported.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) · [Scope and next milestones](docs/MIGRATION-ROADMAP.md)
- [All-ten workflow guide](docs/WORKFLOW-GUIDE.md) · [Model setup](docs/LOCAL-MODEL.md)
- [Image experiment](docs/VISION.md) · [Proxy replay](docs/WORKSPACE.md)
- [Earlier prototype observations](docs/EXPERIMENT-VERIFICATION.md)
- [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)
- [Workflow API](http://127.0.0.1:8088/api/openapi.json)
