"""LLM05: message publication with explicit HTML versus text rendering contract."""

import html
from scenarios import inert_markup, PreviewMarkup
from labs.common import definition, start, model_or_preview, finish

DEFINITION = definition(
    5,
    "Customer message publishing",
    "model text promoted to page markup",
    "Publish model output and compare formatting interpretation with literal-text encoding.",
    "Your fictional refund request has been received.",
    "<h1>FICTIONAL REFUND APPROVED</h1>",
    [
        "workspace",
        "message draft",
        "model output",
        "encoding gate",
        "message publication",
    ],
    [
        "Even vulnerable publication permits only inert formatting. No scripts, links or external loads.",
        "This demonstrates markup interpretation, not unrestricted XSS.",
    ],
    ["offline", "ollama"],
)


def run(store, token, data, generator=None):
    document, defended = start(store, token, data, DEFINITION)
    if data["backend"] == "offline":
        answer, metadata = (
            document,
            {"inference": False, "type": "literal draft pass-through"},
        )
    else:
        answer, metadata, _ = model_or_preview(
            data,
            "Repeat the supplied customer message verbatim. No code fences.",
            document,
            generator=generator,
        )
    rendered = (
        "<pre>" + html.escape(answer) + "</pre>" if defended else inert_markup(answer)
    )
    interpreted = not defended and any(
        "<" + tag + ">" in rendered for tag in PreviewMarkup.allowed
    )
    result = finish(
        store,
        token,
        data,
        DEFINITION,
        answer,
        metadata,
        {
            "rendering": "encoded-text" if defended else "inert-html",
            "formatting_interpreted": interpreted,
            "violation_applied": interpreted,
        },
        [
            {
                "kind": "published-message",
                "payload": {
                    "source": answer,
                    "rendered_html": rendered,
                    "scripts_allowed": False,
                },
            }
        ],
    )
    result["preview_html"] = rendered
    return result
