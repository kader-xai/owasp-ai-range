"""Replay an exported synthetic image experiment; no external API needed."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vision import run_vision
parser=argparse.ArgumentParser()
parser.add_argument('evidence',type=Path)
args=parser.parse_args()
with args.evidence.open() as source:
    session=json.load(source)
attempts=session.get('attempts',[])
if not isinstance(attempts,list) or len(attempts)>6:
    raise SystemExit('Use an export with at most six attempts.')
for attempt in attempts:
    result=run_vision(attempt['input'])
    print(json.dumps(result,indent=2))
