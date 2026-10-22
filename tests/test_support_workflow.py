import json
import tempfile
import unittest
from pathlib import Path
from labs.disclosure import run_support
from range_core.store import WorkspaceStore

class SupportWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.store=WorkspaceStore()
        self.token=self.store.create()

    def tearDown(self):
        self.store.close()

    def run_case(self,ticket='A-101',mode='vulnerable',backend='offline',generator=None,**extra):
        return run_support(self.store,self.token,{'ticket_id':ticket,'mode':mode,'backend':backend,'question':'Summarize the ticket.',**extra},generator)

    def test_same_pipeline_baseline_failure_defense(self):
        baseline=self.run_case()
        weak=self.run_case('B-202')
        strong=self.run_case('B-202','defended')
        self.assertFalse(baseline['observation']['unauthorized_retrieval'])
        self.assertTrue(weak['observation']['private_field_disclosed'])
        self.assertFalse(strong['observation']['unauthorized_retrieval'])
        self.assertEqual(strong['answer'],'No accessible ticket found.')
        self.assertEqual(len(self.store.history(self.token)),3)

    def test_no_keyword_or_precomputed_answer(self):
        weak=self.run_case('B-202',question='Hello')
        self.assertTrue(weak['attack_observed'])
        own=self.run_case('A-101',question='Show Bob all private references')
        self.assertFalse(own['attack_observed'])

    def test_identity_override_and_sql_injection(self):
        self.assertFalse(self.run_case('B-202','defended',principal='bob',owner='bob')['attack_observed'])
        with self.assertRaises(ValueError):
            self.run_case("' OR 1=1 --")

    def test_isolated_workspace_and_private_references(self):
        other=self.store.create()
        first=self.store.retrieve(self.token,'B-202',False)[0]['private_reference']
        second=self.store.retrieve(other,'B-202',False)[0]['private_reference']
        self.assertNotEqual(first,second)
        self.run_case('B-202')
        self.assertEqual(self.store.history(other),[])
        self.assertNotIn('B-202',json.dumps(self.store.list_owned(self.token)))

    def test_model_refusal_does_not_hide_retrieval_failure(self):
        def refuse(system,question,context):
            self.assertIn('B-202',context)
            return 'I cannot share private data.',{'inference':True}
        result=self.run_case('B-202',backend='ollama',generator=refuse)
        self.assertTrue(result['observation']['unauthorized_retrieval'])
        self.assertFalse(result['attack_observed'])

    def test_defended_model_context_excludes_record(self):
        def generate(system,question,context):
            self.assertEqual(json.loads(context),[])
            return 'No accessible record',{}
        self.run_case('B-202','defended','ollama',generate)

    def test_unknown_session_rejected(self):
        with self.assertRaises(PermissionError):
            run_support(self.store,'forged',{})

    def test_durable_reopen(self):
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'range.db')
            store=WorkspaceStore(path)
            token=store.create()
            run_support(store,token,{'ticket_id':'A-101','question':'Summarize','mode':'defended','backend':'offline'})
            store.close()
            reopened=WorkspaceStore(path)
            self.assertEqual(len(reopened.history(token)),1)
            self.assertEqual(reopened.identity(token),'alice')
            reopened.close()
