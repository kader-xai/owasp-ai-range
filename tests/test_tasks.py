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
