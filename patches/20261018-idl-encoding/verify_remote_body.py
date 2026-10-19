from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

CODE = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
TOOL = CODE / 'out/rk3568/clang_x64/ability/idl_tool/idl'
ROOT = Path('/srv/workspace/patch_backups/20261018_idl_encoding')
ROOT.mkdir(parents=True, exist_ok=True)
RUN = Path(tempfile.mkdtemp(prefix='contract-', dir=ROOT))
scripts = {}
for name, payload in PAYLOADS.items():
    data = base64.b64decode(payload)
    data.decode('utf-8')
    script = RUN / (name + '.py')
    script.write_bytes(data)
    scripts[name] = script

BASE = 'interface OHOS.IEncodingProbe {\n    int Ping([in] int value);\n}\n'
COMMENT = '/* 中文注释 */\n'
CASES = [
    ('ascii', BASE.encode('ascii'), {}),
    ('utf8', (COMMENT + BASE).encode('utf-8'), {}),
    ('gbk', (COMMENT + BASE).encode('gbk'), {}),
    ('gb18030', ('/* 中文𠀀注释 */\n' + BASE).encode('gb18030'), {}),
    ('latin1', ('/* Café */\n' + BASE).encode('latin-1'), {}),
    ('cp1252', ('/* résumé – note */\n' + BASE).encode('cp1252'), {}),
    ('shift_jis', ('/* 日本語 */\n' + BASE).encode('shift_jis'), {}),
    ('utf8_bom', (COMMENT + BASE).encode('utf-8-sig'), {}),
    ('utf16_le', ('\ufeff' + COMMENT + BASE).encode('utf-16-le'), {}),
    ('utf16_be', ('\ufeff' + COMMENT + BASE).encode('utf-16-be'), {}),
    ('mixed_imports', ('/* UTF-8 中文 */\nimport IImported;\n'
                       'interface OHOS.IEncodingProbe {\n    int Ping([in] IImported child);\n}\n').encode('utf-8'), {
        'IImported.idl': (COMMENT + 'import ILeaf;\ninterface OHOS.IImported {\n'
                         '    int Value([in] ILeaf child);\n}\n').encode('gbk'),
        'ILeaf.idl': ('/* Café; import Missing; */\ninterface OHOS.ILeaf {\n'
                     '    int Value();\n}\n').encode('latin-1'),
    }),
    ('gbk_directory', (COMMENT + BASE).encode('gbk'), {}),
    ('invalid_gbk', (COMMENT + 'interface OHOS.IEncodingProbe { invalid syntax; }\n').encode('gbk'), {}),
    ('unicode_import', ('import 中文;\n' + BASE).encode('utf-8'), {
        '中文.idl': 'interface OHOS.中文 {};\n'.encode('utf-8'),
    }),
]


def snapshot(folder):
    return {path.relative_to(folder).as_posix(): {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'mtime_ns': path.stat().st_mtime_ns,
    } for path in folder.rglob('*') if path.is_file()}


def execute(command):
    result = subprocess.run(command, cwd=TOOL.parent, capture_output=True, timeout=30)
    return {'returncode': result.returncode,
            'stdout': result.stdout.decode('utf-8', errors='backslashreplace'),
            'stderr': result.stderr.decode('utf-8', errors='backslashreplace')}


def wrapper(name, source, output, relative_outputs, depfile=None):
    args = ['python3', str(scripts[name]), '--src-idl', str(source),
            '--dst-path', str(output), '--dst-file',
            ','.join(str(output / relative) for relative in relative_outputs),
            '--idl-tool-path', str(TOOL.parent), '--language', 'cpp']
    if name != 'legacy':
        args += ['--output-root', str(output), '--depfile', str(depfile)]
    return execute(args)


results = []
for name, data, imports in CASES:
    folder = RUN / (name + (' space 中文' if name == 'gbk_directory' else ''))
    folder.mkdir()
    source = folder / 'IEncodingProbe.idl'
    source.write_bytes(data)
    for filename, content in imports.items():
        (folder / filename).write_bytes(content)
    input_bytes = {path: path.read_bytes() for path in folder.glob('*.idl')}
    direct_out = folder / 'direct'
    direct_out.mkdir()
    direct = execute([str(TOOL), '-gen-cpp', '-d', str(direct_out), '-c', str(source)])
    direct_state = snapshot(direct_out)
    supported = direct['returncode'] == 0 and len(direct_state) >= 5
    relative_outputs = sorted(direct_state) if supported else [
        'iencoding_probe.h', 'encoding_probe_proxy.h', 'encoding_probe_proxy.cpp',
        'encoding_probe_stub.h', 'encoding_probe_stub.cpp']
    checks = {'case': name, 'supported_by_original': supported, 'direct': direct,
              'generated_count': len(direct_state), 'wrappers': {}}
    for implementation in ['legacy', 'strict', 'repaired']:
        output = folder / implementation
        depfile = folder / (implementation + '.d')
        outcome = wrapper(implementation, source, output, relative_outputs, depfile)
        checks['wrappers'][implementation] = outcome
        if supported:
            if implementation == 'strict' and name not in ['ascii', 'utf8']:
                assert outcome['returncode'] != 0 and 'UnicodeDecodeError' in outcome['stderr'], name
            else:
                assert outcome['returncode'] == 0, (name, implementation, outcome)
                actual = snapshot(output)
                assert {key: value['sha256'] for key, value in actual.items()} == {
                    key: value['sha256'] for key, value in direct_state.items()}, (name, implementation)
        elif implementation == 'repaired':
            assert outcome['returncode'] != 0, (name, outcome)
    if supported:
        output = folder / 'repaired'
        depfile = folder / 'repaired.d'
        previous = snapshot(output)
        repeated = wrapper('repaired', source, output, relative_outputs, depfile)
        assert repeated['returncode'] == 0
        assert snapshot(output) == previous, name
        assert source.name in depfile.read_text(encoding='utf-8')
        if imports:
            dependency_text = depfile.read_text(encoding='utf-8')
            assert all(filename in dependency_text for filename in imports), dependency_text
            assert 'Missing.idl' not in dependency_text
        missing = output / relative_outputs[0]
        assert missing.resolve().is_relative_to(RUN.resolve())
        missing.unlink()
        restored = wrapper('repaired', source, output, relative_outputs, depfile)
        assert restored['returncode'] == 0
        assert {key: value['sha256'] for key, value in snapshot(output).items()} == {
            key: value['sha256'] for key, value in direct_state.items()}
        checks['unchanged_mtime'] = True
        checks['missing_output_recovered'] = True
        failed_source = folder / 'IEncodingProbe.idl'
        failed_source.write_bytes(b'import Missing;\n' + data)
        preserved = snapshot(output)
        failed = wrapper('repaired', failed_source, output, relative_outputs, depfile)
        assert failed['returncode'] != 0
        assert snapshot(output) == preserved
        failed_source.write_bytes(data)
        checks['missing_import_preserves_outputs'] = True
    assert all(path.read_bytes() == content for path, content in input_bytes.items())
    results.append(checks)
    print(json.dumps({'case': name, 'original_supported': supported,
                      'generated_count': len(direct_state),
                      'wrapper_returncodes': {key: value['returncode']
                                             for key, value in checks['wrappers'].items()}}, ensure_ascii=True), flush=True)
result = {'tool_path': str(TOOL), 'tool_sha256': hashlib.sha256(TOOL.read_bytes()).hexdigest(),
          'generator_head': subprocess.check_output(['git', '-C', str(CODE / 'foundation/ability/idl_tool'),
                                                     'rev-parse', 'HEAD']).decode().strip(),
          'generator_status': subprocess.check_output(['git', '-C', str(CODE / 'foundation/ability/idl_tool'),
                                                       'status', '--short']).decode().strip(),
          'run_directory': str(RUN), 'cases': results}
(RUN / 'verification.json').write_text(json.dumps(result, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
(ROOT / 'latest-verification-path.txt').write_text(str(RUN / 'verification.json') + '\n', encoding='utf-8')
print('RESULT', RUN / 'verification.json')
