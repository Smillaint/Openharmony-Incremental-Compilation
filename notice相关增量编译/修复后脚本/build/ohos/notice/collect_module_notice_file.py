#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Huawei Device Co., Ltd.
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

import sys
import argparse
import json
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
from scripts.util.file_utils import read_json_file  # noqa: E402
from scripts.util import build_utils  # noqa: E402

README_FILE_NAME = 'README.OpenSource'
LICENSE_CANDIDATES = [
    'LICENSE',
    'License',
    'NOTICE',
    'Notice',
    'COPYRIGHT',
    'Copyright',
    'COPYING',
    'Copying'
]


def is_top_dir(current_dir: str):
    return os.path.exists(os.path.join(current_dir, '.gn'))


def find_other_files(license_file_path):
    other_files = []
    if os.path.isfile(license_file_path):
        license_dir = os.path.dirname(license_file_path)
        license_file = os.path.basename(license_file_path)
        for file in LICENSE_CANDIDATES:
            license_path = os.path.join(license_dir, file)
            if os.path.isfile(license_path) and file != license_file and \
                    license_path not in other_files:
                other_files.append(license_path)
    elif os.path.isdir(license_file_path):
        for file in ['COPYRIGHT', 'Copyright', 'COPYING', 'Copying']:
            license_file = os.path.join(license_file_path, file)
            if os.path.isfile(license_file):
                other_files.append(license_file)
    return other_files


def find_file_recursively(current_dir: str, target_files: list):
    if is_top_dir(current_dir):
        return None
    for file in target_files:
        candidate = os.path.join(current_dir, file)
        if os.path.isfile(candidate):
            return candidate
    return find_file_recursively(os.path.dirname(current_dir), target_files)


def find_license(current_dir: str):
    return find_file_recursively(current_dir, LICENSE_CANDIDATES)


def find_opensource(current_dir: str):
    return find_file_recursively(current_dir, [README_FILE_NAME])


def get_license_from_readme(readme_path: str):
    contents = read_json_file(readme_path)
    if contents is None:
        raise Exception("Error: failed to read {}.".format(readme_path))

    if len(contents) <= 1:
        notice_file = contents[0].get('License File').strip()
        notice_files = []
        if "," in notice_file:
            notice_files = [file.strip() for file in notice_file.split(",")]
        else:
            notice_files = [notice_file]

        notice_name = contents[0].get('Name').strip()
        notice_version = contents[0].get('Version Number').strip()
        if notice_file is None:
            raise Exception("Error: value of notice file is empty in {}.".format(
                readme_path))
        if notice_name is None:
            raise Exception("Error: Name of notice file is empty in {}.".format(
                readme_path))
        if notice_version is None:
            raise Exception("Error: Version Number of notice file is empty in {}.".format(
                readme_path))

        return [os.path.join(os.path.dirname(readme_path), notice_file) for file in notice_files], notice_name, notice_version
    else:
        notice_files = []
        notice_names = []
        notice_versions = []
        for content in contents:
            notice_file = content.get('License File').strip()
            if "," in notice_file:
                notice_files_list = [file.strip() for file in notice_file.split(",")]
                notice_file = ",".join([os.path.join(os.path.dirname(readme_path), file) for file in notice_files_list])
            else:
                notice_file = os.path.join(os.path.dirname(readme_path), notice_file)

            notice_files.append(notice_file)
            notice_names.append(content.get('Name').strip())
            notice_versions.append(content.get('Version Number').strip())

        if notice_files is None:
            raise Exception("Error: value of notice file is empty in {}.".format(
                readme_path))
        if notice_names is None:
            raise Exception("Error: Name of notice file is empty in {}.".format(
                readme_path))
        if notice_versions is None:
            raise Exception("Error: Version Number of notice file is empty in {}.".format(
                readme_path))

        return notice_files, notice_names, notice_versions


def add_path_to_module_notice(module_notice_info, module_notice_info_list, options):
    if isinstance(module_notice_info.get('Software', None), list):
        softwares = module_notice_info.get('Software')
        versions = module_notice_info.get('Version')
        for software, version in zip(softwares, versions):
            module_notice_info_list.append({'Software': software, 'Version': version})
        module_notice_info_list[-1]['Path'] = "/{}".format(options.module_source_dir[5:])
    else:
        if module_notice_info.get('Software', None):
            module_notice_info['Path'] = "/{}".format(options.module_source_dir[5:])
            module_notice_info_list.append(module_notice_info)
    if module_notice_info_list:
        for module_notice_info in module_notice_info_list:
            module_path = module_notice_info.get("Path", None)
            if module_path is not None:
                module_notice_info["Path"] = module_path.replace("../", "")


def do_collect_notice_files(options, depfiles: list):
    module_notice_info_list = []
    module_notice_info = {}
    notice_file = options.license_file
    other_files = []
    if notice_file:
        opensource_file = find_opensource(os.path.abspath(options.module_source_dir))
        if opensource_file is not None and os.path.exists(opensource_file):
            depfiles.append(opensource_file)
            other_files.extend(find_other_files(opensource_file))
            notice_file_info = get_license_from_readme(opensource_file)
            module_notice_info['Software'] = notice_file_info[1]
            module_notice_info['Version'] = notice_file_info[2]
        else:
            module_notice_info['Software'] = ""
            module_notice_info['Version'] = ""
    if notice_file is None:
        readme_path = os.path.join(options.module_source_dir,
                                   README_FILE_NAME)
        if not os.path.exists(readme_path):
            readme_path = find_opensource(os.path.abspath(options.module_source_dir))
        other_files.extend(find_other_files(options.module_source_dir))
        if readme_path is not None:
            depfiles.append(readme_path)
            notice_file_info = get_license_from_readme(readme_path)
            notice_file = notice_file_info[0]
            if isinstance(notice_file, list):
                notice_file = ",".join(notice_file)
            module_notice_info['Software'] = notice_file_info[1]
            module_notice_info['Version'] = notice_file_info[2]

    if notice_file is None:
        notice_file = find_license(options.module_source_dir)
        opensource_file = find_opensource(os.path.abspath(options.module_source_dir))
        if opensource_file is not None and os.path.exists(opensource_file):
            depfiles.append(opensource_file)
            other_files.extend(find_other_files(opensource_file))
            notice_file_info = get_license_from_readme(opensource_file)
            module_notice_info['Software'] = notice_file_info[1]
            module_notice_info['Version'] = notice_file_info[2]
        else:
            module_notice_info['Software'] = ""
            module_notice_info['Version'] = ""

    add_path_to_module_notice(module_notice_info, module_notice_info_list, options)

    notice_files = []
    if notice_file:
        if other_files:
            notice_file = f"{notice_file},{','.join(other_files)}"
        notice_files = [file for file in notice_file.split(",") if file]

    # GN declares every path in options.output as an action output. Create a
    # stable empty notice when the module has no license file so Ninja does not
    # rerun the action because a declared output is missing.
    for output in options.output:
        notice_info_json = '{}.json'.format(output)
        write_file_content(notice_files, options, output, notice_info_json,
                           module_notice_info_list, depfiles)


def write_file_content(notice_files, options, output, notice_info_json, module_notice_info_list, depfiles):
    notice_contents = []
    for notice_file in notice_files:
        notice_file = notice_file.strip()
        if not os.path.exists(notice_file):
            notice_file = os.path.join(options.module_source_dir, notice_file)
        if os.path.exists(notice_file):
            with open(notice_file, 'r', encoding='utf-8', errors='ignore') as notice_file_object:
                notice_contents.append(notice_file_object.read())
            depfiles.append(notice_file)

    output_content = "".join("{}\n".format(content) for content in notice_contents)
    write_text_if_changed(output, output_content)
    write_text_if_changed(
        notice_info_json,
        json.dumps(module_notice_info_list, sort_keys=True, indent=2),
    )


def write_text_if_changed(output_path, content):
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8', errors='ignore') as output_file:
            if output_file.read() == content:
                return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    temporary_path = "{}.tmp".format(output_path)
    with open(temporary_path, 'w', encoding='utf-8', newline='\n') as output_file:
        output_file.write(content)
    os.replace(temporary_path, output_path)


def main(args):
    args = build_utils.expand_file_args(args)

    parser = argparse.ArgumentParser()
    build_utils.add_depfile_option(parser)

    parser.add_argument('--license-file', required=False)
    parser.add_argument('--output', action='append', required=True)
    parser.add_argument('--sources', action='append', required=False)
    parser.add_argument('--sdk-install-info-file', required=False)
    parser.add_argument('--label', required=False)
    parser.add_argument('--sdk-notice-dir', required=False)
    parser.add_argument('--module-source-dir',
                        help='source directory of this module',
                        required=True)

    options = parser.parse_args()
    depfiles = []

    if options.sdk_install_info_file:
        install_dir = ''
        sdk_install_info = read_json_file(options.sdk_install_info_file)
        for item in sdk_install_info:
            if options.label == item.get('label'):
                install_dir = item.get('install_dir')
                break
        if options.sources and install_dir:
            for src in options.sources:
                extend_output = os.path.join(options.sdk_notice_dir, install_dir,
                                             '{}.{}'.format(os.path.basename(src), 'txt'))
                options.output.append(extend_output)

    do_collect_notice_files(options, depfiles)
    if options.license_file:
        depfiles.append(options.license_file)
    depfiles = sorted(set(depfiles))
    build_utils.write_depfile(options.depfile, options.output[0], depfiles)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
