import base64
import io
import json
import unittest
import struct
from unittest.mock import patch
from vision import run_vision

class VisionTests(unittest.TestCase):
    def test_image_boundary(self):
        for mode in ('vulnerable','defended'):
            with patch('vision.urllib.request.urlopen') as call:
                call.return_value.__enter__.return_value=io.BytesIO(b'{"message":{"content":"30 days"},"eval_count":3}')
                fixture=b'\x89PNG\r\n\x1a\n'+struct.pack('>I',13)+b'IHDR'+struct.pack('>II',900,400)
                result=run_vision({'mode':mode,'image':base64.b64encode(fixture).decode()})
                payload=json.loads(call.call_args.args[0].data)
                self.assertEqual('images' in payload['messages'][1],mode=='vulnerable')
                self.assertEqual(result['evidence']['image_in_context'],mode=='vulnerable')
                self.assertFalse(result['attack_observed'])

    def test_reject_invalid_images(self):
        for image in ('not-base64',base64.b64encode(b'<svg></svg>').decode(),'a'*1400001):
            with self.assertRaises(ValueError):
                run_vision({'mode':'vulnerable','image':image})
