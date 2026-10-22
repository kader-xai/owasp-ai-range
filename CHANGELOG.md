# Changelog

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
