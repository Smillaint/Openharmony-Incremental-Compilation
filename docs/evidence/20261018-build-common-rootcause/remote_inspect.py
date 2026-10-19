from pathlib import Path
import hashlib
import json
import os
import subprocess

CODE = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
ACE = CODE / 'developtools/ace_ets2bundle'
PROJECT = ACE / 'ets1.2'
NODE = CODE / 'prebuilts/build-tools/common/nodejs/current/bin/node'
NPM = NODE.parent / 'npm'
environment = dict(os.environ, PATH=str(NODE.parent) + ':' + os.environ['PATH'])


def command(args, cwd=PROJECT):
    outcome = subprocess.run([str(arg) for arg in args], cwd=cwd, env=environment,
                             capture_output=True, timeout=30)
    return {'returncode': outcome.returncode, 'stdout': outcome.stdout.decode('utf-8'),
            'stderr': outcome.stderr.decode('utf-8')}


result = {'environment': 'existing product workspace; not the failed CI node',
          'code': str(CODE), 'ace_head': command(['git', '-C', ACE, 'rev-parse', 'HEAD']),
          'ace_status': command(['git', '-C', ACE, 'status', '--short']),
          'node': str(NODE.resolve()), 'node_version': command([NODE, '--version']),
          'npm_version': command([NPM, '--version']), 'directories': [], 'resolution': []}
for folder in ['', 'common', 'compat', 'interop', 'libarkts', 'arktscgen']:
    base = PROJECT / folder
    item = {'folder': folder or '.', 'paths': []}
    package = base / 'package.json'
    if package.is_file():
        content = package.read_bytes()
        item['package_sha256'] = hashlib.sha256(content).hexdigest()
        item['package'] = json.loads(content.decode('utf-8'))
    lock = base / 'package-lock.json'
    if lock.is_file():
        item['lock_sha256'] = hashlib.sha256(lock.read_bytes()).hexdigest()
        lock_data = json.loads(lock.read_text(encoding='utf-8'))
        item['lock_build_common'] = lock_data.get('dependencies', {}).get('@koalaui/build-common')
    for relative in ['node_modules/@koalaui/build-common', 'node_modules/@koalaui/interop',
                     'node_modules/@koalaui/common', 'node_modules/@koalaui/compat']:
        path = base / relative
        item['paths'].append({'path': str(path), 'lexists': os.path.lexists(path),
                              'exists': path.exists(), 'is_symlink': path.is_symlink(),
                              'link': os.readlink(path) if path.is_symlink() else None,
                              'realpath': str(path.resolve()),
                              'tsconfig_exists': (path / 'tsconfig.json').is_file()})
    result['directories'].append(item)
    js = "try { console.log(require.resolve('@koalaui/build-common/tsconfig.json', {paths:[process.argv[1]]})); } catch (e) { console.error(e.message); process.exitCode=1; }"
    result['resolution'].append({'folder': folder or '.', 'result': command([NODE, '-e', js, base])})
print(json.dumps(result, ensure_ascii=True))
