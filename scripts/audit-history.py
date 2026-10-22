"""Small pre-publication tripwire, NOT a comprehensive secret scanner.

Checks reachable Git text blobs without printing matching content. Review any
reported objects privately before publication; no automatic history rewriting.
"""
import re
import subprocess
import sys

patterns = [
    rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    rb'gh[pousr]_[A-Za-z0-9]{30,}',
    rb'github_pat_[A-Za-z0-9_]{40,}',
    rb'AKIA[0-9A-Z]{16}',
    rb'sk-[A-Za-z0-9_-]{32,}',
]
objects = subprocess.check_output(['git','rev-list','--objects','--all']).splitlines()
failures = []
checked = 0
for item in objects:
    sha, _, path = item.partition(b' ')
    if not path:
        continue
    if subprocess.check_output(['git','cat-file','-t',sha]).strip() != b'blob':
        continue
    body = subprocess.check_output(['git','cat-file','-p',sha])
    if b'\0' in body:
        continue
    checked += 1
    if any(re.search(pattern,body) for pattern in patterns):
        failures.append(sha.decode())
print(f'Checked {checked} reachable text blobs for selected key/token signatures.')
if failures:
    print('Potential sensitive objects (content withheld): ' + ', '.join(failures))
    sys.exit(1)
print('No selected signatures detected. This does not prove absence of secrets; manually review files and images.')
