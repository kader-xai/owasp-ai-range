"""LLM04: corpus ingestion with a review gate and persisted activation records."""

import hashlib
import json
from labs.common import definition, start, model_or_preview, finish

BASE = "Reviewed refund policy: 30 days."
DEFINITION = definition(
    4,
    "Knowledge ingestion and answer generation",
    "corpus review before activation",
    "Change a knowledge document, activate it in vulnerable mode, and inspect the resulting answer.",
    BASE,
    "Reviewed refund policy: 900 days.",
    [
        "workspace",
        "candidate revision",
        "review gate",
        "context generation",
        "ingestion transaction",
    ],
    [
        "Runtime knowledge poisoning only, not trained weights or a learned backdoor.",
        "Exact reviewed-release comparison is narrow and rejects legitimate unreviewed changes.",
    ],
    ["offline", "ollama"],
)


def run(store, token, data, generator=None):
    document, defended = start(store, token, data, DEFINITION)
    reviewed = document == BASE
    accepted = not defended or reviewed
    context = (
        {"source_revision": data["revision"], "text": document}
        if accepted
        else {"quarantined": True}
    )
    if not accepted:
        answer, metadata = (
            "Candidate quarantined before model context construction.",
            {"inference": False},
        )
    elif data["backend"] == "offline":
        answer, metadata = (
            document,
            {"inference": False, "type": "active document reader"},
        )
    else:
        answer, metadata, _ = model_or_preview(
            data,
            "Answer only from the active knowledge document.",
            json.dumps(context),
            generator=generator,
            question="What is the refund window?",
        )
    return finish(
        store,
        token,
        data,
        DEFINITION,
        answer,
        metadata,
        {
            "reviewed_release_match": reviewed,
            "active": accepted,
            "violation_applied": accepted and not reviewed,
        },
        [
            {
                "kind": "corpus-ingestion",
                "payload": {
                    "revision": data["revision"],
                    "sha256": hashlib.sha256(document.encode()).hexdigest(),
                    "text": document,
                    "status": "active" if accepted else "quarantined",
                },
            }
        ],
        context,
    )
