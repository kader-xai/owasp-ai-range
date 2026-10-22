# Contributing

Use small, reviewable changes. Explain which OWASP LLM Top 10:2025 risk and trust
boundary the change teaches. This project is independent of OWASP.

## Local checks
Python 3.12+ and the standard library are sufficient:

```sh
python3 -m unittest discover -s tests -v
python3 app.py
```

In another terminal: `python3 scripts/smoke-http.py http://127.0.0.1:8088`.
Do not run a second app on an occupied port. Docker CI builds and starts a
non-root, read-only container and repeats the smoke checks without Ollama.

## A new lab must include
1. Intended behavior and a minimal synthetic scenario.
2. A bounded vulnerable path and independently enforced defensive boundary.
3. Explanation, hint, visible evidence, and export support.
4. Tests of the actual boundary, including invalid input and failed attempts.
5. Explicit distinction between scripted behavior and real model inference.
6. Sources, model configuration, scope limitations, and reproducible observations.

Never add real credentials/customer records, unrestricted execution, external
exfiltration callbacks, uncontrolled loops, or silently paid API dependencies.
Do not turn a one-off model outcome into an attack-success-rate claim. Keep safety
controls independent of teaching-mode controls. Preserve existing unrelated changes.

## Pull requests
Describe the scenario, changes, tests, and limitations. Mark untested Docker/GPU/
model paths explicitly. New dependencies need justification and license review.
Do not commit local evidence containing private images or personal data. Original
contributions are submitted under this repository's MIT license; third-party
models, documentation, and trademarks retain their own terms.
