#!/usr/bin/env python3
#coding: utf-8
"""
Copyright (c) 2022-2023 Huawei Device Co., Ltd.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Description: run script
    input: resource file
    output: output file
"""

import argparse
import os
import sys


def resource_file_to_cpp(input_dir, input_file, output_path):
    with open(os.path.join(input_dir, input_file), 'rb') \
            as resource_file_object:
        resource_content = resource_file_object.read()

    symbol_name = input_file.replace(".", "_")
    byte_code = ",".join(hex(content) for content in resource_content)
    new_content = (
        "#include <cstdint>\n"
        "extern const uint8_t  _binary_{}_start[{}] = {{{}}};\n"
        "extern const uint32_t _binary_{}_length = {};"
    ).format(
        symbol_name,
        len(resource_content),
        byte_code,
        symbol_name,
        len(resource_content),
    )

    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as output_file:
            if output_file.read() == new_content:
                return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    temporary_path = "{}.tmp".format(output_path)
    with open(temporary_path, 'w', encoding='utf-8', newline='\n') as output_file:
        output_file.write(new_content)
    os.replace(temporary_path, output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)

    args = parser.parse_args()

    input_dir, input_file = os.path.split(args.input)
    output_path = os.path.abspath(args.output)
    resource_file_to_cpp(input_dir, input_file, output_path)


if __name__ == '__main__':
    sys.exit(main())
