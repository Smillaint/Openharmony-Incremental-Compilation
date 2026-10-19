"""Read the failed ets1.2 workspace without installing or modifying files."""

from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess


def command(arguments, cwd):
    try:
        result = subprocess.run(arguments, cwd=cwd, capture_output=True, timeout=30)
        return {'returncode': result.returncode,
                'stdout': result.stdout.decode('utf-8', errors='backslashreplace').strip(),
                'stderr': result.stderr.decode('utf-8', errors='backslashreplace').strip()}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'error': str(error)}


def read_json(path):
    try:
        content = path.read_bytes()
        return json.loads(content.decode('utf-8')), hashlib.sha256(content).hexdigest()
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return {'read_error': str(error)}, None


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('project', type=Path, help='Failed workspace developtools/ace_ets2bundle/ets1.2')
parser.add_argument('--node', default='node', help='Node executable used by the failed job')
args = parser.parse_args()
project = args.project.resolve()
if not (project / 'package.json').is_file():
    parser.error('project must contain package.json')

names = ['@koalaui/build-common', '@koalaui/interop', '@koalaui/common',
         '@koalaui/compat', '@koalaui/libarkts']
report = {'project': str(project), 'node': command([args.node, '--version'], project),
          'ace_revision': command(['git', 'rev-parse', 'HEAD'], project), 'packages': []}
for folder in ['', 'common', 'compat', 'interop', 'libarkts', 'build-common']:
    directory = project / folder
    package, digest = read_json(directory / 'package.json')
    link = directory / 'node_modules/@koalaui/build-common'
    try:
        link_state = {'lexists': os.path.lexists(link), 'exists': link.exists(),
                      'is_symlink': link.is_symlink(),
                      'target': os.readlink(link) if link.is_symlink() else None,
                      'realpath': str(link.resolve()),
                      'tsconfig_exists': (link / 'tsconfig.json').is_file()}
    except OSError as error:
        link_state = {'error': str(error)}
    item = {'folder': folder or '.', 'package_sha256': digest,
            'name': package.get('name'), 'version': package.get('version'),
            'dependencies': {name: package.get('dependencies', {}).get(name) for name in names},
            'devDependencies': {name: package.get('devDependencies', {}).get(name) for name in names},
            'build_common': link_state}
    if 'read_error' in package:
        item['read_error'] = package['read_error']
    script = "try{console.log(require.resolve('@koalaui/build-common/tsconfig.json',{paths:[process.argv[1]]}))}catch(e){console.error(e.message);process.exitCode=1}"
    item['resolution'] = command([args.node, '-e', script, str(directory)], project)
    report['packages'].append(item)

report['locks'] = []
for name in ['package-lock.json', 'npm-shrinkwrap.json']:
    path = project / name
    data, digest = read_json(path)
    report['locks'].append({'name': name, 'sha256': digest, 'exists': path.is_file(),
        'lockfileVersion': data.get('lockfileVersion'), 'read_error': data.get('read_error'),
        'dependencies': {key: data.get('dependencies', {}).get(key) for key in names},
        'packages': {key: value for key, value in data.get('packages', {}).items()
                     if key in ['', 'build-common', 'interop', 'common', 'compat', 'libarkts']
                     or key in ['node_modules/' + item for item in names]}})
print(json.dumps(report, ensure_ascii=False, indent=2))
