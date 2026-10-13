from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
DEST = Path('/srv/workspace/patch_backups/20261013_phone_norm')
gn = ROOT / 'prebuilts/build-tools/linux-x86/bin/gn'
repo = ROOT / 'developtools/ace_ets2bundle'
spec = importlib.util.spec_from_file_location('sdk_files', repo / 'sdk_files.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = {}
for kind, sub, out in [('plugins', 'arkui-plugins', 'gen'), ('wrapper', 'koala-wrapper', 'clang_x64/gen')]:
    inputs, generated, copies = module.describe(kind, repo / sub)
    missing_inputs = [str(p) for p in inputs if not p.is_file()]
    expected = generated | set(copies)
    previous = ROOT / 'out/rk3568' / out / 'developtools/ace_ets2bundle' / sub
    existing = {p.relative_to(previous).as_posix() for p in previous.rglob('*') if p.is_file()}
    existing = {p for p in existing if p not in ['lib/ui-plugins/sysResource.js'] and not (p.endswith('.d') and '/' not in p)}
    print(kind, 'input files', len(inputs), 'output files', len(expected))
    print('MISSING INPUTS', missing_inputs[:20])
    print('NEW OUTPUTS', sorted(expected - existing)[:30])
    print('UNDECLARED OLD OUTPUTS', sorted(existing - expected)[:30])
    result[kind] = dict(input_count=len(inputs), output_count=len(expected), missing_inputs=missing_inputs,
                        new_outputs=sorted(expected - existing), old_outputs_not_declared=sorted(existing - expected))

with tempfile.TemporaryDirectory(dir=DEST, prefix='publish-test-') as temporary:
    root = Path(temporary)
    source, output = root / 'source', root / 'output'
    source.mkdir()
    (source / 'a').write_text('old', encoding='utf-8')
    (source / 'b').write_text('B', encoding='utf-8')
    state = root / 'state.json'
    module.publish(source, output, ['a', 'b'], state)
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in output.iterdir()}
    state_before = state.stat().st_mtime_ns
    module.publish(source, output, ['a', 'b'], state)
    assert before == {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in output.iterdir()}
    assert state_before == state.stat().st_mtime_ns
    (source / 'a').write_text('new', encoding='utf-8')
    try:
        module.publish(source, output, ['a', 'b', 'missing'], state)
        raise AssertionError('Missing output was accepted')
    except FileNotFoundError:
        assert (output / 'a').read_text(encoding='utf-8') == 'old'
    (output / 'b').unlink()
    module.publish(source, output, ['a', 'b'], state)
    assert (output / 'a').read_text(encoding='utf-8') == 'new'
    assert (output / 'b').is_file()
    module.publish(source, output, ['a'], state)
    assert not (output / 'b').exists()
    assert json.loads(state.read_text(encoding='utf-8')) == ['a']
    try:
        module.publish(source, output, ['../outside'], state)
        raise AssertionError('Path traversal accepted')
    except ValueError:
        pass
    print('PASS publish: stable mtime, missing output, failure safety, stale removal, path validation')
    result['publisher_fixture'] = 'passed'

for relative in ['arkui-plugins/BUILD.gn', 'koala-wrapper/BUILD.gn', 'sdk_copy.gni']:
    subprocess.run([str(gn), 'format', str(repo / relative)], check=True)
subprocess.run([str(gn), 'format', str(ROOT / 'third_party/css-what/BUILD.gn')], check=True)
records = json.loads((DEST / 'before.json').read_text(encoding='utf-8'))
for name in records:
    folder = ROOT / name
    changed = subprocess.check_output(['git', 'diff', '--name-only', records[name]['before']], cwd=folder, text=True).splitlines()
    changed += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=folder, text=True).splitlines()
    for relative in sorted(set(changed)):
        path = folder / relative
        if path.suffix in ('.py', '.gn', '.gni', '.sh', '.ts'):
            text = path.read_text(encoding='utf-8')
            if path.suffix == '.py':
                compile(text, str(path), 'exec')
            elif path.suffix == '.sh':
                subprocess.run(['bash', '-n', str(path)], check=True)
            elif path.suffix in ('.gn', '.gni'):
                check = subprocess.run([str(gn), 'format', '--dry-run', str(path)], capture_output=True)
                assert check.returncode in (0, 2), (relative, check.stdout, check.stderr)
    subprocess.run(['git', 'diff', '--check'], cwd=folder, check=True)
print('PASS UTF-8, Python syntax, GN parser, shell syntax and diff whitespace')
(DEST / 'static-checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
