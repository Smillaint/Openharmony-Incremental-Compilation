from pathlib import Path
import base64
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import time

CODE = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
ACE = CODE / 'developtools/ace_ets2bundle'
ROOT = Path('/srv/workspace/patch_backups/20261018_build_common_rootcause')
RUN = Path(tempfile.mkdtemp(prefix='stale-lock-', dir=ROOT))
NODE = CODE / 'prebuilts/build-tools/common/nodejs/current/bin/node'
NPM = NODE.parent / 'npm'
ENV = dict(os.environ, PATH=str(NODE.parent) + ':' + os.environ['PATH'],
           npm_config_cache=str(ROOT / 'npm-cache'), npm_config_audit='false',
           npm_config_update_notifier='false', npm_config_progress='false')
archive_bytes = subprocess.check_output(['git', '-C', str(ACE), 'archive', 'HEAD', 'ets1.2'])
with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as archive:
    for member in archive:
        target = RUN / member.name
        assert target.resolve().is_relative_to(RUN.resolve())
        archive.extract(member, RUN, filter='data')
PROJECT = RUN / 'ets1.2'
assert hashlib.sha256((PROJECT / 'package.json').read_bytes()).hexdigest() == EXPECTED_ORIGINAL_HASH


def run(name, args, timeout=180):
    start = time.monotonic()
    outcome = subprocess.run([str(arg) for arg in args], cwd=PROJECT, env=ENV,
                             capture_output=True, timeout=timeout)
    out = outcome.stdout.decode('utf-8', errors='backslashreplace')
    err = outcome.stderr.decode('utf-8', errors='backslashreplace')
    (RUN / (name + '.stdout.log')).write_text(out, encoding='utf-8')
    (RUN / (name + '.stderr.log')).write_text(err, encoding='utf-8')
    return {'name': name, 'returncode': outcome.returncode, 'seconds': round(time.monotonic() - start, 2),
            'errors': [line for line in (out + err).splitlines() if 'error TS' in line][:20]}


def state():
    link = PROJECT / 'node_modules/@koalaui/build-common'
    lock = PROJECT / 'package-lock.json'
    info = json.loads(lock.read_text(encoding='utf-8')) if lock.is_file() else {}
    resolution = subprocess.run([str(NODE), '-e',
        "try{console.log(require.resolve('@koalaui/build-common/tsconfig.json',{paths:[process.argv[1]]}))}catch(e){console.error(e.message);process.exitCode=1}",
        str(PROJECT / 'common')], cwd=PROJECT, env=ENV, capture_output=True)
    return {'lexists': os.path.lexists(link), 'exists': link.exists(), 'is_symlink': link.is_symlink(),
            'link': os.readlink(link) if link.is_symlink() else None,
            'realpath': str(link.resolve()), 'tsconfig_exists': (link / 'tsconfig.json').is_file(),
            'lock_has_build_common': '@koalaui/build-common' in info.get('dependencies', {}),
            'lock_sha256': hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else None,
            'resolve_rc': resolution.returncode, 'resolve_stdout': resolution.stdout.decode('utf-8'),
            'resolve_stderr': resolution.stderr.decode('utf-8')}


def clean_node_modules():
    path = PROJECT / 'node_modules'
    assert path.resolve().is_relative_to(RUN.resolve())
    if path.is_dir():
        shutil.rmtree(path)


originals = {}
for folder in ['interop', 'libarkts']:
    path = PROJECT / folder / 'package.json'
    originals[path] = path.read_bytes()
    data = json.loads(originals[path].decode('utf-8'))
    data['dependencies'].pop('@koalaui/build-common')
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
install = [NPM, 'install', '--registry', 'https://repo.huaweicloud.com/repository/npm/', '--verbose']
results = []
seed = run('seed-old-lock', install)
assert seed['returncode'] == 0
seed['state'] = state()
assert not seed['state']['exists']
results.append(seed)
for path, content in originals.items():
    path.write_bytes(content)
clean_node_modules()
stale = run('install-current-source-with-old-lock', install)
stale['state'] = state()
stale['compile'] = run('compile-with-old-lock', [NPM, 'run', 'compile:interop'])
results.append(stale)
print(json.dumps(stale, ensure_ascii=True), flush=True)
stale_lock = (PROJECT / 'package-lock.json').read_bytes()
(RUN / 'stale-package-lock.json').write_bytes(stale_lock)
if 'FIXED_PACKAGE_B64' in globals():
    fixed_package = base64.b64decode(FIXED_PACKAGE_B64)
    fixed_package.decode('utf-8')
    (PROJECT / 'package.json').write_bytes(fixed_package)
    clean_node_modules()
    fixed = run('install-fixed-source-with-old-lock', install)
    fixed['state'] = state()
    fixed['compile'] = run('compile-fixed-with-old-lock', [NPM, 'run', 'compile:interop'])
    assert fixed['returncode'] == 0 and fixed['state']['exists'] and fixed['state']['resolve_rc'] == 0
    assert fixed['compile']['returncode'] == 0
    results.append(fixed)
    print(json.dumps(fixed, ensure_ascii=True), flush=True)
clean_node_modules()
lock = PROJECT / 'package-lock.json'
assert lock.resolve().is_relative_to(RUN.resolve())
lock.unlink()
fresh = run('install-current-source-without-lock', install)
fresh['state'] = state()
fresh['compile'] = run('compile-without-lock', [NPM, 'run', 'compile:interop'])
results.append(fresh)
print(json.dumps(fresh, ensure_ascii=True), flush=True)
result = {'run_directory': str(RUN), 'cases': results,
          'fixture_boundary': 'Synthetic older local-package graph; not the unavailable CI package-lock.json.'}
(RUN / 'verification.json').write_text(json.dumps(result, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
(ROOT / 'latest-stale-verification-path.txt').write_text(str(RUN / 'verification.json') + '\n', encoding='utf-8')
print('RESULT', RUN / 'verification.json', flush=True)
