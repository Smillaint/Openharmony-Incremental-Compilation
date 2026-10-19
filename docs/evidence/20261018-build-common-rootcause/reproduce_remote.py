from pathlib import Path
import hashlib
import io
import json
import os
import subprocess
import tarfile
import tempfile
import time

CODE = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
ACE = CODE / 'developtools/ace_ets2bundle'
ROOT = Path('/srv/workspace/patch_backups/20261018_build_common_rootcause')
ROOT.mkdir(parents=True, exist_ok=True)
RUN = Path(tempfile.mkdtemp(prefix='fresh-install-', dir=ROOT))
NODE = CODE / 'prebuilts/build-tools/common/nodejs/current/bin/node'
NPM = NODE.parent / 'npm'
ENV = dict(os.environ, PATH=str(NODE.parent) + ':' + os.environ['PATH'],
           npm_config_cache=str(ROOT / 'npm-cache'), npm_config_audit='false',
           npm_config_update_notifier='false', npm_config_progress='false')
archive_bytes = subprocess.check_output(['git', '-C', str(ACE), 'archive', 'HEAD', 'ets1.2'])
results = []


def command(args, cwd, timeout=40):
    start = time.monotonic()
    try:
        completed = subprocess.run([str(arg) for arg in args], cwd=cwd, env=ENV,
                                   capture_output=True, timeout=timeout)
        return {'returncode': completed.returncode, 'stdout': completed.stdout.decode('utf-8', errors='backslashreplace'),
                'stderr': completed.stderr.decode('utf-8', errors='backslashreplace'),
                'seconds': round(time.monotonic() - start, 2)}
    except subprocess.TimeoutExpired as error:
        return {'returncode': 'timeout', 'stdout': (error.stdout or b'').decode('utf-8', errors='backslashreplace'),
                'stderr': (error.stderr or b'').decode('utf-8', errors='backslashreplace'),
                'seconds': round(time.monotonic() - start, 2)}


def links(project):
    output = []
    for folder in ['', 'common', 'compat', 'interop', 'libarkts']:
        path = project / folder / 'node_modules/@koalaui/build-common'
        script = "try { console.log(require.resolve('@koalaui/build-common/tsconfig.json',{paths:[process.argv[1]]})); } catch(e) { console.error(e.message); process.exitCode=1; }"
        output.append({'folder': folder or '.', 'path': str(path),
            'lexists': os.path.lexists(path), 'exists': path.exists(),
            'is_symlink': path.is_symlink(), 'target': os.readlink(path) if path.is_symlink() else None,
            'realpath': str(path.resolve()), 'tsconfig_exists': (path / 'tsconfig.json').is_file(),
            'resolve': command([NODE, '-e', script, project / folder], project)})
    return output


for name in ['original', 'explicit_build_common']:
    destination = RUN / name
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes)) as archive:
        for member in archive:
            target = destination / member.name
            assert target.resolve().is_relative_to(destination.resolve())
            archive.extract(member, destination, filter='data')
    project = destination / 'ets1.2'
    package_path = project / 'package.json'
    original = package_path.read_bytes()
    package = json.loads(original.decode('utf-8'))
    if name != 'original':
        package['devDependencies']['@koalaui/build-common'] = './build-common'
        package_path.write_text(json.dumps(package, indent=2) + '\n', encoding='utf-8')
    hooks = {}
    for package_json in project.glob('*/package.json'):
        info = json.loads(package_json.read_text(encoding='utf-8'))
        hooks[str(package_json.relative_to(project))] = {key: value for key, value in info.get('scripts', {}).items()
            if key in ['preinstall', 'install', 'postinstall', 'prepare', 'prepublish']}
    print(json.dumps({'case': name, 'phase': 'npm install', 'directory': str(project)}, ensure_ascii=True), flush=True)
    install = command([NPM, 'install', '--registry', 'https://repo.huaweicloud.com/repository/npm/',
                       '--verbose'], project, timeout=240)
    (destination / 'npm-install.stdout.log').write_text(install['stdout'], encoding='utf-8')
    (destination / 'npm-install.stderr.log').write_text(install['stderr'], encoding='utf-8')
    result = {'case': name, 'directory': str(project), 'package_before_sha256': hashlib.sha256(original).hexdigest(),
              'package_sha256': hashlib.sha256(package_path.read_bytes()).hexdigest(),
              'install': {key: value for key, value in install.items() if key not in ['stdout', 'stderr']},
              'install_tail': install['stderr'].splitlines()[-12:], 'hooks': hooks,
              'links': links(project)}
    if install['returncode'] == 0:
        compile_result = command([NPM, 'run', 'compile:interop'], project, timeout=120)
        (destination / 'compile.stdout.log').write_text(compile_result['stdout'], encoding='utf-8')
        (destination / 'compile.stderr.log').write_text(compile_result['stderr'], encoding='utf-8')
        result['compile'] = compile_result
    results.append(result)
    print(json.dumps({'case': name, 'install': result['install'],
                      'links': [(item['folder'], item['exists'], item['target'], item['resolve']['returncode']) for item in result['links']],
                      'compile': result.get('compile', {}).get('returncode'),
                      'errors': [line for line in result.get('compile', {}).get('stdout', '').splitlines() if 'error TS' in line][:12],
                      'install_tail': result['install_tail']}, ensure_ascii=True), flush=True)
result = {'run_directory': str(RUN), 'source_ace_head': subprocess.check_output(['git', '-C', str(ACE), 'rev-parse', 'HEAD']).decode().strip(),
          'node': command([NODE, '--version'], RUN), 'npm': command([NPM, '--version'], RUN), 'cases': results}
(RUN / 'verification.json').write_text(json.dumps(result, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
(ROOT / 'latest-verification-path.txt').write_text(str(RUN / 'verification.json') + '\n', encoding='utf-8')
print('RESULT', RUN / 'verification.json', flush=True)
