from pathlib import Path
import argparse, ast, importlib.util, json, os, py_compile, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode=True
HERE=Path(__file__).parent
ROOT=HERE/'verification-source'
DEST=HERE/'verification-tmp'
DEST.mkdir(exist_ok=True)
REPOS=Path(r'D:\workspace\repositories\pr-maintenance-20261015')
PREPARED=json.loads((HERE/'prepared.json').read_text(encoding='utf-8'))
REL={'build':'build','third_party_jsframework':'third_party/jsframework','third_party_sane-airscan':'third_party/sane-airscan'}
passed=[]

def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def state(folder):
    return {p.relative_to(folder).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in folder.rglob('*') if p.is_file() and '.git' not in p.relative_to(folder).parts}

for entry in PREPARED:
    repo=REPOS/entry['repo']
    for name in entry['files']:
        path=ROOT/REL[entry['repo']]/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(git(repo,'show',entry['commit']+':'+name))
        if name.endswith('.py'):
            py_compile.compile(str(path),cfile=str(DEST/(entry['repo']+'-'+path.name+'.pyc')),doraise=True)
    if entry['repo']=='third_party_sane-airscan':
        module=load('airscan_list',ROOT/REL[entry['repo']]/'patch_install.py')
        for name in module.AIRSCAN_LIBRARY_FILES+['patches/'+p for p in module.AIRSCAN_PATCHES]:
            path=ROOT/REL[entry['repo']]/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(git(repo,'show',entry['commit']+':'+name))
    # Every file matches the preserved repair, except the two narrowly recorded integrations.
    for name in entry['files']:
        if entry['number']==7046 and name=='ohos/packages/BUILD.gn':continue
        current=git(repo,'show',entry['commit']+':'+name)
        original=git(repo,'show','archive/validated:'+name)
        if entry['number']==6982 and name.endswith('idl.gni'):
            delta=git(repo,'diff','archive/validated',entry['commit'],'--',name).decode('utf-8')
            (HERE/'idl-upstream-preserved.patch').write_text(delta,encoding='utf-8')
        else:assert current==original,(entry['number'],name)
passed.append('Four PR file scopes, UTF-8 and Python bytecode compilation')

# Reuse the existing IDL and JSON recovery cases against the exact prepared commit files.
fixtures=Path(r'D:\workspace\archives\20261012-migration\test_phone_norm_fixtures.py').read_text(encoding='utf-8')
body=fixtures[fixtures.index("idl = load('idl_recovery'"):fixtures.index("(DEST / 'fixture-checks.json')")]
exec(compile(body,'existing-idl-json-fixtures','exec'))

os.environ['PATH']=r'C:\Program Files\Git\usr\bin'+os.pathsep+os.environ['PATH']
script=ROOT/'third_party/jsframework/js_framework_build.sh'
subprocess.run([r'C:\Program Files\Git\bin\bash.exe','-n',str(script)],check=True)
passed.append('JS shell syntax')

old=Path(r'D:\workspace\archives\20261012-migration\test_incremental.py').read_text(encoding='utf-8')
body=old[old.index("airscan = load('airscan'"):old.index("file_utils = load('file_utils'")]
TEST=DEST
def record(name):passed.append(name)
# Existing tests remove only generated fixture directories beneath verification-tmp.
body=body.replace('expected.mkdir()', "expected.mkdir(); subprocess.run(['git','init','-q',str(expected)],check=True)")
body=body.replace("['git','apply',", "['git','-c','core.autocrlf=false','apply','--whitespace=nowarn',")
body=body.replace('shutil.rmtree(output)', "assert output.resolve().is_relative_to(DEST.resolve()); shutil.rmtree(output)")
body=body.replace("assert {k:v[0] for k,v in state(expected).items()} == {k:v[0] for k,v in state(output).items()}", "\n    expected_state, actual_state = state(expected), state(output)\n    for key in expected_state:\n        if expected_state[key][0] != actual_state[key][0]:\n            print('OUTPUT DIFFERENCE', key, 'expected', len(expected_state[key][0]), 'actual', len(actual_state[key][0]), 'CRLF-only', expected_state[key][0].replace(b'\\r\\n',b'\\n') == actual_state[key][0].replace(b'\\r\\n',b'\\n'))\n    assert {k:v[0] for k,v in expected_state.items()} == {k:v[0] for k,v in actual_state.items()}")
exec(compile(body,'existing-airscan-fixtures','exec'))
(HERE/'verification.json').write_text(json.dumps({'passed':passed,'product_build_run':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for message in passed:print('PASS',message)
