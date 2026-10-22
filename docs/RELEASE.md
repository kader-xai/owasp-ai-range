# v0.1.0-alpha.1 — local education release

AI Range is an independent, vulnerable-by-design LLM security teaching project
aligned to the OWASP LLM Top 10:2025. Not an official OWASP project or endorsement.

## Included
- Ten focused category scenarios, not exhaustive attack coverage.
- Explanation, challenge, request inspection, ball analogies, and JSON evidence.
- Scripted mode with no model/API key, optional Ollama text and vision inference.
- Synthetic local task/outbox adapters; no real email or SaaS connected.
- Native launch scripts, Dockerfile, and local model Compose option.
- MIT license, contribution guide, security policy, and regression tests.

## Verification for this release
- 33 local unit/integration tests pass.
- Running native server passes health, eleven page routes, and ten scenarios in
  both modes without model calls.
- CI separately builds and launches the non-root read-only container, then runs
  the same smoke test. Check the release commit's actual Actions status before
  treating this as verified container execution.
- Existing text/image model observations are historical, not new benchmark runs.
- Selected-signature scan of reachable text history found no matches before
  release preparation; this limited check is not a full secret audit.

## Known limitations
Localhost only. Do not deploy the application or Ollama on the Internet.
No production authentication, multi-user security, or comprehensive rate limiting.
No arbitrary commands or dangerous model components are executed.
Supply-chain lab uses a prompt bundle, poisoning uses runtime knowledge, retrieval
uses sparse vectors, and resource consumption projects rather than runs overload.
The recorded vision test changed the answer but missed the full marker condition.
Model-stack Docker inference and GPU/vision container execution remain untested.

Start with the README. Do not use real credentials, private documents, or customer data.
