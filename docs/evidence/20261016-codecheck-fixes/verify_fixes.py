import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).parent
REPOS = Path('D:/workspace/repositories/companion-prs-20261015')
passed = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob('*') if p.is_file()}


def verify_sdk(name):
    module = load(REPOS / 'interface_sdk-js' / (name + '.py'), name)
    with tempfile.TemporaryDirectory(prefix=name + '-', dir=ROOT) as temporary:
        root = Path(temporary)
        source = root / 'api'
        source.mkdir()
        (source / 'a.d.ts').write_text('declare const a: number;', encoding='utf-8')
        (source / '@internal').mkdir()
        (source / '@internal/hidden.d.ts').write_text('hidden', encoding='utf-8')
        output = root / 'published'
        stamp, depfile = root / 'action.stamp', root / 'action.d'
        args = ['--input', str(source), '--output', str(output),
                '--stamp', str(stamp), '--depfile', str(depfile)]
        if name == 'process_internal':
            rules = root / 'remove.json'
            rules.write_text('{}', encoding='utf-8')
            args += ['--remove', str(rules), '--name', 'fixture',
                     '--base-dir', str(root), '--project-dir', str(root), '--ispublic', 'true']

        def run():
            assert module.main(args) == 0
            assert not list(root.glob('.published.*')), 'Temporary directory left behind'

        run()
        assert (output / '@internal').exists() == (name == 'process_internal')
        initial = snapshot(output)
        times = (output.stat().st_mtime_ns, stamp.stat().st_mtime_ns, depfile.stat().st_mtime_ns)
        run()
        assert snapshot(output) == initial
        assert times == (output.stat().st_mtime_ns, stamp.stat().st_mtime_ns, depfile.stat().st_mtime_ns)
        passed.append(name + ': unchanged output and metadata timestamps; staging removed')
        (source / 'a.d.ts').unlink()
        (source / 'b.d.ts').write_text('declare const b: string;', encoding='utf-8')
        run()
        assert not (output / 'a.d.ts').exists()
        assert (output / 'b.d.ts').read_bytes() == (source / 'b.d.ts').read_bytes()
        assert 'b.d.ts' in depfile.read_text(encoding='utf-8')
        (output / 'b.d.ts').unlink()
        run()
        assert (output / 'b.d.ts').is_file()
        passed.append(name + ': changed inputs, stale-file removal, missing output recovery and depfile')

        initial = snapshot(output)
        stage_name = 'stage_output_files' if name == 'process_internal' else 'copy_files_staging'
        with patch.object(module, stage_name, side_effect=RuntimeError('Injected copy failure')):
            try:
                run()
                raise AssertionError('Copy failure swallowed')
            except RuntimeError:
                pass
        assert snapshot(output) == initial
        assert not list(root.glob('.published.*'))
        passed.append(name + ': staging failure preserves published files and cleans temporary directory')

        (source / 'b.d.ts').write_text('changed again', encoding='utf-8')
        replace = os.replace
        def fail_publish(src, dst):
            if Path(src).name.startswith('.published.') and not str(src).endswith('.old') and Path(dst) == output:
                raise OSError('Injected publication failure')
            return replace(src, dst)
        with patch.object(module.os, 'replace', side_effect=fail_publish):
            try:
                run()
                raise AssertionError('Publication failure swallowed')
            except OSError:
                pass
        assert snapshot(output) == initial
        assert not list(root.glob('.published.*'))
        passed.append(name + ': failed publication rolls back old output and removes staging')
        run()
        assert (output / 'b.d.ts').read_text(encoding='utf-8') == 'changed again'


for filename in ['process_internal', 'remove_internal']:
    verify_sdk(filename)

ace = REPOS / 'developtools_ace_ets2bundle'
current = load(ace / 'sdk_files.py', 'sdk_files_current')
baseline_text = subprocess.check_output(
    ['git', '-C', str(ace), 'show', 'backup/codecheck-fixes-20261016:sdk_files.py']).decode('utf-8')
baseline = type(sys)('sdk_files_baseline')
exec(compile(baseline_text, 'sdk_files_baseline.py', 'exec'), baseline.__dict__)
with tempfile.TemporaryDirectory(prefix='manifest-space-', dir=ROOT) as temporary:
    root = Path(temporary)
    project = root / 'developtools' / 'ace_ets2bundle'
    for kind, folder in [('plugins', 'arkui-plugins'), ('wrapper', 'koala-wrapper')]:
        source = project / folder
        source.mkdir(parents=True)
        for relative in ['package.json', 'babel.config.js', 'tsconfig.json', 'koalaui-transform.js',
                         'custom-import-plugin.js', 'src/nested/a file.ts', 'src/nested/中文.ts']:
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('{}', encoding='utf-8')
        if kind == 'plugins':
            for dependency in current.RUNTIME_DEPS:
                path = source / 'node_modules' / dependency / 'index.js'
                path.parent.mkdir(parents=True)
                path.write_text('module.exports = {};', encoding='utf-8')

        def manifest(module, extra=()):
            output = io.StringIO()
            with patch.object(sys, 'argv', ['sdk_files.py', 'manifest', kind, str(source), str(root), *extra]):
                with contextlib.redirect_stdout(output):
                    module.main()
            return output.getvalue()

        expected, actual = manifest(baseline), manifest(current)
        assert actual == expected
        assert all(p.startswith('//developtools/ace_ets2bundle/') and '\\' not in p
                   for p in json.loads(actual)['inputs'])
        target = source / 'sdk_files.json'
        manifest(current, ['--output', str(target)])
        before = target.read_bytes(), target.stat().st_mtime_ns
        manifest(current, ['--output', str(target)])
        assert (target.read_bytes(), target.stat().st_mtime_ns) == before
        passed.append(kind + ': manifest byte-identical to baseline including GN // prefix, spaces and Unicode; unchanged mtime')

for relative, filenames in [('interface_sdk-js', ['process_internal.py', 'remove_internal.py']),
                            ('developtools_ace_ets2bundle', ['sdk_files.py'])]:
    for filename in filenames:
        ast.parse((REPOS / relative / filename).read_text(encoding='utf-8'))
    subprocess.run(['git', '-C', str(REPOS / relative), 'diff', '--check'], check=True)
passed.append('All modified Python files parse as UTF-8 and git diff --check passes')
result = {'passed': passed, 'community_codecheck_run': False, 'product_build_run': False}
(ROOT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
