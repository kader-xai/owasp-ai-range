import json
import unittest
import sqlite3
from range_core.store import WorkspaceStore
from labs.refund import run_refund
from labs.registry import definitions

class RefundWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.store=WorkspaceStore()
        self.token=self.store.create()
        self.revision=self.store.attachment(self.token,'A fictional customer document.')

    def tearDown(self):
        self.store.close()

    def run_case(self,mode='vulnerable',backend='ollama',proposal=None):
        def generate(system,question,context,**options):
            self.assertEqual(json.loads(context)['customer_attachment']['revision'],self.revision)
            self.assertEqual(json.loads(context)['approved_policy']['days'],30)
            self.assertNotIn('days=900',question)
            return json.dumps(proposal if proposal is not None else {'days':900,'reference':'override'}),{'inference':True}
        return run_refund(self.store,self.token,{'revision':self.revision,'mode':mode,'backend':backend},generate)

    def test_actual_quote_transaction_and_defense(self):
        weak=self.run_case()
        strong=self.run_case('defended')
        self.assertTrue(weak['attack_observed'])
        self.assertTrue(strong['observation']['proposal_deviates_from_policy'])
        self.assertFalse(strong['observation']['quote_applied'])
        self.assertEqual(len(self.store.quotes(self.token)),1)
        self.assertEqual(self.store.quotes(self.token)[0]['days'],900)
        self.assertEqual(len(self.store.history(self.token)),2)

    def test_valid_business_baseline(self):
        self.assertTrue(self.run_case('defended',proposal={'days':30,'reference':'policy-v1'})['observation']['quote_applied'])
        self.assertFalse(self.store.history(self.token)[0]['result']['attack_observed'])

    def test_preview_has_no_model_or_mutation(self):
        result=self.run_case(backend='preview')
        self.assertFalse(result['observation']['inference_ran'])
        self.assertEqual(self.store.quotes(self.token),[])

    def test_invalid_proposals_are_never_applied(self):
        for proposal in ({'days':True,'reference':'x'},{'days':0,'reference':'x'},{'days':900,'reference':'x','approved':True},['invalid']):
            self.assertFalse(self.run_case(proposal=proposal)['observation']['quote_applied'])
        self.assertEqual(self.store.quotes(self.token),[])

    def test_attachment_revision_is_immutable_and_scoped(self):
        revision2=self.store.attachment(self.token,'Second revision')
        self.assertNotEqual(revision2,self.revision)
        self.assertEqual(self.store.read_attachment(self.token,self.revision),'A fictional customer document.')
        other=self.store.create()
        with self.assertRaises(ValueError):
            self.store.read_attachment(other,self.revision)

    def test_registry_contract(self):
        self.assertEqual(len(definitions()),10)
        self.assertTrue(all(x['architecture']=='workflow-v1' for x in definitions()))

    def test_capacity_failure_prevents_business_effect(self):
        for _ in range(200):
            self.store.record(self.token,{}, {})
        with self.assertRaises(ValueError):
            self.run_case()
        self.assertEqual(self.store.quotes(self.token),[])

    def test_quote_rolls_back_if_attempt_write_fails(self):
        self.store.connection.execute("CREATE TRIGGER fail_attempt BEFORE INSERT ON attempts BEGIN SELECT RAISE(ABORT,'test failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.run_case()
        self.assertEqual(self.store.quotes(self.token),[])
        self.assertEqual(self.store.history(self.token),[])

    def test_quotes_do_not_cross_workspace(self):
        self.run_case()
        other=self.store.create()
        self.assertEqual(self.store.quotes(other),[])
