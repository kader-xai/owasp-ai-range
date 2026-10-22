# Changelog

## Unreleased — workflow architecture migration
- LLM02 RangeDesk: SQLite ticket repository, isolated server-owned workspaces,
  domain service, offline record serializer / Ollama adapter, and stored attempts.
- Authorization and answer disclosure measured separately; random per-workspace
  private fields replace a globally hardcoded success marker in this workflow.
- 43 tests including real HTTP sessions, storage reopening, isolation, identity
  override rejection, and model refusal without concealing retrieval failure.
- Existing alpha remains a prototype. Other labs are not yet migrated.

## v0.1.0-alpha.1 — 2026-10-22

First public-source alpha: ten focused OWASP LLM Top 10:2025 experiments and an
optional real local image-input scenario. Explanation/challenge/replay workflows,
ball analogies, synthetic fixtures, JSON export, and local review tasks.

### Release preparation
- Local Host/Origin and cross-site request checks; JSON framing and body limits.
- Bounded HTTP workers and single active experiment.
- Real HTTP integration tests and scripted smoke tests across all categories.
- CI Python 3.12/3.13/3.14 matrix and non-root read-only Docker startup smoke test.
- MIT license, security policy, contribution guide, issue/PR templates, coverage
  limitations, and explicit independent-project branding.

### Known limits
Local-only alpha. No production authentication or Internet-hosting support.
Supply-chain lab uses inert prompt bundles; poisoning does not modify weights;
retrieval uses sparse vectors; consumption projects rather than executes overload.
Image experiments showed influence but missed the exact full target marker.
Historical real-model observations are not performance guarantees or benchmarks.
Docker model-stack inference and GPU/vision container runtime need separate testing.
