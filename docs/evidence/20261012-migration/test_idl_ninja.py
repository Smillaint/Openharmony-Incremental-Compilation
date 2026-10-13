import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
BACKUP = Path('/srv/workspace/patch_backups/20261012_migration_clean')
OUT = ROOT / 'out/idl_clean_validation'
NINJA = ROOT / 'prebuilts/build-tools/linux-x86/bin/ninja'
LOG = BACKUP / 'build/idl-ninja'
LOG.mkdir(exist_ok=True)
status = {'phase': 'collecting', 'results': []}


def save():
    (LOG / 'status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')


def state(outputs):
    return {str(p): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in outputs}


def run(name, targets, no_work=False):
    status['phase'] = name
    save()
    start = time.monotonic()
    command = [str(NINJA), '-w', 'dupbuild=warn', '-C', str(OUT), '-j', '4', *targets]
    with (LOG / (name + '.log')).open('w', encoding='utf-8') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    text = (LOG / (name + '.log')).read_text(encoding='utf-8')
    item = {'name': name, 'exit_code': result.returncode, 'seconds': time.monotonic() - start,
            'no_work': 'ninja: no work to do.' in text}
    status['results'].append(item)
    save()
    assert result.returncode == 0, name
    if no_work:
        assert item['no_work'], name


try:
    targets = []
    output_groups = []
    with (OUT / 'toolchain.ninja').open(encoding='utf-8') as source:
        for line in source:
            if line.startswith('  command = ') and '/idl_tool/idl.py ' in line:
                command = shlex.split(line.split(' = ', 1)[1].strip())
                outputs = [(OUT / p).resolve() for p in command[command.index('--dst-file') + 1].split(',')]
                for p in outputs:
                    p.relative_to(OUT.resolve())
                output_groups.append(outputs)
                targets.append(str(outputs[0].relative_to(OUT)))
    status['rule_count'] = len(targets)
    all_outputs = sorted(set(p for group in output_groups for p in group))
    status['output_count'] = len(all_outputs)
    assert len(targets) == 141
    run('initial', targets)
    original = state(all_outputs)
    run('unchanged', targets, no_work=True)
    removed = set(group[0] for group in output_groups)
    for p in removed:
        assert p.is_file() and not p.is_symlink()
        p.unlink()
    run('one_output_per_rule_removed', targets)
    repaired = state(all_outputs)
    assert {p: v[0] for p, v in original.items()} == {p: v[0] for p, v in repaired.items()}
    assert all(original[str(p)] == repaired[str(p)] for p in all_outputs if p not in removed)
    run('unchanged_after_partial_clean', targets, no_work=True)
    for p in all_outputs:
        assert p.is_file() and not p.is_symlink()
        p.unlink()
    tool = OUT / 'clang_x64/ability/idl_tool/idl'
    assert tool.is_file() and not tool.is_symlink()
    tool.unlink()
    run('all_outputs_and_idl_tool_removed', targets)
    assert tool.is_file()
    restored = state(all_outputs)
    assert {p: v[0] for p, v in original.items()} == {p: v[0] for p, v in restored.items()}
    run('unchanged_after_full_clean', targets, no_work=True)
    status['phase'] = 'passed'
except Exception as error:
    status['phase'] = 'failed'
    status['error'] = repr(error)
    raise
finally:
    save()
