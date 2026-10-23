"""Teaching metadata, separate from workflow execution and evidence scoring."""

LEARNING = {
    3: {
        "mechanism": "An attacker changes a supplier instruction without changing its release name. If import trusts the name rather than the reviewed content, the changed dependency is activated.",
        "defense": "Compare the canonical digest with a server-owned reviewed release before activation. A digest is not a signature and cannot prove the reference release is safe.",
        "negative_check": "Import the approved baseline defended. Reject malformed manifests in both modes. A model refusing the changed instruction does not undo an unsafe import.",
    },
    4: {
        "mechanism": "An attacker edits a knowledge document before ingestion. The application activates unreviewed information and later uses it as answer context. No weights are trained.",
        "defense": "Quarantine revisions that do not match the reviewed fixture before building model context. This strict release gate also rejects innocent unreviewed edits.",
        "negative_check": "Run the baseline in both modes, then try an innocent edit. Inspect activation/quarantine independently from what the answer says.",
    },
    5: {
        "mechanism": "The application promotes generated text into HTML structure. The same characters can be harmless literal text or interpreted formatting depending on the publication sink.",
        "defense": "Encode output as text at the HTML sink. Both variants keep an independent sandbox and block scripts, links and external loads.",
        "negative_check": "Compare plain text and an h1 heading. Script tags must never execute. Stripped unsupported tags are not scored as interpreted formatting.",
    },
    6: {
        "mechanism": "A support note redirects a summarization planner toward send. The weak adapter confuses a valid model proposal with permission and creates a local outbox entry.",
        "defense": "Authorize only summarize in the execution adapter, independently of the model plan. A valid JSON schema does not grant permission.",
        "negative_check": "Use a normal note and an invalid plan. Preview creates no agent job; only a real valid send proposal can cause the vulnerable outbox effect.",
    },
    7: {
        "mechanism": "A fictional configuration label is placed in system context. The model may repeat it, including while claiming not to reveal internal configuration.",
        "defense": "Keep the label outside model context. This label grants no privileges; prompt wording itself is not a secret-management or authorization system.",
        "negative_check": "Use the ordinary support question first. Inspect label-in-context and actual disclosure separately. Preview is not evidence of model leakage.",
    },
    8: {
        "mechanism": "A shared index ranks a relevant document belonging to another customer. Semantic similarity answers relevance, not authorization.",
        "defense": "Filter source records by server-owned identity before embedding and ranking. Defended embedding input must not include the other customer’s text.",
        "negative_check": "Query Alice delivery first, then Bob billing. Separate unauthorized retrieval from actual answer disclosure. Offline vectors are word counts; Ollama vectors are neural embeddings.",
    },
    9: {
        "mechanism": "A plausible draft is normalized into well-formed JSON, then published without evidence review. A citation label can look real while supporting no such value.",
        "defense": "Check the source/value pair against the trusted registry before publication. Here only policy-v1 with 30 days is supported.",
        "negative_check": "Try the real source name with the wrong value. It must still fail. A deliberately supplied false draft is not proof of spontaneous hallucination.",
    },
    10: {
        "mechanism": "An oversized plan or repeated small plans reserve more inference work than the workspace allowance. A per-request limit alone does not enforce cumulative usage.",
        "defense": "Enforce per-job limits and the cumulative reservation ledger before execution. Keep the separate one-call / 200-output-token safety cap in both modes.",
        "negative_check": "Use fresh workspaces for independent comparisons. The ninth 100-token reservation is denied defended after eight accepted jobs. Projections are not billed tokens.",
    },
}
