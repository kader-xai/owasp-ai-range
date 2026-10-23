# Architecture upgrade: workflows, not marker demos

## Quality standard
The public alpha contains bounded workflows and older compatibility experiments. It must not be represented
as having the maturity of established OWASP training applications. A passing marker
or a polished README does not establish realistic vulnerability behavior.

Architecture references (read October 22, 2026):
- [VulnerableApp design](https://sasanlabs.github.io/VulnerableApp/DesignDocumentation.html):
  modular definitions, variants, metadata-driven UI and scanner-facing endpoints.
- [DonkAI](https://github.com/OWASP/DonkAI): category modules, challenge briefs,
  hints, attempt history, and separation of web application and ML service.

These patterns inform original code here; we have not copied their implementation,
inherited their endorsement, or asserted feature parity.

## Target layers

```text
HTTP routes + browser UI
        ↓
learner workspace / challenge definition
        ↓
lab application service
        ↓
domain repository + authorization variant
        ↓
context builder → inference adapter (or explicit offline serializer)
        ↓
server observation → attempt repository → evidence export
```

The deployment safety envelope stays outside the deliberately weak lab boundary.
Adding a lab should not require expanding a central category switch indefinitely.
Migration is incremental; the existing `scenarios.py` and compatibility endpoints
remain prototype infrastructure, not the target module architecture.

## Implemented vertical slice: LLM02 / RangeDesk
- `range_core/store.py`: SQLite schema, isolated workspace seed data, ticket
  queries, append-only API attempt recording (not cryptographically immutable).
- `labs/disclosure.py`: lab definition and support service. No HTTP dependency.
- `support.html`: owned-ticket list, assistant workflow, separate evidence panel,
  stored history, proxy request preview and export.
- `/api/support/start`: issues an opaque HttpOnly, SameSite=Strict workspace cookie.
- `/api/support/workspace`: server principal and owned tickets only.
- `/api/support/chat`: ticket lookup → context → backend → observation → history.
- `/api/support/attempts`: history scoped to the caller's workspace cookie.
- `/api/support/definition`: module metadata and limitations.

Vulnerable repository query intentionally omits `owner = principal`, but never
omits workspace isolation. Defended query includes ownership. Both use parameterized
SQL; teaching disclosure does not require introducing SQL injection.

Offline mode serializes actual query results; changing the question text does not
trigger a canned secret. Ollama receives the same context. A refusal can coexist
with unauthorized retrieval; tests record this distinction. Each workspace gets a
fresh synthetic private reference; observation derives from actual retrieved fields
and actual response, not a hardcoded globally known marker or submitted score.

Sessions provision a demo Alice identity. They are not real login. Workspace tokens
are bearer credentials for synthetic data; do not share exports/cookies casually.
No public multi-user deployment is supported. Capacity is bounded to 500 workspaces
and 200 recorded attempts per workspace. New workspace creation does not delete
prior state. There is no deletion/reset API yet.

## Storage
Default: in-memory SQLite. For native persistence:

```sh
RANGE_DB=./range-workspaces.db python3 app.py
```

The database file is ignored by Git and should contain synthetic data only. Restart
with the same file and browser cookie to resume. A read-only app container can use
the in-memory default. For persistence, explicitly mount a writable directory owned
by container UID 65532 and set RANGE_DB to a file inside it. Do not make the app
filesystem globally writable to accommodate storage. The persistent-volume Docker
configuration has not been execution-tested.

## Migration acceptance gate for every category
1. Real user workflow with meaningful domain objects and state.
2. One clearly identified weak boundary—not “if payload contains marker, win.”
3. Identical business pipeline with a separately enforced defensive policy.
4. Honest offline/model distinction; no fake inference.
5. Server-derived evidence, scoped history, and reproducible fixtures.
6. Unit, repository, HTTP, isolation, invalid-input, and negative tests.
7. Browser verification and Docker smoke verification.

All ten categories now dispatch to domain modules through the registry. The
additional modules use the same saved revisions, workspace isolation and atomic
effect/evidence storage. A persisted event is the application's local effect:
dependency activation, corpus quarantine, publication, job/outbox, configuration
observation, vector-index/retrieval audit, claim review and quota reservation.
No remote side effect or hidden production service is implied.

LLM08 can call real Ollama embeddings; its index is stored as an attempt event.
Offline explicitly uses sparse word-count vectors. LLM06 remains a one-step
structured planner, and LLM10 serial admission runs under the HTTP experiment
semaphore. A production concurrent scheduler is not implemented. See the
[all-ten workflow guide](WORKFLOW-GUIDE.md) and [scope matrix](MIGRATION-ROADMAP.md).

## LLM01 / Refund operations
`labs/refund.py` turns a saved attachment into a structured model proposal. The
authorized task and 30-day policy are server-owned. The attachment is the attacker-
controlled input; it is stored as an immutable per-workspace revision before use.

Vulnerable mode trusts a schema-valid proposal's value and stores a synthetic
quote. Defended mode receives the same context, but the application only accepts
the approved value. Both reject malformed/out-of-bounds proposals. Quote insertion
and attempt insertion occur in one SQLite transaction; a failure rolls back both.
Maximum 3,650 days is an independent fixture bound, not an authorization policy.

The `preview` backend shows actual context with no model call and no quote mutation.
Only real Ollama inference (or injected test adapters in unit tests) generates
proposals. There is no marker trigger or canned vulnerable response in this workflow.

`labs/registry.py` owns workflow definitions and dispatch. `/api/workflows` exposes
metadata; `/api/openapi.json` describes the workflow contract. Additional APIs:
- `POST /api/workflows/attachment`: save content and return a revision.
- `POST /api/workflows/run`: run a registered lab in the caller's workspace.
- `GET /api/workflows/quotes`: list that workspace's applied synthetic quotes.
- `GET /api/workflows/history`: stored attempts from all registered workflows.
- `GET /api/workflows/events`: workspace-scoped domain events with lab and kind.

New workspace cookies use Path=/api so both workflows share a learner session.
An older Path=/api/support cookie may require creating a fresh workspace for new
workflow endpoints. History is not removed by this operation. Default storage is
still in-memory; use RANGE_DB for restart persistence.

The refund workflow's [setup and measured observations](REFUND-WORKFLOW.md) and
the [category migration roadmap](MIGRATION-ROADMAP.md) track what is actually
implemented versus what remains a prototype. No mature-project parity is claimed.
The root catalogue uses API architecture metadata to label workflows and prototypes;
the original LLM01 exercise is retained at `/legacy/llm01` rather than being
presented as the default application.

## Historical validation of the LLM02 slice — October 22, 2026
43 tests passed locally, including the real HTTP cookie/lookup/history path.
Browser checks verified own-ticket baseline, cross-customer offline disclosure,
defended lookup, real Qwen2.5:1.5b disclosure, defended empty context, and export.
The real model returned the workspace-specific billing reference in vulnerable
mode. With ownership filtering it received an empty record list and said it
could not summarize the ticket without access. This is a narrow observed result,
not a model robustness benchmark. Native SQLite reopening is unit-tested;
production auth and persistent Docker storage are not validated.
