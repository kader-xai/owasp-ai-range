"""Shared validation and transaction envelope; category logic stays in modules."""

import json
from scenarios import infer
from labs.learning import LEARNING


def start(store, token, data, definition):
    store.ensure_capacity(token)
    if (
        data.get("mode") not in ("vulnerable", "defended")
        or data.get("backend") not in definition["backends"]
    ):
        raise ValueError("Invalid variant or backend")
    document = store.read_attachment(token, data.get("revision"))
    return document, data["mode"] == "defended"


def model_or_preview(
    data,
    system,
    context,
    schema=None,
    generator=None,
    question="Process the supplied application data.",
):
    if data["backend"] == "preview":
        return (
            "Context preview only. No inference or domain mutation.",
            {"inference": False},
            None,
        )
    answer, metadata = (generator or infer)(
        system, question, context, json_mode=schema or False
    )
    parsed = None
    if schema:
        try:
            parsed = json.loads(answer)
        except (ValueError, TypeError):
            pass
    return answer, metadata, parsed


def finish(
    store, token, data, definition, answer, metadata, evidence, events=(), context=None
):
    result = {
        "lab": definition["id"],
        "mode": data["mode"],
        "backend": data["backend"],
        "answer": answer,
        "model_metadata": metadata,
        "observation": evidence,
        "attack_observed": bool(evidence.get("violation_applied", False)),
        "workflow_stages": definition["stages"],
        "trace": [
            {"stage": "saved-input", "revision": data.get("revision")},
            {"stage": "backend", "inference_ran": bool(metadata.get("model"))},
            {"stage": "boundary-observation", "details": evidence},
            {
                "stage": "committed-effects",
                "event_kinds": [event["kind"] for event in events],
            },
        ],
    }
    if context is not None:
        result["context_preview"] = context
    result["attempt_id"] = store.complete(
        token,
        {k: data[k] for k in ("lab", "revision", "mode", "backend") if k in data},
        result,
        events=events,
    )
    return result


def definition(
    number,
    title,
    boundary,
    objective,
    baseline,
    example,
    stages,
    limitations,
    backends=None,
):
    return {
        "id": f"LLM{number:02d}:2025",
        "architecture": "workflow-v1",
        "title": title,
        "boundary": boundary,
        "objective": objective,
        "baseline": baseline,
        "example": example,
        "stages": stages,
        "limitations": limitations,
        "variants": ["vulnerable", "defended"],
        "backends": backends or ["preview", "ollama"],
        **LEARNING.get(number, {}),
    }
