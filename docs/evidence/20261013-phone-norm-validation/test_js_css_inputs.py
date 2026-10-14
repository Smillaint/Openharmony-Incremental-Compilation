from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
DEST = ROOT.parent / 'phone_norm_validation_20261013'
SCRIPT = ROOT / 'third_party/jsframework/js_framework_build.sh'
passed = []


def state(path):
    return {str(p.relative_to(path)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in path.rglob('*') if p.is_file()}


with tempfile.TemporaryDirectory(prefix='js-css-', dir=DEST) as tmp:
    base = Path(tmp)
    source, css, prebuilt = base / 'source', base / 'css/src', base / 'prebuilts'
    for p in [source / 'runtime/main', source / 'test', css, prebuilt / 'node/bin',
              prebuilt / 'node_modules', base / 'bin']:
        p.mkdir(parents=True)
    (css / 'index.ts').write_text('CSS source', encoding='utf-8')
    (source / 'runtime/main/index.ts').write_text('JS source', encoding='utf-8')
    (source / 'runtime/src').symlink_to(css, target_is_directory=True)
    for name in ['package.json', 'tsconfig.json', '.eslintrc', '.babelrc', 'build_strip_native_min.js']:
        (source / name).write_text('{}', encoding='utf-8')
    node = prebuilt / 'node/bin/node'
    node.write_text('''#!/bin/sh
test -f runtime/src/index.ts || exit 12
test -f runtime/main/index.ts || exit 13
if [ "$1" = build_strip_native_min.js ]; then
  [ "$FAIL_BUILD" != 1 ] || exit 7
  mkdir -p dist
  printf snapshot > dist/strip.native.min.js
else
  [ "$FAIL_TEST" != 1 ] || exit 9
fi
''', encoding='utf-8')
    node.chmod(0o755)
    npm = base / 'bin/npm'
    npm.write_text('''#!/bin/sh
case "$1 $2" in
  "install ") mkdir -p node_modules ;;
  "run build") test -f runtime/src/index.ts || exit 12; mkdir -p dist; printf snapshot > dist/strip.native.min.js ;;
  "run test:unit") exit 0 ;;
esac
''', encoding='utf-8')
    npm.chmod(0o755)

    def invoke(script, target, independent=False, fallback=False, failure=None):
        dep = css if independent else target / 'runtime/src'
        args = [str(prebuilt / 'node'), str(source / 'runtime'), str(prebuilt / 'node_modules'),
                str(source / 'package.json'), str(source / 'tsconfig.json'), str(source / '.eslintrc'),
                str(source / 'test'), str(target), str(source / '.babelrc'), 'false',
                str(base / 'missing' if fallback else prebuilt), str(source / 'build_strip_native_min.js'),
                str(dep), 'true' if independent else 'false']
        environment = dict(os.environ, PATH=str(base / 'bin') + ':' + os.environ['PATH'])
        if failure:
            environment[failure] = '1'
        return subprocess.run(['bash', str(script), *args], cwd=base, env=environment,
                              capture_output=True, text=True, encoding='utf-8')

    # Reproduce GN copy outputs that share an inode with the source files.
    repro = base / 'out-repro'
    (repro / 'runtime/src').mkdir(parents=True)
    os.link(css / 'index.ts', repro / 'runtime/src/index.ts')
    failed = invoke(DEST / 'js_framework_build.before.sh', repro)
    assert failed.returncode != 0 and 'same file' in failed.stderr, failed.stdout + failed.stderr
    passed.append('previous script reproduces same-file copy failure with hard-linked CSS output')

    for independent, fallback in [(False, False), (True, False), (False, True), (True, True)]:
        target = base / ('out-' + str(independent) + '-' + str(fallback))
        if not independent:
            (target / 'runtime/src').mkdir(parents=True)
            os.link(css / 'index.ts', target / 'runtime/src/index.ts')
        before = state(css)
        for iteration in range(3):
            if iteration == 2:
                (target / 'dist/strip.native.min.js').unlink()
            result = invoke(SCRIPT, target, independent, fallback)
            assert result.returncode == 0, result.stdout + result.stderr
            assert state(css) == before
            output = target / 'dist/strip.native.min.js'
            if iteration == 1:
                assert output.stat().st_mtime_ns == previous_mtime
            previous_mtime = output.stat().st_mtime_ns
        passed.append('repeat, output deletion and source preservation: independent={}, fallback={}'.format(independent, fallback))

    (source / 'runtime/src').unlink()
    result = invoke(SCRIPT, repro)
    assert result.returncode == 0, result.stdout + result.stderr
    passed.append('source-tree CSS symlink absent; declared output dependency still builds')
    for failure in ['FAIL_BUILD', 'FAIL_TEST']:
        result = invoke(SCRIPT, repro, failure=failure)
        assert result.returncode != 0
        passed.append('propagates ' + failure)

(DEST / 'js-css-regression.json').write_text(json.dumps(passed, indent=2) + '\n', encoding='utf-8')
print(json.dumps(passed, indent=2))
