"""Bounded local experiment for one category; JSON on stdout."""
import argparse
import datetime
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scenarios import SCENARIOS, run_scenario
parser = argparse.ArgumentParser()
parser.add_argument('lab', choices=list(SCENARIOS))
parser.add_argument('--summary', action='store_true', help='Print compact actual observations')
args = parser.parse_args()
scenario = SCENARIOS[args.lab]
observations = []
for sample in ('baseline', 'example'):
    for mode in ('vulnerable', 'defended'):
        input_data = {'lab': args.lab, 'mode': mode, 'backend': 'ollama', 'question': scenario['question'], 'document': scenario[sample]}
        observations.append({'sample': sample, 'input': input_data, 'result': run_scenario(input_data)})
if args.summary:
    observations = [{'sample': o['sample'], 'mode': o['result']['mode'], 'answer': o['result']['answer'],
                     'attack_observed': o['result']['attack_observed'], 'evidence': o['result']['evidence'],
                     'model_metadata': o['result']['model_metadata']} for o in observations]
print(json.dumps({'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'scope': scenario['scope'], 'observations': observations}, indent=2))
