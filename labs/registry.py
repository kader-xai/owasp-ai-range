"""Explicit workflow contracts; legacy prototype scenarios remain separate."""
from labs.disclosure import DEFINITION as DISCLOSURE, run_support
from labs.refund import DEFINITION as REFUND, run_refund

WORKFLOWS = {
    REFUND['id']: {'definition': REFUND, 'run': run_refund},
    DISCLOSURE['id']: {'definition': DISCLOSURE, 'run': run_support},
}

def definitions():
    return [entry['definition'] for entry in WORKFLOWS.values()]

def execute(lab, store, token, data):
    if lab not in WORKFLOWS:
        raise ValueError('Unknown workflow')
    return WORKFLOWS[lab]['run'](store, token, data)
