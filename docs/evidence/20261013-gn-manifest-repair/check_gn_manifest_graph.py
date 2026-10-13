from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
REPO = ROOT / 'developtools/ace_ets2bundle'
DEST = Path('/srv/workspace/patch_backups/20261013_gn_manifest_repair')
gn = ROOT / 'prebuilts/build-tools/linux-x86/bin/gn'
files = ['sdk_copy.gni', 'sdk_files.py', 'arkui-plugins/BUILD.gn', 'arkui-plugins/sdk_files.json',
         'arkui-plugins/build_ui_plugins.py', 'koala-wrapper/BUILD.gn',
         'koala-wrapper/sdk_files.json', 'koala-wrapper/build_ts_wrapper.py']
before = {name: hashlib.sha256((REPO / name).read_bytes()).hexdigest() for name in files}

with tempfile.TemporaryDirectory(dir=DEST, prefix='gn-graph-fixture-') as temporary:
    fixture = Path(temporary)
    def write(name, text):
        p = fixture / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
    write('.gn', 'buildconfig = "//BUILDCONFIG.gn"\nexec_script_whitelist = []\nscript_executable = "/usr/bin/env"\n')
    write('BUILDCONFIG.gn', 'set_default_toolchain("//toolchain:default")\ncurrent_os = "linux"\n')
    write('toolchain/BUILD.gn', '''toolchain("default") {
  tool("stamp") { command = "true {{output}}" }
  tool("copy") { command = "true {{source}} {{output}}" }
}
''')
    write('build/ohos.gni', '''template("ohos_copy") {
  copy(target_name) {
    forward_variables_from(invoker, [ "deps", "sources", "outputs" ])
  }
  not_needed(invoker, "*", [ "deps", "sources", "outputs" ])
}
''')
    write('build/config/components/ets_frontend/ets2abc_config.gni', '''ohos_ets_ui_plugins_path = "$root_out_dir/ohos_ets/build-tools/ui-plugins"
ohos_ets_koala_wrapper_path = "$root_out_dir/ohos_ets/build-tools/koala-wrapper"
''')
    write('BUILD.gn', '''group("default") {
  deps = [
    "//developtools/ace_ets2bundle/arkui-plugins:ohos_ets_ui_plugins",
    "//developtools/ace_ets2bundle/arkui-plugins:ui_plugin",
    "//developtools/ace_ets2bundle/koala-wrapper:ohos_ets_koala_wrapper",
    "//developtools/ace_ets2bundle/koala-wrapper:ets2panda_koala_wrapper",
  ]
}
''')
    write('developtools/ace_ets2bundle/koala-wrapper/native/BUILD.gn', '''action("es2panda") {
  script = "//dummy.py"
  outputs = [ "$root_out_dir/libes2panda.node" ]
}
''')
    write('dummy.py', '# dummy action, never executed\n')
    write('developtools/ace_ets2bundle/generateSysResource.py', '# dummy action, never executed\n')
    for name in files:
        path = fixture / 'developtools/ace_ets2bundle' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / name, path)
    for sub in ['arkui-plugins', 'koala-wrapper']:
        manifest = json.loads((REPO / sub / 'sdk_files.json').read_text(encoding='utf-8'))
        for source in manifest['inputs']:
            write(source[2:], '')
    for source in ['prebuilts/build-tools/common/nodejs/current/bin/npm', 'prebuilts/build-tools/common/nodejs/current/bin/node',
                   'base/global/system_resources/systemres/main/resources/base/element/id_defined.json']:
        write(source, '')
    generated = subprocess.run([str(gn), 'gen', str(fixture / 'out'), '--root=' + str(fixture)], text=True, capture_output=True)
    print(generated.stdout + generated.stderr)
    (DEST / 'isolated-gn.log').write_text(generated.stdout + generated.stderr, encoding='utf-8')
    assert generated.returncode == 0, 'Isolated GN graph failed'
    checked = {}
    for sub, target, count in [('arkui-plugins', 'gen_ui_plugins', 1072),
                               ('koala-wrapper', 'gen_sdk_ts_wrapper', 535),
                               ('arkui-plugins', 'ohos_ets_ui_plugins_files', 1072),
                               ('koala-wrapper', 'ohos_ets_koala_wrapper_files', 534)]:
        outputs = subprocess.check_output([str(gn), 'desc', str(fixture / 'out'),
                    '//developtools/ace_ets2bundle/' + sub + ':' + target, 'outputs', '--format=json',
                    '--root=' + str(fixture)], text=True)
        data = json.loads(outputs)
        output_files = data if isinstance(data, list) else next(iter(data.values()))['outputs']
        assert len(output_files) == count, (target, len(output_files), count)
        assert len(set(output_files)) == count
        print(target, len(output_files), 'outputs')
        checked[target] = data
    (DEST / 'isolated-gn-outputs.json').write_text(json.dumps(checked, indent=2), encoding='utf-8')
assert before == {name: hashlib.sha256((REPO / name).read_bytes()).hexdigest() for name in files}
assert (REPO / 'sdk_files.py').stat().st_mode & 0o111
assert (REPO / 'sdk_files.py').read_text(encoding='utf-8').startswith('#!/usr/bin/env python3\n')
assert not any('exec_script(' in (REPO / name).read_text(encoding='utf-8') for name in ['arkui-plugins/BUILD.gn', 'koala-wrapper/BUILD.gn'])
print('PASS isolated GN graph with empty exec_script allowlist; no actions or compiler executed')
