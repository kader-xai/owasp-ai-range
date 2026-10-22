import unittest
from range_core.contracts import openapi
from labs.registry import definitions

class ContractTests(unittest.TestCase):
    def test_registered_workflows_and_auth_contract(self):
        contract=openapi()
        operation=contract['paths']['/api/workflows/run']['post']
        enum=operation['requestBody']['content']['application/json']['schema']['properties']['lab']['enum']
        self.assertEqual(set(enum),{d['id'] for d in definitions()})
        self.assertEqual(operation['security'],[{'WorkspaceCookie':[]}])
        self.assertEqual(contract['paths']['/api/support/start']['post']['security'],[])
