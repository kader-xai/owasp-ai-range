# Security policy and threat model

## Intended deployment
Local education on a single operator's computer. Use fictional data. Bind the
published app port to loopback; never publish Ollama or the range on the Internet.
The code intentionally models unsafe application decisions. A public repository
does not imply the vulnerable application is suitable for public hosting.

There is no production authentication, multi-user isolation, durable audit store,
distributed rate limiter, or security certification. Alice is a fixed server-side
teaching identity. Review tasks are unverified observations in process memory.

## Boundaries retained in both teaching modes
- Local Host/Origin validation and cross-site fetch rejection reduce browser-origin
  attacks and DNS-rebinding exposure. Non-browser proxy replays are allowed only
  with a localhost Host header. This is not authentication.
- Request size limits, 15-second socket read timeout, 16 HTTP workers, and one
  experiment at a time bound local work. Excess workers are disconnected.
- Model generation is bounded. LLM10 never executes its projected large workload.
- No shell execution, arbitrary downloads, real outbound messaging, or real secrets.
- HTML preview permits only inert formatting, with sandbox and restrictive CSP.
- Image input has size/signature checks and PNG dimension checks. It is **not**
  a hardened image-decoding/upload service. Use only the supplied or trusted
  synthetic fixtures. An inference client timeout is not a guarantee of immediate
  cancellation inside an external model runtime.

OLLAMA_URL and model settings are trusted operator configuration—not user-facing
URL parameters. Point only to your own trusted local/runtime service. Docker's
internal Ollama address is configured separately from browser-facing Host checks.

## Reporting
For a defect in the range's safety envelope, use GitHub's private vulnerability
reporting when available: repository Security → Report a vulnerability. If private
reporting is unavailable, open an issue requesting a private contact **without
exploit details or sensitive data**. Do not post real keys or personal records.
Expected behavior inside a clearly labeled vulnerable lab is not itself a newly
discovered vulnerability in the project or underlying model.

Only the latest alpha is maintained, on a best-effort basis. No response-time or
remediation SLA is promised. Never test against third-party systems without permission.
