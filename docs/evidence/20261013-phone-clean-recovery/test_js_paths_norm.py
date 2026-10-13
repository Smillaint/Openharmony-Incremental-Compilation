import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
BACKUP = Path('/srv/workspace/patch_backups/20261013_phone_norm')
results = []


def state(directory):
    return {str(p.relative_to(directory)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in directory.rglob('*') if p.is_file()}


with tempfile.TemporaryDirectory(prefix='js-paths-', dir=BACKUP) as temporary:
    root = Path(temporary)
    source = root / 'source'
    out = root / 'out'
    prebuilts = root / 'prebuilts'
    for path in [source / 'runtime/src', source / 'test', prebuilts / 'node/bin',
                 prebuilts / 'node_modules', root / 'css/src', root / 'bin', out]:
        path.mkdir(parents=True, exist_ok=True)
    (source / 'runtime/src/keep.ts').write_text('source must survive', encoding='utf-8')
    (root / 'css/src/css.ts').write_text('css', encoding='utf-8')
    for name in ['package.json', 'tsconfig.json', '.eslintrc', '.babelrc', 'build_strip_native_min.js']:
        (source / name).write_text('{}', encoding='utf-8')
    node = prebuilts / 'node/bin/node'
    node.write_text('#!/bin/sh\nif [ "$1" = build_strip_native_min.js ]; then\n'
                    '  [ "$FAIL_BUILD" != 1 ] || exit 7\n'
                    '  mkdir -p dist; printf snapshot > dist/strip.native.min.js\n'
                    'else\n  [ "$FAIL_TEST" != 1 ] || exit 9\nfi\n', encoding='utf-8')
    node.chmod(0o755)
    npm = root / 'bin/npm'
    npm.write_text('#!/bin/sh\ncase "$1 $2" in\n'
                   '"install ") mkdir -p node_modules ;;\n'
                   '"run build") mkdir -p dist; printf snapshot > dist/strip.native.min.js ;;\n'
                   '"run test:unit") exit 0 ;;\nesac\n', encoding='utf-8')
    npm.chmod(0o755)
    before = state(source)

    def run(name, independent=False, fallback=False, failure=None):
        target = out / name
        args = [str(prebuilts / 'node'), str(source / 'runtime'), str(prebuilts / 'node_modules'),
                str(source / 'package.json'), str(source / 'tsconfig.json'), str(source / '.eslintrc'),
                str(source / 'test'), str(target), str(source / '.babelrc'), 'false',
                str(root / 'missing-prebuilts' if fallback else prebuilts),
                str(source / 'build_strip_native_min.js'), str(root / 'css/src'),
                'true' if independent else 'false']
        env = dict(os.environ, PATH=str(root / 'bin') + os.pathsep + os.environ['PATH'])
        if failure:
            env[failure] = '1'
        result = subprocess.run(['bash', str(ROOT / 'third_party/jsframework/js_framework_build.sh'), *args],
                                cwd=out, env=env, capture_output=True, text=True, encoding='utf-8')
        if failure:
            assert result.returncode != 0, result.stdout + result.stderr
        else:
            assert result.returncode == 0, result.stdout + result.stderr
            assert (target / 'dist/strip.native.min.js').read_text(encoding='utf-8') == 'snapshot'
        assert state(source) == before
        return target

    for independent, fallback in [(False, False), (True, False), (False, True), (True, True)]:
        name = '{}-{}'.format(independent, fallback)
        target = run(name, independent, fallback)
        snapshot = target / 'dist/strip.native.min.js'
        previous = snapshot.stat().st_mtime_ns
        run(name, independent, fallback)
        assert snapshot.stat().st_mtime_ns == previous
        snapshot.unlink()
        run(name, independent, fallback)
        results.append('normal/repeated/deleted output; independent={}, npm fallback={}'.format(independent, fallback))
    for failure in ['FAIL_BUILD', 'FAIL_TEST']:
        run(failure, failure=failure)
        results.append('propagates ' + failure)

(BACKUP / 'js-path-regression.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print(json.dumps(results, indent=2))
