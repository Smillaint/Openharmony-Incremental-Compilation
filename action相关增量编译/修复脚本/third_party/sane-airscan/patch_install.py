#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Device Co., Ltd.
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

import argparse
import os
import subprocess
import sys
import shutil
import tempfile


AIRSCAN_LIBRARY_FILES = [
    'airscan-array.c',
    'airscan-bmp.c',
    'airscan-conf.c',
    'airscan-devcaps.c',
    'airscan-device.c',
    'airscan-devid.c',
    'airscan-devops.c',
    'airscan-eloop.c',
    'airscan-escl.c',
    'airscan-filter.c',
    'airscan-http.c',
    'airscan-id.c',
    'airscan-image.c',
    'airscan-init.c',
    'airscan-ip.c',
    'airscan-jpeg.c',
    'airscan-log.c',
    'airscan-math.c',
    'airscan-mdns.c',
    'airscan-memstr.c',
    'airscan-netif.c',
    'airscan-os.c',
    'airscan-png.c',
    'airscan-pollable.c',
    'airscan-rand.c',
    'airscan-tiff.c',
    'airscan-trace.c',
    'airscan-wsd.c',
    'airscan-xml.c',
    'airscan-zeroconf.c',
    'airscan.c',
    'airscan.h',
    'http_parser.c',
    'sane_strstatus.c',
]


def run_patch(patch_path, work_dir, reverse=False, dry_run=False):
    command = [
        'patch',
        '-p1',
        '--fuzz=0',
        '--no-backup-if-mismatch',
        '-i',
        patch_path,
        '-d',
        work_dir,
    ]
    if reverse:
        command.append('--reverse')
    if dry_run:
        command.append('--dry-run')
    return subprocess.run(command, text=True, capture_output=True)


def apply_patch(patch_path, work_dir):
    forward_check = run_patch(patch_path, work_dir, dry_run=True)
    if forward_check.returncode == 0:
        subprocess.run(
            [
                'patch', '-p1', '--fuzz=0', '--no-backup-if-mismatch',
                '-i', patch_path, '-d', work_dir,
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        return

    reverse_check = run_patch(patch_path, work_dir, reverse=True, dry_run=True)
    if reverse_check.returncode == 0:
        return

    raise RuntimeError(
        'oh-transplant.patch does not apply cleanly:\n{}'.format(
            forward_check.stderr
        )
    )


def replace_if_changed(source_path, output_path):
    with open(source_path, 'rb') as source_file:
        source_content = source_file.read()
    if os.path.exists(output_path):
        with open(output_path, 'rb') as output_file:
            if output_file.read() == source_content:
                return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    temporary_path = '{}.tmp'.format(output_path)
    with open(temporary_path, 'wb') as output_file:
        output_file.write(source_content)
    os.replace(temporary_path, output_path)


def generate_patched_sources(source_dir, output_dir):
    patch_path = os.path.abspath(
        os.path.join(source_dir, 'patches', 'oh-transplant.patch')
    )
    output_parent = os.path.dirname(output_dir)
    os.makedirs(output_parent, exist_ok=True)
    staging_dir = tempfile.mkdtemp(prefix='airscan_patch_', dir=output_parent)
    try:
        for file_name in AIRSCAN_LIBRARY_FILES:
            shutil.copy2(
                os.path.join(source_dir, file_name),
                os.path.join(staging_dir, file_name),
            )
        apply_patch(patch_path, staging_dir)
        for file_name in AIRSCAN_LIBRARY_FILES:
            replace_if_changed(
                os.path.join(staging_dir, file_name),
                os.path.join(output_dir, file_name),
            )
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    generate_patched_sources(
        os.path.abspath(args.source_dir),
        os.path.abspath(args.output_dir),
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
