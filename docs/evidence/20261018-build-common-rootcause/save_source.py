from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).parent
plan = json.loads((ROOT / 'plan.json').read_text(encoding='utf-8'))
repo = Path(plan['repo'])


def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode('utf-8').strip()


assert git('rev-parse', 'HEAD') == plan['before']
assert git('branch', '--show-current') == plan['local_branch']
assert git('rev-parse', plan['backup_tag']) == plan['before']
assert git('diff', '--name-only').splitlines() == plan['files']
assert not git('diff', '--cached', '--name-only')
before = json.loads((ROOT / 'before/ets1.2/package.json').read_text(encoding='utf-8'))
after = json.loads((repo / 'ets1.2/package.json').read_text(encoding='utf-8'))
before['devDependencies']['@koalaui/build-common'] = './build-common'
assert before == after
verification = json.loads((ROOT / 'reports-exact-gate/fixed/verification.json').read_text(encoding='utf-8'))
assert verification['source_revision'] == '9e0f9e58a243d7aeab672c317a2322dc37efd1a7'
cases = {case['name']: case for case in verification['cases']}
assert cases['install-current-source-with-old-lock']['compile']['returncode'] == 1
for name in ['install-fixed-source-with-old-lock', 'install-current-source-without-lock']:
    assert cases[name]['compile']['returncode'] == 0 and cases[name]['state']['resolve_rc'] == 0
git('diff', '--check')
git('add', '--', 'ets1.2/package.json')
git('-c', 'user.name=Smillick', '-c', 'user.email=3185479846@qq.com', 'commit', '-s',
    '-m', 'Declare build-common as a root build dependency')
plan['after'] = git('rev-parse', 'HEAD')
assert git('rev-parse', 'HEAD^') == plan['before']
assert 'Signed-off-by: Smillick <3185479846@qq.com>' in git('show', '-s', '--format=%B', 'HEAD')
assert not git('status', '--porcelain')
patch = subprocess.check_output(['git', '-C', str(repo), 'format-patch', '-1', '--stdout', 'HEAD'])
patch.decode('utf-8')
(ROOT / 'developtools_ace_ets2bundle.patch').write_bytes(patch)
git('bundle', 'create', str(ROOT / 'developtools_ace_ets2bundle.bundle'),
    plan['local_branch'], '^' + plan['before'])
git('bundle', 'verify', str(ROOT / 'developtools_ace_ets2bundle.bundle'))
plan['patch_sha256'] = hashlib.sha256(patch).hexdigest()
plan['published'] = False
(ROOT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(plan, ensure_ascii=True))
