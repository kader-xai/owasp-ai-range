import unittest
from app import create_task, TASKS, TASK_LOCK

class TaskTests(unittest.TestCase):
    def setUp(self):
        with TASK_LOCK:
            TASKS.clear()

    def test_adapter_records_observation(self):
        task = create_task({'mode': 'vulnerable', 'backend': 'simulation', 'attack_observed': True})
        self.assertEqual(task['id'], 1)
        self.assertEqual(task['adapter'], 'local-memory')

    def test_invalid_boolean(self):
        with self.assertRaises(ValueError):
            create_task({'mode': 'vulnerable', 'backend': 'simulation', 'attack_observed': 'true'})

    def test_category_aware_task(self):
        task = create_task({'lab':'LLM06:2025','mode':'defended','backend':'ollama','attack_observed':False})
        self.assertEqual(task['lab'], 'LLM06:2025')
        with self.assertRaises(ValueError):
            create_task({'lab':'LLM99:2025','mode':'defended','backend':'ollama','attack_observed':False})
