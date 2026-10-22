# Workflow migration status

The public alpha is not equivalent in maturity to established OWASP applications.
This document distinguishes shipped workflows from proposed work. No completion
dates, benchmark outcomes, or finished capabilities are implied by the plan.

| Category | Current architecture | Required next domain workflow |
|---|---|---|
| LLM01 | Workflow: saved attachment → model proposal → transactional refund quote | More cases and repeated model evaluation; multimodal workflow still separate |
| LLM02 | Workflow: session → SQL retrieval → assistant → observation | More customer tasks, lifecycle controls and session management |
| LLM03 | Prototype prompt-bundle digest check | Model/dependency inventory, versioned import and provenance validation |
| LLM04 | Prototype knowledge-ingestion fixture | Versioned corpus ingestion, quarantine/review and retrieval impact |
| LLM05 | Prototype isolated formatting preview | Real message publishing surface with context-aware output handling |
| LLM06 | Prototype in-memory outbox action | Persisted agent job, scoped tool adapter, approvals and action audit |
| LLM07 | Prototype prompt label | Configuration service and reproducible context exposure cases |
| LLM08 | Prototype sparse-vector retrieval | Permission-aware real embedding index and scoped source records |
| LLM09 | Prototype source/value check | Grounded answer lifecycle, evidence verification and review queue |
| LLM10 | Prototype budget planner | Persisted quota/admission service and bounded scheduler |

## Migration gate
Use the same domain workflow and model interface in vulnerable and defended paths.
Only the identified trust-boundary enforcement should differ. The offline option
must say what it actually does, never claim to have inferred an attack outcome.
Every migration needs scoped data, server observations, negative tests, real HTTP
checks, browser QA, and a container smoke check. Guard against unrelated mutations.

## Explicitly not done
No production login, internet-facing deployment, general prompt-injection solution,
unrestricted malicious code execution, paid API integration, or statistical
guardrail benchmark. The original compatibility exercise routes are retained for
existing scripts but do not establish workflow maturity.
