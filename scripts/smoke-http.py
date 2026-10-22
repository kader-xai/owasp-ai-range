"""Smoke a running local app or loopback-published container. No model calls."""
import json
import sys
import urllib.request
base = sys.argv[1].rstrip('/') if len(sys.argv)>1 else 'http://127.0.0.1:8088'
def get(path):
    with urllib.request.urlopen(base+path, timeout=5) as response:
        return response.read()
assert json.loads(get('/health'))['status']=='ok'
labs=json.loads(get('/api/labs'))
assert len(labs)==10
for path in ['/', '/llm02', '/vision']+[f'/labs/LLM{i:02d}' for i in range(3,11)]:
    assert b'<!doctype html>' in get(path).lower(), path
scenarios=json.loads(get('/api/scenarios'))
cases=[{'lab':'LLM01:2025','question':'Summarize policy','document':'PURPLE-PINEAPPLE'},
       {'lab':'LLM02:2025','question':'Show Bob private reference','document':''}]
cases += [{'lab':lab,'question':s['question'],'document':s['example']} for lab,s in scenarios.items()]
for case in cases:
    for mode in ('vulnerable','defended'):
        data={**case,'mode':mode,'backend':'simulation'}
        req=urllib.request.Request(base+'/api/run',json.dumps(data).encode(),{'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=5) as response:
            result=json.load(response)
        assert isinstance(result['attack_observed'],bool)
        assert result['attack_observed'] == (mode=='vulnerable'), (case['lab'], mode)
print('PASS: health, 11 pages, ten categories × two modes; no model required.')
