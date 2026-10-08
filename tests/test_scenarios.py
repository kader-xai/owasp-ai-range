import unittest
from unittest.mock import patch
from scenarios import SCENARIOS, run_scenario, inert_markup

class FocusedScenarioTests(unittest.TestCase):
    def test_preview_removes_active_tags_and_attributes(self):
        value = inert_markup('<h1 onclick="alert(1)">Demo</h1><a href="https://example.com">link</a><img src="https://example.com">')
        self.assertEqual(value, '<h1>Demo</h1>link')
        self.assertNotIn('onclick', value)
    def run_sample(self, lab, sample, mode='vulnerable', backend='simulation'):
        s = SCENARIOS[lab]
        return run_scenario({'lab':lab, 'mode':mode, 'backend':backend, 'question':s['question'], 'document':s[sample]})

    def test_supply_chain_integrity(self):
        lab = 'LLM03:2025'
        self.assertFalse(self.run_sample(lab, 'baseline')['attack_observed'])
        self.assertTrue(self.run_sample(lab, 'example')['attack_observed'])
        with patch('scenarios.infer') as infer:
            result = self.run_sample(lab, 'example', 'defended', 'ollama')
            infer.assert_not_called()
            self.assertTrue(result['blocked_before_inference'])
            self.assertFalse(result['attack_observed'])

    def test_poisoned_fact_ingestion(self):
        lab = 'LLM04:2025'
        self.assertFalse(self.run_sample(lab, 'baseline')['attack_observed'])
        self.assertTrue(self.run_sample(lab, 'example')['attack_observed'])
        with patch('scenarios.infer') as infer:
            result = self.run_sample(lab, 'example', 'defended', 'ollama')
            infer.assert_not_called()
            self.assertTrue(result['blocked_before_inference'])

    def test_html_sink_encoding(self):
        lab = 'LLM05:2025'
        weak = self.run_sample(lab, 'example')
        strong = self.run_sample(lab, 'example', 'defended')
        self.assertTrue(weak['attack_observed'])
        self.assertFalse(strong['attack_observed'])
        self.assertIn('<h1>', weak['preview_html'])
        self.assertIn('&lt;h1&gt;', strong['preview_html'])

    def test_read_only_agent_adapter(self):
        lab = 'LLM06:2025'
        self.assertFalse(self.run_sample(lab, 'baseline')['attack_observed'])
        self.assertTrue(self.run_sample(lab, 'example')['attack_observed'])
        with patch('scenarios.infer', return_value=('{"action":"send","text":"DEMO-SENT","approved":true}', {})):
            result = self.run_sample(lab, 'example', 'defended', 'ollama')
            self.assertFalse(result['attack_observed'])
            self.assertEqual(result['evidence']['outbox'], [])

    def test_private_configuration_not_in_context(self):
        lab = 'LLM07:2025'
        self.assertTrue(self.run_sample(lab, 'example')['attack_observed'])
        with patch('scenarios.infer', return_value=('Public role only', {})) as call:
            self.run_sample(lab, 'example', 'defended', 'ollama')
            self.assertNotIn('SILVER-KITE-319', str(call.call_args))

    def test_vector_owner_filter_before_ranking(self):
        lab = 'LLM08:2025'
        weak = self.run_sample(lab, 'example')
        strong = self.run_sample(lab, 'example', 'defended')
        self.assertTrue(weak['evidence']['unauthorized_retrieval'])
        self.assertTrue(weak['attack_observed'])
        self.assertFalse(strong['evidence']['unauthorized_retrieval'])
        self.assertFalse(strong['attack_observed'])

    def test_source_and_value_verification(self):
        lab = 'LLM09:2025'
        self.assertFalse(self.run_sample(lab, 'baseline')['attack_observed'])
        self.assertTrue(self.run_sample(lab, 'example')['attack_observed'])
        self.assertFalse(self.run_sample(lab, 'example', 'defended')['evidence']['published'])
        with patch('scenarios.infer', return_value=('{"days":47,"source":"policy-v1"}', {})):
            self.assertFalse(self.run_sample(lab, 'example', 'defended', 'ollama')['evidence']['published'])

    def test_resource_admission_and_hard_cap(self):
        lab = 'LLM10:2025'
        self.assertTrue(self.run_sample(lab, 'example')['attack_observed'])
        with patch('scenarios.infer', return_value=('Hello', {})) as call:
            weak = self.run_sample(lab, 'example', backend='ollama')
            self.assertEqual(weak['evidence']['actual_model_calls'], 1)
            self.assertEqual(call.call_args.kwargs['tokens'], 200)
        with patch('scenarios.infer') as call:
            strong = self.run_sample(lab, 'example', 'defended', 'ollama')
            call.assert_not_called()
            self.assertTrue(strong['blocked_before_inference'])

    def test_invalid_plan_is_not_admitted(self):
        for document in ('{"calls":true,"tokens_per_call":200}', '{"calls":-1,"tokens_per_call":200}', '{"calls":10001,"tokens_per_call":200}'):
            with self.assertRaises(ValueError):
                run_scenario({'lab':'LLM10:2025','mode':'vulnerable','backend':'ollama','question':'hello','document':document})

    def test_no_zero_similarity_record_selected(self):
        result = run_scenario({'lab':'LLM08:2025','mode':'defended','backend':'simulation','question':'Summarize','document':'billing invoice payment'})
        self.assertEqual(result['evidence']['selected_ids'], [])

    def test_invalid_model_claim_rejected_in_both_modes(self):
        with patch('scenarios.infer', return_value=('{"error":"no answer"}', {})):
            for mode in ('vulnerable', 'defended'):
                result = self.run_sample('LLM09:2025', 'example', mode, 'ollama')
                self.assertFalse(result['evidence']['published'])
