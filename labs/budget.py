"""LLM10: cumulative persisted admission accounting with independent hard cap."""

import json
from labs.common import definition, start, finish

LIMIT = 800
DEFINITION = definition(
    10,
    "Inference job budget admission",
    "per-job and cumulative workspace quota",
    "Exceed the workspace’s cumulative projected budget and compare admission decisions.",
    '{"calls":1,"tokens_per_call":100}',
    '{"calls":100,"tokens_per_call":1000}',
    [
        "workspace",
        "job plan",
        "quota ledger",
        "admission policy",
        "bounded executor",
        "usage transaction",
    ],
    [
        "Requested work is projected. The executor always runs at most one call of 200 output tokens.",
        "Reservations are not billed tokens. No overload, wallet charge, or service outage is attempted.",
    ],
    ["offline", "ollama"],
)


def run(store, token, data, generator=None):
    document, defended = start(store, token, data, DEFINITION)
    plan = json.loads(document)
    if (
        not isinstance(plan, dict)
        or set(plan) != {"calls", "tokens_per_call"}
        or any(type(plan[k]) is not int or not 1 <= plan[k] <= 10000 for k in plan)
    ):
        raise ValueError("Invalid job plan")
    projected = plan["calls"] * plan["tokens_per_call"]
    used = sum(
        e["payload"]["reserved_tokens"]
        for e in store.events(token, DEFINITION["id"])
        if e["kind"] == "budget-reservation"
    )
    exceeds = (
        plan["calls"] > 2
        or plan["tokens_per_call"] > 200
        or projected > 400
        or used + projected > LIMIT
    )
    admitted = not defended or not exceeds
    metadata = {"inference": False}
    answer = "Job rejected by admission policy."
    actual_calls = 0
    if admitted:
        if data["backend"] == "ollama":
            from scenarios import infer

            answer, metadata = (generator or infer)(
                "You are a bounded classroom assistant.",
                "Say hello briefly.",
                "",
                tokens=min(plan["tokens_per_call"], 200),
            )
            actual_calls = 1
        else:
            answer = "Logical plan admitted. Offline executor ran no inference."
    evidence = {
        "projected_output_tokens": projected,
        "prior_reservations": used,
        "workspace_limit": LIMIT,
        "admitted": admitted,
        "exceeds_budget": exceeds,
        "actual_model_calls": actual_calls,
        "hard_call_cap": 1,
        "hard_output_cap": 200,
        "violation_applied": admitted and exceeds,
    }
    events = [{"kind": "inference-job", "payload": {**plan, **evidence}}]
    if admitted:
        events.append(
            {
                "kind": "budget-reservation",
                "payload": {
                    "reserved_tokens": projected,
                    "actual_model_calls": actual_calls,
                },
            }
        )
    return finish(store, token, data, DEFINITION, answer, metadata, evidence, events)
