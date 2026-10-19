from pathlib import Path
import base64
import json
import subprocess
import sys

ROOT = Path(__file__).parent
REPORTS = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'reports')
assert REPORTS.resolve().is_relative_to(ROOT.resolve())
source = r'''
from pathlib import Path
import base64, json
root = Path('/srv/workspace/patch_backups/20261018_build_common_rootcause')
result = {}
for kind, pointer in [('fresh', 'latest-verification-path.txt'), ('fixed', 'latest-stale-verification-path.txt')]:
    path = Path((root / pointer).read_text(encoding='utf-8').strip())
    assert path.is_relative_to(root)
    directory = path.parent
    files = [item for item in directory.rglob('*') if item.is_file() and item.parent in
             [directory, directory/'original', directory/'explicit_build_common'] and
             (item.name.endswith('.log') or item.name in ['verification.json', 'stale-package-lock.json'])]
    result[kind] = {str(item.relative_to(directory)): base64.b64encode(item.read_bytes()).decode('ascii') for item in files}
print(json.dumps(result))
'''
result = subprocess.run(['ssh', '-p', '42247', '-i', r'C:\Users\31854\.ssh\id_ed25519',
    '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
    'root@119.3.182.128', 'python3 -'], input=source.encode('utf-8'), capture_output=True, timeout=180)
if result.returncode:
    raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))
data = json.loads(result.stdout.decode('utf-8'))
for kind, files in data.items():
    for name, payload in files.items():
        path = REPORTS / kind / name
        assert path.resolve().is_relative_to(REPORTS.resolve())
        path.parent.mkdir(parents=True, exist_ok=True)
        content = base64.b64decode(payload)
        content.decode('utf-8')
        path.write_bytes(content)
    print(kind, len(files), 'files saved')
fixed = json.loads((REPORTS / 'fixed/verification.json').read_text(encoding='utf-8'))
checks = {case['name']: case for case in fixed['cases']}
assert checks['install-current-source-with-old-lock']['returncode'] == 0
assert not checks['install-current-source-with-old-lock']['state']['exists']
assert checks['install-current-source-with-old-lock']['compile']['returncode'] == 1
for name in ['install-fixed-source-with-old-lock', 'install-current-source-without-lock']:
    assert checks[name]['returncode'] == 0
    assert checks[name]['state']['exists'] and checks[name]['state']['resolve_rc'] == 0
    assert checks[name]['compile']['returncode'] == 0
print('Original failure and both fixed installation modes verified.')
