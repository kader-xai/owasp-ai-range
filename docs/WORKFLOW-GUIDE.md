# Ten boundaries, ten local workflows

Aligned to the [OWASP LLM Top 10:2025](https://genai.owasp.org/llm-top-10/).
These are original, synthetic teaching scenarios—not reproductions of reported
breaches. Category descriptions below are paraphrased; implementation scope is
deliberately narrower than OWASP's full risk descriptions.

## The experiment contract

Start at `/`, create a workspace, run baseline, save a controlled example, compare
both variants on the same saved revision, inspect the effect and export evidence.
Do not treat a changed sentence, refusal or challenge marker as a full verdict.
Record inputs, model/version, options, mode, context, proposal, boundary decision,
stored effect and timestamp. Offline means the named actual non-model component;
preview means no inference. Neither is evidence of model susceptibility.

Use browser Network tools, Burp or ZAP to replay requests to localhost only. Keep
the HttpOnly workspace cookie and immutable revision; see the request preview and
`/api/openapi.json`. Never use production accounts or imported private documents.

## LLM01 — A document becomes an unauthorized refund proposal

**Mechanism:** instructions in an untrusted attachment compete with the authorized
task. The serious failure is the application accepting an unauthorized value, not
merely the model repeating text. The attacker controls an attachment, not policy.

**Workflow:** `/llm01`, `labs/refund.py`. A saved revision enters real Ollama
inference. A schema-valid proposal can become a synthetic refund quote. Both modes
use the same input and schema. Defended mode additionally enforces the server's
30-day policy before the quote transaction.

**Try:** baseline → inspect 30 days. Controlled attachment → inspect the actual
proposed value, then any stored quote. Reuse that revision in defended mode.
**Negative check:** malformed or out-of-range proposals must never create quotes.
**Evidence:** proposal, policy decision, quote ID and stored attempt. Quote and
attempt insertion roll back together. Model output may resist the example.

**Excludes:** universal injection detection, a payment system, or an image-driven
quote. The separate `/vision` experiment uses a real vision model; earlier image
redirection missed its full exact marker. Do not present that as complete success.
[OWASP source](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).

## LLM02 — The assistant receives another customer's ticket

**Mechanism:** missing ownership enforcement supplies unauthorized records to the
model. A prompt asking it to keep secrets does not replace record authorization.
The attacker selects a ticket ID while the server identity stays Alice.

**Workflow:** `/llm02`, `labs/disclosure.py`. Both variants query SQLite with
parameters and workspace isolation. Vulnerable mode omits customer ownership;
defended mode filters ownership before context construction. Offline serializes
actual returned rows; Ollama summarizes those same rows.

**Try:** own A-101 baseline, then Bob's B-202, then B-202 defended.
**Negative check:** changing a request principal must not change the server identity;
a second workspace must not see the first workspace's records or history.
**Evidence:** retrieved IDs/owners and actual private-reference disclosure are
separate observations. A refusal after an unauthorized lookup still leaves a
retrieval failure. Per-workspace private references are randomly seeded.

**Excludes:** membership inference, model extraction and production authentication.
[OWASP source](https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/).

## LLM03 — An unreviewed dependency is activated

**Mechanism:** a supplier name/version is treated as proof of integrity. A changed
dependency reaches deployment without checking the reviewed release.

**Workflow:** `/workflows/LLM03`, `labs/supply.py`. Import an inert JSON manifest
with supplier, version and system instruction. The application computes a canonical
SHA-256 digest. Vulnerable mode activates a changed bundle; defended mode compares
against a server-owned pinned digest before activation or inference.

**Try:** import the baseline, then the changed 900-day instruction under the same
version. Reuse it defended. **Negative check:** unknown fields and malformed JSON
are rejected in both variants; the reviewed release remains usable defended.
**Evidence:** manifest, received/pinned digest and activation decision in a
`dependency-import` event. Offline inspects the real manifest, not a fake answer.

**Excludes:** malicious model weights, package malware, unsafe deserialization,
signed attestations and a complete AI bill of materials. A digest does not prove
that its reference release is safe or authentic.
[OWASP source](https://genai.owasp.org/llmrisk/llm032025-supply-chain/).

## LLM04 — Unreviewed knowledge becomes active context

**Mechanism:** changing a source before ingestion corrupts the information later
used to answer. This can overlap with retrieval manipulation, but it is not
automatically a change to trained model weights.

**Workflow:** `/workflows/LLM04`, `labs/poisoning.py`. A saved knowledge revision is
reviewed, activated or quarantined, then used as answer context. Vulnerable mode
activates the changed 900-day fixture. Defended mode requires the exact reviewed
30-day release. Quarantined candidates never enter the model context.

**Try:** baseline in both modes; changed policy in both modes. **Negative check:**
even an innocent unreviewed edit is quarantined—this is a strict release gate, not
a semantic poison detector. **Evidence:** revision, hash, text, active/quarantined
status and actual answer. Offline is an active-document reader.

**Excludes:** training poisoning, a learned trigger/backdoor and a realistic large
corpus review process. The stored ingestion event documents this one activation;
it is not a shared production knowledge service.
[OWASP source](https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/).

## LLM05 — Generated text is promoted into page structure

**Mechanism:** the downstream sink interprets output instead of treating it as
untrusted data. The correct defense depends on the sink, not on model politeness.

**Workflow:** `/workflows/LLM05`, `labs/output.py`. A draft is passed through offline
or repeated by Ollama. Vulnerable publication interprets allowlisted inert HTML;
defended publication HTML-encodes it as literal text. A publication event stores
the source and rendered form. The browser preview is sandboxed with no external
loads or scripts even in vulnerable mode.

**Try:** plain message baseline, then the heading example. Compare the preview and
stored HTML. **Negative check:** script/link content must never execute or load a
remote resource. **Evidence:** actual publication mode and formatting interpretation.

**Excludes:** unrestricted XSS, SQL injection, SSRF and command execution. Do not
describe the heading-formatting fixture as a working arbitrary-XSS exploit.
[OWASP source](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/).

## LLM06 — A model plan is mistaken for permission

**Mechanism:** a summarizer has an unnecessary write capability, and the adapter
executes an action based solely on the model's proposed plan.

**Workflow:** `/workflows/LLM06`, `labs/agency.py`. Real Ollama returns structured
`summarize` or `send` JSON. Both paths validate the schema. Vulnerable mode can
append a local-outbox event for `send`; defended mode independently authorizes
only `summarize`. The plan and any outbox effect commit with the attempt.

**Try:** ordinary support note, then the controlled send request embedded in the
note. Compare proposed action and actual outbox, not only prose. **Negative check:**
invalid plans have no send effect; preview never invokes the adapter.
**Evidence:** `agent-job`, `local-outbox`, authorization decision and zero external
calls. If the real model chooses summarize, report that result—no send is invented.

**Excludes:** real mail, SaaS tokens, autonomous multi-step agents, human approval
queues and an installed orchestration framework. This is a one-step local planner.
[OWASP source](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/).

## LLM07 — Sensitive configuration is placed in model context

**Mechanism:** the model can repeat information it was given. An instruction to
hide it is not a secret-management or authorization boundary.

**Workflow:** `/workflows/LLM07`, `labs/prompt.py`. Vulnerable context includes a
workspace-specific fictional routing label. Defended context omits it. Only actual
Ollama output can establish disclosure; preview exposes context for inspection but
does not score a model leak.

**Try:** ask the ordinary policy question, then the controlled configuration
question in both modes. **Negative check:** label disclosure grants no privileges
and must not let a client change identity. **Evidence:** whether the label was
submitted and whether it appeared in the actual response; persisted observation.

**Excludes:** real secrets, credentials and privilege escalation. Public prompt
wording by itself is not automatically a security failure; the sensitive content
and downstream trust decisions determine impact.
[OWASP source](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/).

## LLM08 — Semantic relevance is confused with permission

**Mechanism:** a shared index returns a relevant but unauthorized document. Vector
similarity is a ranking signal, not an access-control decision.

**Workflow:** `/workflows/LLM08`, `labs/retrieval.py`. Three synthetic SQLite records
become an index. Defended mode applies ownership before vector generation/ranking.
Offline uses transparent word-count vectors and cosine similarity. Ollama uses
real `/api/embed` vectors plus a separate generation model. Pull the optional
embedding model first; see the model guide.

**Try:** Alice delivery baseline, then Bob billing query, both modes. **Negative
check:** defended embedding requests must not even contain Bob's source text.
**Evidence:** indexed IDs, vectors, model/dimension, ranking scores, selected IDs,
unauthorized retrieval and actual answer disclosure. The index and retrieval audit
are saved per attempt; there is no hidden production vector database.

**Excludes:** embedding inversion, a persistent approximate-nearest-neighbor service
and a large-scale RAG benchmark.
[OWASP source](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/).

## LLM09 — An unsupported claim is published as policy

**Mechanism:** well-formed, credible-looking output is trusted without checking
its evidence. A citation string is not proof that the cited source supports it.

**Workflow:** `/workflows/LLM09`, `labs/claims.py`. Offline parses an actual draft
or Ollama normalizes it into structured JSON. The application reviews it against
a server-owned registry: policy-v1 supports exactly 30 days. Vulnerable mode
publishes any valid bounded claim; defended mode publishes only a supported pair.

**Try:** supported baseline, then 47 days / policy-v99. **Negative check:** a real
source name paired with the wrong value must still fail review. **Evidence:**
schema validity, support decision, `claim-review` and optional `published-claim`.

**Excludes:** universal factual correctness, adjudication across open-web sources
and proof of spontaneous model hallucination. The misleading fixture is supplied
on purpose to isolate the publication control.
[OWASP source](https://genai.owasp.org/llmrisk/llm092025-misinformation/).

## LLM10 — Work is admitted without enforcing its budget

**Mechanism:** a job plan or repeated small jobs reserve more work than the
application's allowance. Limiting one request is not a cumulative workspace quota.

**Workflow:** `/workflows/LLM10`, `labs/budget.py`. Plans specify calls and output
tokens per call. Defended admission limits calls (2), tokens/call (200), per-job
projection (400) and cumulative reservations (800). Vulnerable admission ignores
those policy limits. Independent fixture safety always caps actual inference at
one call and 200 output tokens. Offline runs zero model calls.

**Try:** small baseline, oversized plan, then cumulative small jobs. Use separate
fresh workspaces for independent comparisons because admitted jobs reserve quota.
**Negative check:** malformed/bool/negative values reject in both modes; a defended
ninth 100-token reservation is denied after eight accepted ones. **Evidence:**
prior ledger total, projected tokens, admission, hard caps and actual call count.

**Excludes:** real DoS, load generation, a paid bill and a concurrent scheduler.
The HTTP server serializes active experiments; reservations are not measured usage.
[OWASP source](https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/).
