"""Explicit workflow contracts; legacy prototype scenarios remain separate."""

from labs.disclosure import DEFINITION as DISCLOSURE, run_support
from labs.refund import DEFINITION as REFUND, run_refund
from labs import supply, poisoning, output, agency, prompt, retrieval, claims, budget

WORKFLOWS = {
    REFUND["id"]: {"definition": REFUND, "run": run_refund},
    DISCLOSURE["id"]: {"definition": DISCLOSURE, "run": run_support},
}
for module in (supply, poisoning, output, agency, prompt, retrieval, claims, budget):
    WORKFLOWS[module.DEFINITION["id"]] = {
        "definition": module.DEFINITION,
        "run": module.run,
    }


def definitions():
    return [WORKFLOWS[key]["definition"] for key in sorted(WORKFLOWS)]


def execute(lab, store, token, data):
    if lab not in WORKFLOWS:
        raise ValueError("Unknown workflow")
    return WORKFLOWS[lab]["run"](store, token, data)
