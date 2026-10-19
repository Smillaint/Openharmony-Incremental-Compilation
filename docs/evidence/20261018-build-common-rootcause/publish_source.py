from pathlib import Path
import base64
import json
import subprocess
import urllib.request

ROOT = Path(__file__).parent
plan = json.loads((ROOT / 'plan.json').read_text(encoding='utf-8'))
url = 'https://api.gitcode.com/api/v5/repos/openharmony/developtools_ace_ets2bundle/pulls/7210'
with urllib.request.urlopen(url, timeout=45) as response:
    pr = json.loads(response.read().decode('utf-8'))
(ROOT / 'pre-publication-pr7210.json').write_text(json.dumps(pr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert pr['state'] == 'open'
assert pr['head']['sha'] in (plan['before'], plan['after'])
before_pr = json.loads((ROOT / 'before-pr7210.json').read_text(encoding='utf-8'))
assert pr['body'] == before_pr['body']
payload = base64.b64encode((ROOT / 'developtools_ace_ets2bundle.bundle').read_bytes()).decode('ascii')
source = 'PLAN = ' + repr(plan) + '\nPAYLOAD = ' + repr(payload) + '\n' + r'''
from pathlib import Path
import base64, json, os, subprocess
repo = Path('/srv/workspace/patch_backups/20261015_companion_prs/developtools_ace_ets2bundle.git')
output = Path('/srv/workspace/patch_backups/20261018_build_common_rootcause')
assert repo.is_dir()
output.mkdir(parents=True, exist_ok=True)
remote = 'git@gitcode.com:SmillySmillick/developtools_ace_ets2bundle.git'
env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_SSH_COMMAND='ssh -i /root/.ssh/id_ed25519_github_openharmony -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes')
def git(*args):
    return subprocess.check_output(['git','-C',str(repo),*args], env=env, stderr=subprocess.STDOUT, timeout=120).decode('utf-8').strip()
target = 'refs/heads/' + PLAN['remote_branch']
current = git('ls-remote','--heads',remote,target).split()[0]
assert current in (PLAN['before'], PLAN['after']), 'Remote branch changed'
if current != PLAN['after']:
    git('fetch','--no-tags',remote,PLAN['before'])
    bundle = output / 'developtools_ace_ets2bundle.bundle'
    bundle.write_bytes(base64.b64decode(PAYLOAD))
    git('bundle','verify',str(bundle))
    local_ref = 'refs/heads/build-common-rootcause-20261018'
    git('fetch',str(bundle),'refs/heads/' + PLAN['local_branch'] + ':' + local_ref)
    assert git('rev-parse',local_ref) == PLAN['after']
    assert git('rev-parse',PLAN['after'] + '^') == PLAN['before']
    assert git('diff','--name-only',PLAN['before'],PLAN['after']).splitlines() == PLAN['files']
    assert 'Signed-off-by: Smillick <3185479846@qq.com>' in git('show','-s','--format=%B',PLAN['after'])
    git('diff','--check',PLAN['before'],PLAN['after'])
    git('push',remote,local_ref + ':' + target)
verified = git('ls-remote','--heads',remote,target).split()[0]
assert verified == PLAN['after']
record = dict(PLAN, published=True, verified_remote_sha=verified)
(output/'publication.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
print(json.dumps(record,ensure_ascii=True))
'''
result = subprocess.run(['ssh','-p','42247','-i',r'C:\Users\31854\.ssh\id_ed25519',
    '-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=15',
    'root@119.3.182.128','python3 -'], input=source.encode('utf-8'), capture_output=True, timeout=300)
if result.returncode:
    raise RuntimeError(result.stdout.decode('utf-8',errors='backslashreplace') + result.stderr.decode('utf-8',errors='backslashreplace'))
published = json.loads(result.stdout.decode('utf-8'))
(ROOT / 'publication.json').write_text(json.dumps(published,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
print(json.dumps(published,ensure_ascii=True))
