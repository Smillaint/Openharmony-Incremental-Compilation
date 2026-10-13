#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run SA archive regressions with real helpers and temporary inputs/outputs."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

sys.dont_write_bytecode = True
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, required=True)
parser.add_argument('--baseline-file', type=Path,
                    help='Execute saved source text with the real helper imports')
args = parser.parse_args()
script = args.source_root.resolve() / 'build/ohos/sa_profile/sa_profile_binary.py'
spec = importlib.util.spec_from_file_location('sa_binary_under_test', script)
sa_binary = importlib.util.module_from_spec(spec)
if args.baseline_file:
    exec(compile(args.baseline_file.read_text(encoding='utf-8'), str(script), 'exec'),
         sa_binary.__dict__)
else:
    spec.loader.exec_module(sa_binary)


class BinaryArchiveTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sa-binary-regression-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input_dir = self.root / 'inputs'
        self.input_dir.mkdir()
        self.payload = self.input_dir / 'service.xml'
        self.payload.write_text('<profile>original</profile>\n', encoding='utf-8')
        self.parts = self.root / 'parts.json'
        self.parts.write_text(json.dumps([
            {'is_source': False, 'part_name': 'binary_part'}]), encoding='utf-8')
        self.archive_info = self.input_dir / 'archive.json'
        self.archive_info.write_text(json.dumps({
            'binary_part': ['service.xml']}), encoding='utf-8')
        self.output = self.root / 'result.zip'
        self.depfile = self.root / 'result.d'

    def generate(self, day=15, archive=True):
        command = [str(script), '--system-install-info-file', str(self.parts),
                   '--sa-output-dir', str(self.root / 'sa'),
                   '--sa-output-zipfile', str(self.output),
                   '--depfile', str(self.depfile)]
        if archive:
            command += ['--sa-profile-archive-info-file', str(self.archive_info)]
        # Different calendar days avoid ZIP's two-second timestamp granularity.
        clock = (2026, 9, day, 12, 0, 0, 1, 258, -1)
        with mock.patch.object(sys, 'argv', command), \
                mock.patch.object(zipfile.time, 'localtime', return_value=clock):
            self.assertEqual(sa_binary.main(), 0)

    def snapshot(self):
        return (hashlib.sha256(self.output.read_bytes()).hexdigest(),
                self.output.stat().st_mtime_ns)

    def retain_old_mtime(self):
        os.utime(self.output, ns=(1_600_000_000_000_000_000,) * 2)

    def test_nonempty_archive_is_stable_across_clock_changes(self):
        self.generate(day=15)
        self.retain_old_mtime()
        before = self.snapshot()
        self.generate(day=16)
        self.assertEqual(before, self.snapshot())

    def test_empty_archive_is_stable(self):
        self.generate(day=15, archive=False)
        self.retain_old_mtime()
        before = self.snapshot()
        self.generate(day=16, archive=False)
        self.assertEqual(before, self.snapshot())
        with zipfile.ZipFile(self.output) as result:
            self.assertEqual(result.namelist(), [])

    def test_payload_change_is_published(self):
        self.generate()
        self.retain_old_mtime()
        before = self.snapshot()
        self.payload.write_text('<profile>modified</profile>\n', encoding='utf-8')
        self.generate()
        self.assertNotEqual(before[0], self.snapshot()[0])
        self.assertNotEqual(before[1], self.snapshot()[1])
        with zipfile.ZipFile(self.output) as result:
            self.assertEqual(result.read('service.xml'), self.payload.read_bytes())

    def test_deleted_archive_is_recreated(self):
        self.generate()
        before = self.output.read_bytes()
        self.output.unlink()
        self.generate()
        self.assertEqual(before, self.output.read_bytes())

    def test_missing_payload_does_not_replace_previous_archive(self):
        self.generate()
        before = self.snapshot()
        self.payload.unlink()
        files = set(self.root.iterdir())
        with self.assertRaises(FileNotFoundError):
            self.generate()
        self.assertEqual(before, self.snapshot())
        self.assertEqual(files, set(self.root.iterdir()))

    def test_metadata_mapping_change_is_published(self):
        self.generate()
        before = self.output.read_bytes()
        self.parts.write_text(json.dumps([
            {'is_source': False, 'part_name': 'renamed_part'}]), encoding='utf-8')
        self.archive_info.write_text(json.dumps({
            'renamed_part': ['service.xml']}), encoding='utf-8')
        self.generate()
        self.assertNotEqual(before, self.output.read_bytes())
        with zipfile.ZipFile(self.output) as result:
            self.assertEqual(json.loads(result.read('part_name_info.json')),
                             {'service.xml': 'renamed_part'})

    def test_contents_order_permissions_and_dependencies_are_preserved(self):
        self.generate()
        with zipfile.ZipFile(self.output) as result:
            self.assertEqual(result.namelist(), ['service.xml', 'part_name_info.json'])
            self.assertEqual(result.read('service.xml'), self.payload.read_bytes())
            self.assertEqual(result.read('part_name_info.json'), json.dumps(
                {'service.xml': 'binary_part'}, indent=2, sort_keys=True).encode('utf-8'))
            metadata = result.getinfo('part_name_info.json')
            self.assertEqual(metadata.external_attr, 0o600 << 16)
            self.assertEqual(metadata.compress_type, zipfile.ZIP_STORED)
        dependencies = self.depfile.read_text(encoding='utf-8')
        self.assertIn(str(self.payload), dependencies)
        self.assertIn(str(self.archive_info), dependencies)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]], verbosity=2)
