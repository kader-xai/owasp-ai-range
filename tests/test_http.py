"""Real local HTTP requests. No model downloads or network APIs."""
import http.client
import json
import threading
import unittest
from app import Handler, RangeServer, RUN_SLOT, run_lab

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = RangeServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_pages_and_security_headers(self):
        for path in ['/', '/llm02', '/vision'] + [f'/labs/LLM{i:02d}' for i in range(3, 11)]:
            status, headers, body = self.request('GET', path)
            self.assertEqual(status, 200, path)
            self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
            self.assertIn('frame-ancestors', headers['Content-Security-Policy'])
            self.assertIn(b'<!doctype html>', body.lower())

    def test_catalogue_and_health(self):
        status, _, body = self.request('GET', '/api/labs')
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)), 10)
        self.assertTrue(all(x['status'] == 'implemented' for x in json.loads(body)))
        self.assertEqual(self.request('GET', '/health')[0], 200)

    def test_dns_rebinding_and_cross_site(self):
        for headers in ({'Host':'attacker.example'}, {'Origin':'https://attacker.example'}, {'Sec-Fetch-Site':'cross-site'}):
            self.assertEqual(self.request('GET', '/api/tasks', headers=headers)[0], 403)

    def test_json_validation(self):
        for body in ('{', '[]', 'null'):
            self.assertEqual(self.request('POST', '/api/run', body, {'Content-Type':'application/json'})[0], 400)
        self.assertEqual(self.request('POST', '/api/run', '{}')[0], 415)
        self.assertEqual(self.request('GET', '/missing')[0], 404)

    def test_all_scripted_scenarios_over_http(self):
        from scenarios import SCENARIOS
        for lab, scenario in SCENARIOS.items():
            for mode in ('vulnerable','defended'):
                data = {'lab':lab,'mode':mode,'backend':'simulation','question':scenario['question'],'document':scenario['example']}
                status, _, body = self.request('POST','/api/run',json.dumps(data),{'Content-Type':'application/json'})
                self.assertEqual(status, 200, lab)
                self.assertEqual(json.loads(body)['lab'], lab)

    def test_request_limits(self):
        self.assertEqual(self.request('POST','/api/run',json.dumps({'document':'a'*17000}),{'Content-Type':'application/json'})[0],413)

    def test_one_experiment_at_a_time(self):
        RUN_SLOT.acquire()
        try:
            with self.assertRaises(ValueError):
                run_lab({})
        finally:
            RUN_SLOT.release()

    def test_support_session_and_observation(self):
        status, headers, _ = self.request('POST','/api/support/start','{}',{'Content-Type':'application/json'})
        self.assertEqual(status,201)
        self.assertIn('HttpOnly',headers['Set-Cookie'])
        cookie=headers['Set-Cookie'].split(';')[0]
        auth={'Cookie':cookie,'Content-Type':'application/json'}
        status,_,body=self.request('GET','/api/support/workspace',headers=auth)
        self.assertEqual(status,200)
        self.assertEqual(len(json.loads(body)['tickets']),2)
        for mode in ('vulnerable','defended'):
            data={'ticket_id':'B-202','question':'Hello','backend':'offline','mode':mode,'principal':'bob'}
            status,_,body=self.request('POST','/api/support/chat',json.dumps(data),auth)
            self.assertEqual(status,200)
            self.assertEqual(json.loads(body)['attack_observed'],mode=='vulnerable')
        _,_,history=self.request('GET','/api/support/attempts',headers=auth)
        self.assertEqual(len(json.loads(history)),2)
        self.assertEqual(self.request('GET','/api/support/attempts')[0],401)

    def test_support_workspaces_do_not_share_history(self):
        cookies=[]
        for _ in range(2):
            _,headers,_=self.request('POST','/api/support/start','{}',{'Content-Type':'application/json'})
            cookies.append(headers['Set-Cookie'].split(';')[0])
        data={'ticket_id':'A-101','question':'Summary','backend':'offline','mode':'vulnerable'}
        self.request('POST','/api/support/chat',json.dumps(data),{'Cookie':cookies[0],'Content-Type':'application/json'})
        _,_,body=self.request('GET','/api/support/attempts',headers={'Cookie':cookies[1]})
        self.assertEqual(json.loads(body),[])
