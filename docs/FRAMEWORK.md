# Framework and implementation plan
Verified October 8, 2026 against the official OWASP catalogue, which displays the
2025 LLM Top 10. Version mappings are pinned to that edition.

Source: https://genai.owasp.org/llm-top-10/
First category: https://genai.owasp.org/llmrisk/llm01-prompt-injection/

| ID | Category | Status |
| --- | --- | --- |
| LLM01 | Prompt Injection | First teaching lab implemented |
| LLM02 | Sensitive Information Disclosure | Planned |
| LLM03 | Supply Chain | Planned |
| LLM04 | Data and Model Poisoning | Planned |
| LLM05 | Improper Output Handling | Planned |
| LLM06 | Excessive Agency | Planned |
| LLM07 | System Prompt Leakage | Planned |
| LLM08 | Vector and Embedding Weaknesses | Planned |
| LLM09 | Misinformation | Planned |
| LLM10 | Unbounded Consumption | Planned |

OWASP is a risk taxonomy, not a simulator. The implementation teaches one scenario
per selected category; a lab cannot demonstrate every possible variant.
Agentic Top 10 is a separate taxonomy and should be added explicitly later.

For each milestone: explain normal behavior, reproduce a synthetic failure,
identify its cause, add a bounded defense, and retest. Keep simulator results
separate from real-model evaluations. Track model version and repeated outcomes
before claiming benchmark findings.

This first defense removes document context for an approved-policy-only task.
It sacrifices arbitrary document summarization to enforce a specific boundary.
Sources and examples are teaching material; no novel attack is claimed.

