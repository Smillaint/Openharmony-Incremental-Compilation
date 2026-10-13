import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
BACKUP = Path('/srv/workspace/patch_backups/20261012_migration_clean')
TEST = BACKUP / 'regressions'
TEST.mkdir(exist_ok=True)
results = []


def record(name):
    results.append(name)
    print('PASS', name, flush=True)


def state(path):
    return {str(p.relative_to(path)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in path.rglob('*') if p.is_file()}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


with tempfile.TemporaryDirectory(prefix='idl-', dir=TEST) as temporary:
    folder = Path(temporary)
    tool = folder / 'tool'
    tool.mkdir()
    shutil.copy2(ROOT / 'out/rk3568/clang_x64/ability/idl_tool/idl', tool / 'idl')
    sources = folder / 'source'
    sources.mkdir()
    original = ROOT / 'base/usb/usb_manager/interfaces/innerkits'
    for p in original.glob('*.idl'):
        shutil.copy2(p, sources / p.name)
    source = sources / 'IUsbServer.idl'
    source_before = state(sources)
    expected = folder / 'expected'
    expected.mkdir()
    subprocess.run([str(tool/'idl'), '-gen-cpp', '-d', str(expected), '-c', str(source), '-client-enable'], check=True)
    names = sorted(state(expected))
    assert names and 'usb_server_client.h' in names, names
    output = folder / 'out' / 'gen' / 'usb'
    depfile = folder / 'out' / 'usb.d'
    command = ['python3', str(ROOT/'build/config/components/idl_tool/idl.py'),
               '--src-idl', str(source), '--dst-path', str(output),
               '--dst-file', ','.join(str(output/n) for n in names),
               '--idl-tool-path', str(tool), '--language', 'cpp',
               '--client-enable', 'true', '--depfile', str(depfile),
               '--output-root', str(folder/'out/gen')]
    subprocess.run(command, check=True)
    assert {k:v[0] for k,v in state(output).items()} == {k:v[0] for k,v in state(expected).items()}
    assert state(sources) == source_before
    record('IDL real USB generator equivalence, client header and source-tree immutability')
    before = state(output)
    subprocess.run(command, check=True)
    assert state(output) == before
    record('IDL identical generation preserves every output mtime')
    (output / names[0]).unlink()
    subprocess.run(command, check=True)
    restored = state(output)
    assert restored[names[0]][0] == before[names[0]][0]
    assert all(restored[n] == before[n] for n in names[1:])
    record('IDL deleted output recreated without touching unchanged siblings')
    dep = depfile.read_text(encoding='utf-8')
    for name in ['IUsbServer.idl', 'IClaimExclusiveCallback.idl', 'IUsbConnectionCallback.idl', 'UsbServerTypes.idl']:
        assert name in dep, name
    record('IDL recursive imports and generator recorded as file dependencies')
    before = state(output)
    source.write_text('invalid idl source', encoding='utf-8')
    assert subprocess.run(command).returncode != 0
    assert state(output) == before
    record('IDL generator failure preserves previous complete output set')
    shutil.copy2(original / source.name, source)
    missing_command = command.copy()
    missing_command[missing_command.index('--dst-file')+1] += ',' + str(output/'missing.h')
    assert subprocess.run(missing_command).returncode != 0
    assert state(output) == before
    record('IDL undeclared generation mismatch fails before publishing')
    shutil.rmtree(output)
    subprocess.run(command, check=True)
    assert {k:v[0] for k,v in state(output).items()} == {k:v[0] for k,v in before.items()}
    record('IDL full generated directory clean recovers from source inputs')

airscan = load('airscan', ROOT/'third_party/sane-airscan/patch_install.py')
source = ROOT/'third_party/sane-airscan'
source_before = {name: (source/name).read_bytes() for name in airscan.AIRSCAN_LIBRARY_FILES}
with tempfile.TemporaryDirectory(prefix='airscan-', dir=TEST) as temporary:
    directory = Path(temporary)
    expected = directory/'expected'
    expected.mkdir()
    for name in airscan.AIRSCAN_LIBRARY_FILES:
        shutil.copy2(source/name, expected/name)
    for patch in airscan.AIRSCAN_PATCHES:
        subprocess.run(['git','apply',str(source/'patches'/patch)],cwd=expected,check=True)
    output = directory/'generated'
    airscan.generate_patched_sources(str(source),str(output))
    assert {k:v[0] for k,v in state(expected).items()} == {k:v[0] for k,v in state(output).items()}
    record('airscan all 8 upstream patches match independent git apply')
    before = state(output)
    airscan.generate_patched_sources(str(source),str(output))
    assert state(output) == before
    record('airscan all 34 output contents and mtimes stable')
    (output/'airscan.h').unlink()
    airscan.generate_patched_sources(str(source),str(output))
    assert (output/'airscan.h').read_bytes() == (expected/'airscan.h').read_bytes()
    assert all(state(output)[n] == before[n] for n in before if n != 'airscan.h')
    record('airscan missing header restored without changing siblings')
    shutil.rmtree(output)
    airscan.generate_patched_sources(str(source),str(output))
    assert {k:v[0] for k,v in state(expected).items()} == {k:v[0] for k,v in state(output).items()}
    assert all((source/n).read_bytes() == data for n,data in source_before.items())
    record('airscan clean rebuild leaves all source files unchanged')

file_utils = load('file_utils', ROOT/'build/scripts/util/file_utils.py')
with tempfile.TemporaryDirectory(prefix='metadata-', dir=TEST) as temporary:
    output = Path(temporary)/'part.json'
    file_utils.write_json_file(str(output), {'b':2,'a':1}, check_changes=True)
    before = output.stat().st_mtime_ns
    file_utils.write_json_file(str(output), {'a':1,'b':2}, check_changes=True)
    assert output.stat().st_mtime_ns == before
    output.unlink()
    file_utils.write_json_file(str(output), {'a':1,'b':2}, check_changes=True)
    assert json.loads(output.read_text(encoding='utf-8')) == {'a':1,'b':2}
    file_utils.write_json_file(str(output), {'a':3}, check_changes=True)
    assert json.loads(output.read_text(encoding='utf-8')) == {'a':3}
    record('JSON unchanged preservation, deleted-file recovery and changed-content update')

(BACKUP/'regression-results.json').write_text(json.dumps({'passed':results},indent=2),encoding='utf-8')
