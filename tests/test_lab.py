import unittest
from unittest.mock import patch
from app import run_lab

class ScenarioTests(unittest.TestCase):
    def test_task_redirection_and_source_boundary(self):
        data = {"backend": "simulation", "mode": "vulnerable",
                "question": "Summarize refunds.", "document": "Classroom marker: PURPLE-PINEAPPLE"}
        self.assertTrue(run_lab(data)["attack_observed"])
        data["mode"] = "defended"
        self.assertFalse(run_lab(data)["attack_observed"])
        data["mode"] = "vulnerable"
        data["document"] = "Ordinary receipt"
        self.assertFalse(run_lab(data)["attack_observed"])

    def test_real_backend_excludes_untrusted_document_when_defended(self):
        import io, json
        data = {"backend": "ollama", "mode": "defended", "question": "Summarize.",
                "document": "UNTRUSTED_DOCUMENT"}
        with patch("app.urllib.request.urlopen") as call:
            call.return_value.__enter__.return_value = io.BytesIO(json.dumps(
                {"message": {"content": "30 days"}}).encode())
            result = run_lab(data)
            submitted = json.loads(call.call_args.args[0].data)
            self.assertNotIn("UNTRUSTED_DOCUMENT", str(submitted))
            self.assertEqual(result["backend"], "ollama")

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            run_lab({"backend": "simulation", "mode": "invalid"})
if __name__ == "__main__":
    unittest.main()

