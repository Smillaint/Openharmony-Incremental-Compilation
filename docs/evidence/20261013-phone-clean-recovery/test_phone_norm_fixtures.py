from pathlib import Path
import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
DEST = Path('/srv/workspace/patch_backups/20261013_phone_norm')
passed = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def state(folder):
    return {p.relative_to(folder).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in folder.rglob('*') if p.is_file()}


for kind, relative in [('plugins', 'arkui-plugins/build_ui_plugins.py'),
                       ('wrapper', 'koala-wrapper/build_ts_wrapper.py')]:
    mod = load(kind, ROOT / 'developtools/ace_ets2bundle' / relative)
    with tempfile.TemporaryDirectory(dir=DEST, prefix=kind + '-fixture-') as tmp:
        folder = Path(tmp)
        source = folder / 'source' / kind
        source.mkdir(parents=True)
        for name in ['package.json', 'babel.config.js', 'tsconfig.json',
                     'custom-import-plugin.js', 'koalaui-transform.js']:
            (source / name).write_text('{}', encoding='utf-8')
        ts_file = source / ('example.ts' if kind == 'plugins' else 'src/example.ts')
        ts_file.parent.mkdir(exist_ok=True)
        ts_file.write_text('source', encoding='utf-8')
        if kind == 'plugins':
            from sdk_files import RUNTIME_DEPS
            for package in RUNTIME_DEPS:
                path = source / 'node_modules' / package / 'package.json'
                path.parent.mkdir(parents=True)
                path.write_text('{}', encoding='utf-8')
            output_name = 'lib/example.js'
        else:
            output_name = 'build/lib/example.js'
        native = folder / 'native.node'
        native.write_bytes(b'native')
        output = folder / 'out/gen'
        options = argparse.Namespace(source_path=str(source), output_path=str(output),
            npm=str(folder / 'fake-npm'), state_file=str(folder / 'out/state.json'),
            native_file=str(native), current_os='linux', root_out_dir=str(folder / 'out'))
        mod.parse_args = lambda: options
        fail = [False]
        commands = []
        def fake_run(command, execution_path=None):
            assert execution_path == str(source)
            commands.append(command)
            if fail[0]:
                raise RuntimeError('simulated compiler failure')
            flag = '--out-dir' if '--out-dir' in command else '--outDir'
            directory = Path(command[command.index(flag) + 1])
            directory.relative_to(folder / 'out')
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'example.js').write_text('generated', encoding='utf-8')
        mod.run_cmd = fake_run
        before_source = state(source)
        mod.main()
        before = state(output)
        mod.main()
        assert state(output) == before
        (output / output_name).unlink()
        mod.main()
        assert (output / output_name).read_text(encoding='utf-8') == 'generated'
        before = state(output)
        fail[0] = True
        try:
            mod.main()
            raise AssertionError('Failed generator succeeded')
        except RuntimeError:
            assert state(output) == before
        assert state(source) == before_source
        assert not list((folder / 'out').glob('.*-*/'))
        if kind == 'wrapper':
            assert any('--tsBuildInfoFile' in command for command in commands)
            assert (output / 'build/native/es2panda.node').read_bytes() == b'native'
        passed.append(kind + ': out-only commands, stable output, missing output recovery, failure safety')

idl = load('idl_recovery', ROOT / 'build/config/components/idl_tool/idl.py')
with tempfile.TemporaryDirectory(dir=DEST, prefix='idl-fixture-') as tmp:
    folder = Path(tmp)
    source, output = folder / 'source', folder / 'out/gen/api'
    source.mkdir()
    (source / 'IService.idl').write_text('import Data;\ninterface IService {}', encoding='utf-8')
    (source / 'Data.idl').write_text('import Nested;\n', encoding='utf-8')
    (source / 'Nested.idl').write_text('// import Ignored;\n', encoding='utf-8')
    tool = folder / 'tool'
    tool.mkdir()
    (tool / 'idl').write_text('fake tool', encoding='utf-8')
    options = argparse.Namespace(src_idl=str(source / 'IService.idl'), dst_path=str(output),
        dst_file=','.join(str(output / f) for f in ['iservice.h', 'service_client.h']),
        output_root=str(folder / 'out/gen'), idl_tool_path=str(tool), language='cpp',
        log_domainid=None, log_tag=None, hitrace=None, client_enable='true', depfile=str(folder / 'out/idl.d'))
    fail, incomplete = [False], [False]
    def fake_idl(command, execution_path):
        if fail[0]:
            return 1
        stage = Path(command[command.index('-d') + 1])
        stage.relative_to(folder / 'out/gen')
        for name in ['iservice.h'] if incomplete[0] else ['iservice.h', 'service_client.h', 'undeclared.h']:
            (stage / name).write_text('header', encoding='utf-8')
        return 0
    idl.run_command = fake_idl
    before_source = state(source)
    assert idl.idl_gen_interface(options) == 0
    assert not (output / 'undeclared.h').exists()
    before = state(output)
    assert idl.idl_gen_interface(options) == 0 and state(output) == before
    (output / 'service_client.h').unlink()
    assert idl.idl_gen_interface(options) == 0
    assert (output / 'iservice.h').stat().st_mtime_ns == before['iservice.h'][1]
    before = state(output)
    fail[0] = True
    assert idl.idl_gen_interface(options) == 1 and state(output) == before
    fail[0], incomplete[0] = False, True
    try:
        idl.idl_gen_interface(options)
        raise AssertionError('Incomplete output set accepted')
    except RuntimeError:
        assert state(output) == before
    incomplete[0] = False
    shutil.rmtree(output)
    assert idl.idl_gen_interface(options) == 0
    assert {p: v[0] for p, v in state(output).items()} == {p: v[0] for p, v in before.items()}
    dependencies = Path(options.depfile).read_text(encoding='utf-8')
    assert all(name in dependencies for name in ['IService.idl', 'Data.idl', 'Nested.idl'])
    assert 'Ignored.idl' not in dependencies
    assert state(source) == before_source
    passed.append('IDL: concrete outputs, transitive imports, partial/full clean recovery, stable mtime, failure safety')

file_utils = load('json_recovery', ROOT / 'build/scripts/util/file_utils.py')
with tempfile.TemporaryDirectory(dir=DEST, prefix='json-fixture-') as tmp:
    path = Path(tmp) / 'config.json'
    file_utils.write_json_file(str(path), {'b': 2, 'a': 1}, check_changes=True)
    timestamp = path.stat().st_mtime_ns
    file_utils.write_json_file(str(path), {'a': 1, 'b': 2}, check_changes=True)
    assert path.stat().st_mtime_ns == timestamp
    path.unlink()
    file_utils.write_json_file(str(path), {'a': 1, 'b': 2}, check_changes=True)
    assert json.loads(path.read_text(encoding='utf-8')) == {'a': 1, 'b': 2}
    passed.append('JSON: semantic comparison and deleted output recovery')

(DEST / 'fixture-checks.json').write_text(json.dumps(passed, indent=2), encoding='utf-8')
for name in passed:
    print('PASS', name)
