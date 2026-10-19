from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).parent
source = (ROOT / 'remote_inspect.py').read_text(encoding='utf-8')
result = subprocess.run(['ssh', '-p', '42247', '-i', r'C:\Users\31854\.ssh\id_ed25519',
    '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
    'root@119.3.182.128', 'python3 -'], input=source.encode('utf-8'), capture_output=True, timeout=180)
if result.returncode:
    raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))
data = json.loads(result.stdout.decode('utf-8'))
(ROOT / 'existing-workspace.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: data[key] for key in ['environment', 'ace_head', 'ace_status', 'node',
                                           'node_version', 'npm_version', 'resolution']}, ensure_ascii=False, indent=2))
for item in data['directories']:
    print(item['folder'], [(Path(path['path']).name, path['exists'], path['is_symlink'],
                            path['link'], path['tsconfig_exists']) for path in item['paths']])
