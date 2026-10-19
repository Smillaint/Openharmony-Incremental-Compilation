#!/usr/bin/env python3
# coding: utf-8
#
# Copyright (c) 2023-2024 Huawei Device Co., Ltd.
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

import os
import subprocess
import argparse
import sys
import re
import tempfile
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src-idl', required=True, help='idl source file')
    parser.add_argument('--dst-path', required=True, help='the converted target path')
    parser.add_argument('--dst-file', required=True, help='the converted target file')
    parser.add_argument('--idl-tool-path', required=True, help='path of the idl conversion tool')
    parser.add_argument('--log-domainid', help='hilog domain id')
    parser.add_argument('--log-tag', help='hilog tag')
    parser.add_argument('--hitrace', help='hitrace switch, default off')
    parser.add_argument('--language', help='language switch, default cpp')
    parser.add_argument('--client-enable', help='gen client code')
    parser.add_argument('--depfile', help='IDL import dependencies')
    parser.add_argument('--output-root', help='root of generated outputs')
    arguments = parser.parse_args()
    return arguments


def run_command(cmd, execution_path):
    print("cmd:", " ".join(cmd))
    print("execution_path:", execution_path)
    proc = subprocess.run(cmd, cwd=execution_path)
    return proc.returncode


def idl_gen_interface(input_arguments):
    gen_language = "-gen-cpp"
    if input_arguments.language == "rust":
        gen_language = "-gen-rust"
    elif input_arguments.language == "ts":
        gen_language = "-gen-ts"

    sources = [Path(p).resolve() for p in input_arguments.src_idl.split(',')]
    outputs = [Path(p).resolve() for p in input_arguments.dst_file.split(',')]
    destination = Path(input_arguments.dst_path).resolve()
    output_root = Path(input_arguments.output_root).resolve() if input_arguments.output_root else Path(
        os.path.commonpath([str(destination)] + [str(p.parent) for p in outputs]))
    relative_destination = destination.relative_to(output_root)
    for output in outputs:
        output.relative_to(output_root)
    dependencies = collect_idl_inputs(sources)
    tool_dir = Path(input_arguments.idl_tool_path).resolve()
    tool = tool_dir / ('idl.exe' if os.name == 'nt' else 'idl')
    output_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.idl-', dir=output_root) as temporary:
        staging_root = Path(temporary)
        staging = staging_root / relative_destination
        staging.mkdir(parents=True, exist_ok=True)
        for src_idl in sources:
            cmd = [str(tool), gen_language, '-d', str(staging), '-c', str(src_idl)]
            if input_arguments.log_domainid:
                cmd += ['-log-domainid', input_arguments.log_domainid]
            if input_arguments.log_tag:
                cmd += ['-log-tag', input_arguments.log_tag]
            if input_arguments.hitrace:
                cmd += ['-t', input_arguments.hitrace]
            if input_arguments.client_enable == 'true':
                cmd += ['-client-enable']
            ret = run_command(cmd, str(tool_dir))
            if ret != 0:
                return ret
        # Validate the complete declared output set before replacing any file.
        for output in outputs:
            generated = staging_root / output.relative_to(output_root)
            if not generated.is_file():
                raise RuntimeError('IDL did not generate declared output: {}'.format(output))
        for output in outputs:
            generated = staging_root / output.relative_to(output_root)
            publish_if_changed(generated, output)
    if input_arguments.depfile:
        write_depfile(input_arguments.depfile, outputs[0], dependencies | {tool})
    return 0


def collect_idl_inputs(sources):
    dependencies = set()
    pending = list(sources)
    while pending:
        source = pending.pop().resolve()
        if source in dependencies:
            continue
        dependencies.add(source)
        text = source.read_text(encoding='utf-8')
        text = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
        for name in re.findall(r'\bimport\s+([\w./]+)\s*;', text):
            pending.append(source.parent / (name + '.idl'))
    return dependencies


def publish_if_changed(source, destination):
    content = source.read_bytes()
    if destination.is_file() and destination.read_bytes() == content:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(source, destination)


def write_depfile(path, output, dependencies):
    def escape(value):
        value = os.path.relpath(value).replace(os.sep, '/')
        return value.replace('$', '$$').replace('#', '\\#').replace(' ', '\\ ').replace(':', '\\:')

    depfile = Path(path)
    depfile.parent.mkdir(parents=True, exist_ok=True)
    depfile.write_text('{}: {}\n'.format(escape(output), ' '.join(
        escape(p) for p in sorted(dependencies))), encoding='utf-8')


if __name__ == '__main__':
    sys.exit(idl_gen_interface(parse_args()))
