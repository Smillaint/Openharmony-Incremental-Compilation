from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import importlib.util
import json
import os
import tempfile

ROOT = Path(__file__).parent
BASE = ROOT / 'base'
PATCH = ROOT / 'gate-patch'
EXPECTED = ['hb/util/loader/load_ohos_build.py', 'ohos/hisysevent/hisysevent_process.py']
manifest = json.loads((PATCH / '3dc5695a126e2c9b3de9336ad8a290d2b66c8d29.json').read_text(encoding='utf-8'))
assert sorted(manifest) == sorted(EXPECTED)
assert all(value == 'M' for value in manifest.values())
assert all((PATCH / 'old' / name).read_bytes() == (BASE / name).read_bytes() for name in EXPECTED)
pr_files = json.loads((ROOT / 'files.json').read_text(encoding='utf-8'))
blob_ids = {item['filename']: item['blob_id'] for item in pr_files}
for name in EXPECTED:
    content = (PATCH / 'new' / name).read_bytes()
    blob_id = hashlib.sha1(b'blob ' + str(len(content)).encode('ascii') + b'\0' + content).hexdigest()
    assert blob_id == blob_ids[name]
spec = importlib.util.spec_from_file_location('base_file_utils', BASE / 'scripts/util/file_utils.py')
file_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(file_utils)


def loader(version):
    source = (PATCH / version / EXPECTED[0]).read_text(encoding='utf-8')
    function = next(node for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name == 'process_other_parts')
    namespace = {'os': os, 'write_json_file': file_utils.write_json_file,
                 'LogUtil': SimpleNamespace(hb_info=lambda *args, **kwargs: None),
                 'Config': SimpleNamespace(log_mode='silent')}
    exec(compile(ast.Module(body=[function], type_ignores=[]), '<actual-process-other-parts>', 'exec'), namespace)
    return namespace['process_other_parts']


functions = {version: loader(version) for version in ['old', 'new']}
names = ['parts_variants', 'parts_inner_kits_info', 'parts_targets',
         'phony_target', 'hisysevent_config', 'parts_deps']
results = []
with tempfile.TemporaryDirectory(prefix='metadata-', dir=ROOT) as temporary:
    folder = Path(temporary)
    for name in names:
        initial = {'ace_ets2bundle': ['//developtools/ace_ets2bundle:target', '//build:dependency']}
        changed = {'ace_ets2bundle': ['//developtools/ace_ets2bundle:target', '//build:new_dependency']}
        filename = {'hisysevent_config': 'hisysevent_configs',
                    'parts_inner_kits_info': 'inner_kits_info'}.get(name, name) + '.json'
        paths = {}
        for version, function in functions.items():
            output = folder / name / version
            path = output / filename
            function(name, {name: initial}, str(output))
            paths[version] = path
            assert json.loads(path.read_text(encoding='utf-8')) == initial
        assert paths['old'].read_bytes() == paths['new'].read_bytes()
        unchanged_mtimes = {}
        for version, function in functions.items():
            path = paths[version]
            os.utime(path, ns=(1000000000, 1000000000))
            function(name, {name: initial}, str(path.parent))
            unchanged_mtimes[version] = path.stat().st_mtime_ns == 1000000000
            function(name, {name: changed}, str(path.parent))
            assert json.loads(path.read_text(encoding='utf-8')) == changed
        assert unchanged_mtimes == {'old': False, 'new': name == 'hisysevent_config'}
        assert paths['old'].read_bytes() == paths['new'].read_bytes()
        for version, function in functions.items():
            path = paths[version]
            assert path.resolve().is_relative_to(folder.resolve())
            path.unlink()
            function(name, {name: changed}, str(path.parent))
            assert json.loads(path.read_text(encoding='utf-8')) == changed
        assert paths['old'].read_bytes() == paths['new'].read_bytes()
        results.append({'branch': name, 'initial_bytes_identical': True,
                        'dependency_payload_identical': True, 'real_change_written': True,
                        'missing_output_restored': True, 'unchanged_mtime_preserved': unchanged_mtimes})
log_path = Path('D:/workspace/archives/20261018-7006-gate/sdk-complete-ditribute_job_client_failed.log')
log_lines = log_path.read_text(encoding='utf-8').splitlines()
assert 'run npm install in ' in log_lines[2006] and 'ace_ets2bundle/ets1.2' in log_lines[2006]
install_config = json.loads((BASE / 'prebuilts_config.json').read_text(encoding='utf-8'))
summary = {
    'head': '3dc5695a126e2c9b3de9336ad8a290d2b66c8d29',
    'base': '6b6d6533967db07e8e7d40d140fc63d0faabacbd',
    'gate_patch_matches_pr': True, 'gate_old_matches_exact_base': True,
    'only_changed_files': sorted(manifest),
    'npm_install_invoked': {'line': 2007, 'text': log_lines[2006]},
    'metadata_branch_checks': results,
    'test_boundary': 'Actual loader function and exact-base JSON writer; logging/config display are stubbed. No complete product GN/Ninja or npm installation was run.',
    'root_cause_boundary': 'Installation was invoked; install output and CI node_modules state are insufficient to explain the later TS6053.',
}
(ROOT / 'verification.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
excerpt = '\n'.join(f'{index+1}: {log_lines[index]}'.rstrip() for index in range(1970, 2024)) + '\n'
(ROOT / 'npm-install-excerpt.txt').write_text(excerpt, encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
