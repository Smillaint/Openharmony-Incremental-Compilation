#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate airscan staging against an independent git apply result."""

import argparse
import hashlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, required=True)
args = parser.parse_args()
repo = args.source_root.resolve() / 'third_party/sane-airscan'
spec = importlib.util.spec_from_file_location('airscan_under_test', repo / 'patch_install.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def snapshot(directory):
    return {p.name: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in directory.iterdir() if p.suffix in ('.c', '.h')}


real_before = snapshot(repo)
with tempfile.TemporaryDirectory(prefix='airscan-regression-') as temporary:
    root = Path(temporary)
    source = root / 'source'
    expected = root / 'expected'
    output = root / 'output'
    source.mkdir()
    expected.mkdir()
    (source / 'patches').mkdir()
    for name in module.AIRSCAN_LIBRARY_FILES:
        shutil.copy2(repo / name, source / name)
        shutil.copy2(repo / name, expected / name)
    patch = source / 'patches/oh-transplant.patch'
    shutil.copy2(repo / 'patches/oh-transplant.patch', patch)
    subprocess.run(['git', 'apply', '--directory=expected', str(patch)],
                   cwd=root, check=True, capture_output=True)
    before = snapshot(source)
    module.generate_patched_sources(str(source), str(output))
    assert snapshot(source) == before
    assert all((output / name).read_bytes() == (expected / name).read_bytes()
               for name in module.AIRSCAN_LIBRARY_FILES)
    print('PASS clean input generates all 34 files equal to independent git apply')

    before = snapshot(output)
    module.generate_patched_sources(str(source), str(output))
    assert snapshot(output) == before
    print('PASS repeated execution preserves hashes and mtimes')

    (output / 'airscan.h').unlink()
    module.generate_patched_sources(str(source), str(output))
    assert (output / 'airscan.h').read_bytes() == (expected / 'airscan.h').read_bytes()
    print('PASS missing output is regenerated with patched content')

    changed = source / 'airscan-array.c'
    changed.write_text(changed.read_text(encoding='utf-8') + '\n/* regression input */\n',
                       encoding='utf-8')
    module.generate_patched_sources(str(source), str(output))
    assert (output / changed.name).read_bytes() == changed.read_bytes()
    print('PASS real input changes propagate')

    for name in module.AIRSCAN_LIBRARY_FILES:
        shutil.copy2(output / name, source / name)
    before = snapshot(output)
    module.generate_patched_sources(str(source), str(output))
    assert snapshot(output) == before
    print('PASS already patched input is neither reversed nor patched twice')

    patch.write_text('invalid patch\n', encoding='utf-8')
    try:
        module.generate_patched_sources(str(source), str(output))
    except RuntimeError:
        pass
    else:
        raise AssertionError('Invalid patch was accepted')
    assert snapshot(output) == before
    assert not list(root.glob('airscan_patch_*'))
    print('PASS conflict fails without publishing or leaking staging')

assert snapshot(repo) == real_before
print('PASS actual source hashes and mtimes are unchanged')
