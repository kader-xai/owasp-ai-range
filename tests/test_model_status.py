import io
import json
import unittest
from unittest.mock import patch
from app import model_status

class ModelStatusTests(unittest.TestCase):
    def test_unavailable(self):
        with patch('app.urllib.request.urlopen', side_effect=OSError('offline')):
            self.assertFalse(model_status()['available'])

    def test_downloaded_model(self):
        with patch.dict('os.environ', {'OLLAMA_MODEL': 'test:small'}):
            with patch('app.urllib.request.urlopen', return_value=io.BytesIO(json.dumps(
                    {'models': [{'name': 'test:small'}]}).encode())):
                self.assertEqual(model_status(), {'available': True, 'model': 'test:small', 'loaded': True})

    def test_missing_model(self):
        with patch('app.urllib.request.urlopen', return_value=io.BytesIO(b'{"models": []}')):
            self.assertFalse(model_status()['loaded'])
