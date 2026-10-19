from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request

ROOT = Path(__file__).parent
REPO = Path('D:/workspace/repositories/companion-prs-20261015/developtools_ace_ets2bundle')


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args]).decode('utf-8').strip()


assert git('status', '--porcelain') == ''
before = git('rev-parse', 'HEAD')
request = urllib.request.Request('https://api.gitcode.com/api/v5/repos/openharmony/developtools_ace_ets2bundle/pulls/7210',
                                headers={'User-Agent': 'OpenHarmony-PR-Maintenance'})
with urllib.request.urlopen(request, timeout=40) as response:
    pr = json.load(response)
assert pr['head']['sha'] == before
assert pr['state'] == 'open'
(ROOT / 'before-pr7210.json').write_text(json.dumps(pr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
name = 'ets1.2/package.json'
content = (REPO / name).read_bytes()
data = json.loads(content.decode('utf-8'))
assert '@koalaui/build-common' not in data['devDependencies']
git('tag', 'backup/build-common-rootcause-20261018', before)
git('switch', '-c', 'fix/build-common-root-dependency-20261018')
path = ROOT / 'before' / name
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(content)
plan = {'repo': str(REPO), 'number': 7210, 'before': before,
        'remote_branch': pr['head']['ref'], 'local_branch': 'fix/build-common-root-dependency-20261018',
        'backup_tag': 'backup/build-common-rootcause-20261018', 'files': [name],
        'before_sha256': hashlib.sha256(content).hexdigest()}
(ROOT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(plan, ensure_ascii=False, indent=2))
