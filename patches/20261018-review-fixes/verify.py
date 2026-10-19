from pathlib import Path
from unittest.mock import patch
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import py_compile
import subprocess
import sys
import tempfile


ROOT = Path(__file__).parent
GN = Path(os.environ.get('OPENHARMONY_REVIEW_GN',
                        'D:/workspace/archives/20261018-ringking0-review/tools/gn.exe'))
PLAN = json.loads((ROOT / 'plan.json').read_text(encoding='utf-8'))
RESULTS = []
sys.dont_write_bytecode = True


def record(name, **details):
    RESULTS.append({'name': name, 'passed': True, **details})
    print('PASS', name, flush=True)


def run(command, cwd=None):
    result = subprocess.run([str(value) for value in command], cwd=cwd, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout.decode('utf-8', errors='replace')
                           + result.stderr.decode('utf-8', errors='replace'))
    return result.stdout.decode('utf-8')


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8', newline='\n')


def gn_fixture(path):
    path.mkdir(parents=True, exist_ok=True)
    write(path / '.gn', 'buildconfig = "//BUILDCONFIG.gn"\n')
    write(path / 'BUILDCONFIG.gn', 'set_default_toolchain("//:tc")\n')
    return '''toolchain("tc") {
  tool("stamp") {
    command = "cmd /c echo > {{output}}"
  }
}
'''


def desc(path, target):
    run([GN, 'gen', 'out'], path)
    details = json.loads(run([GN, 'desc', 'out', target, '--format=json'], path))
    return next(iter(details.values()))


hashes = set()
for number in [6965, 6999, 7009, 7046, 7134]:
    source = ROOT / 'files' / str(number) / 'scripts/util/file_utils.py'
    hashes.add(hashlib.sha256(source.read_bytes()).hexdigest())
    spec = importlib.util.spec_from_file_location(f'file_utils_{number}', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix=f'json-{number}-', dir=ROOT) as temporary:
        path = Path(temporary) / 'output.json'
        for malformed in ['', '{', 'not json']:
            write(path, malformed)
            with contextlib.redirect_stdout(io.StringIO()):
                module.write_json_file(str(path), {'b': 2, 'a': 1}, check_changes=True)
            assert json.loads(path.read_text(encoding='utf-8')) == {'a': 1, 'b': 2}
        os.utime(path, ns=(1_000_000_000, 1_000_000_000))
        before = path.read_bytes(), path.stat().st_mtime_ns
        module.write_json_file(str(path), {'a': 1, 'b': 2}, check_changes=True)
        assert (path.read_bytes(), path.stat().st_mtime_ns) == before
        module.write_json_file(str(path), {'a': 3}, check_changes=True)
        assert json.loads(path.read_text(encoding='utf-8')) == {'a': 3}
        for failure in [PermissionError('fixture permission'), OSError('fixture I/O')]:
            with patch.object(module, 'read_json_file', side_effect=failure):
                try:
                    module.write_json_file(str(path), {}, check_changes=True)
                except type(failure):
                    pass
                else:
                    raise AssertionError('I/O error was swallowed')
        missing = path.parent / 'missing.json'
        module.write_json_file(str(missing), {}, check_changes=True)
        assert missing.read_text(encoding='utf-8').strip() == '{}'
    record(f'PR {number}: JSON recovery, unchanged mtime, changed/missing output and I/O errors')
assert len(hashes) == 1
record('Five duplicate file_utils versions remain byte-identical')

templates = []
for number in [6974, 6999]:
    text = (ROOT / 'files' / str(number) / 'ohos/app/app_internal.gni').read_text(encoding='utf-8')
    start = text.index('template("app_sign") {')
    template = text[start:text.index('\ntemplate(', start + 1)]
    templates.append(template)
    for scenario in ['builtin', 'external', 'external_without_version', 'explicit_builtin']:
        fixture = ROOT / 'gn-sign' / str(number) / scenario
        toolchain = gn_fixture(fixture)
        defaults = '''default_hap_private_key_path = "fixture-key"
default_key_alias = "fixture-alias"
default_signature_algorithm = "fixture-algorithm"
default_keystore_path = "//fixture.keystore"
default_hap_certificate_file = "//fixture.cer"
default_keystore_password = "fixture-password"
hapsigner = "//fixture.jar"
'''
        if scenario.startswith('external'):
            defaults += 'sign_hap_py_path = "//vendor_sign.py"\n'
        elif scenario == 'explicit_builtin':
            defaults += 'sign_hap_py_path = "//build/scripts/app_sign.py"\n'
        write(fixture / 'defaults.gni', defaults)
        write(fixture / 'build/scripts/app_sign.py', 'pass\n')
        write(fixture / 'vendor_sign.py', 'pass\n')
        invocation = '''app_sign("sample") {
  certificate_profile = "//fixture.p7b"
  unsigned_hap_path_list = "//unsigned.json"
  hap_out_dir = "$root_out_dir/haps"
  hap_name = "sample"
  hap_list = "//hap_list.json"
  install_module_info = {
    module_def = "sample"
  }
'''
        if scenario in ['external', 'explicit_builtin']:
            invocation += '  compatible_version = "fixture-version"\n'
        invocation += '}\n'
        write(fixture / 'BUILD.gn', 'import("//defaults.gni")\n' + toolchain + template + invocation)
        info = desc(fixture, '//:sample')
        internal = scenario != 'external'
        assert info['script'] == ('//build/scripts/app_sign.py' if internal else '//vendor_sign.py')
        assert ('--output-file' in info['args']) == internal
        assert len(info['outputs']) == 1
        assert info['outputs'][0].endswith('.sign_result.json' if internal else '.stamp')
        if not internal:
            parser = argparse.ArgumentParser()
            for option in ['--keyPwd', '--sign-algo', '--profileFile', '--keyalias',
                           '--keystoreFile', '--keystorePwd', '--certificate-file',
                           '--hapsigner', '--unsigned-hap-path-list', '--hap-out-dir',
                           '--hap-name', '--hap-list', '--compatible_version']:
                parser.add_argument(option)
            parser.parse_args(info['args'])
        write(fixture / 'target.json', json.dumps(info, ensure_ascii=False, indent=2) + '\n')
    record(f'PR {number}: exact app_sign template passes four signer configurations and strict vendor parser')
assert templates[0] == templates[1]
record('Both duplicate app_sign templates remain identical')

text = (ROOT / 'files/6982/config/components/idl_tool/idl.gni').read_text(encoding='utf-8')
start = text.index('  idl_inner = false\n')
initialization = text[start:text.index('  if (defined(invoker.sources))', start)]
start = text.index('    deps = []\n', text.index('  action('))
dependencies = text[start:text.index('    depfile =', start)]
for arkui in [False, True]:
    for inner in [None, False, True]:
        fixture = ROOT / 'gn-idl' / f'{arkui}-{inner}'
        toolchain = gn_fixture(fixture)
        write(fixture / 'defaults.gni',
              f'is_arkui_x = {str(arkui).lower()}\n'
              'idl_build_deps = [ "//:idl_tool" ]\nhost_toolchain = "//:tc"\n')
        body = ('import("//defaults.gni")\n' + toolchain
                + 'group("idl_tool") {}\ngroup("common") {}\n'
                + 'template("idl_probe") {\n  source = invoker.src_idl\n'
                + initialization + '  action(target_name) {\n' + dependencies
                + '    if (defined(external_deps)) { not_needed([ "external_deps" ]) }\n'
                + '    script = "//noop.py"\n    args = [ source ]\n'
                + '    outputs = [ "$target_gen_dir/output.h" ]\n  }\n}\n'
                + 'idl_probe("sample") {\n  src_idl = "Example.idl"\n  deps = [ "//:common" ]\n')
        if inner is not None:
            body += f'  idl_inner = {str(inner).lower()}\n'
        body += '}\n'
        write(fixture / 'BUILD.gn', body)
        write(fixture / 'noop.py', 'pass\n')
        info = desc(fixture, '//:sample')
        assert '//:common' in info['deps']
        assert ('//:idl_tool' in info['deps']) == (arkui or inner is True)
record('IDL generation dependencies and ArkUI-X pass all six flag combinations')

for item in PLAN:
    for name in item['files']:
        source = ROOT / 'files' / str(item['number']) / name
        source.read_text(encoding='utf-8')
        if source.suffix == '.py':
            py_compile.compile(str(source), cfile=str(ROOT / f"{item['number']}.pyc"), doraise=True)
        else:
            result = subprocess.run([str(GN), 'format', '--stdin'], input=source.read_bytes(), capture_output=True)
            assert result.returncode == 0, result.stderr.decode('utf-8', errors='replace')
record('All changed files parse as UTF-8, Python bytecode and GN syntax')
write(ROOT / 'verification.json', json.dumps({
    'checks': RESULTS, 'gn_version': run([GN, '--version']).strip(),
    'product_build_run': False, 'community_gate_triggered': False,
}, ensure_ascii=False, indent=2) + '\n')
