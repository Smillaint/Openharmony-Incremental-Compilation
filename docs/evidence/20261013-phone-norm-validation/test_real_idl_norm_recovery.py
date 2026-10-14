from pathlib import Path
import subprocess,shlex,hashlib,json,time
R=Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
RAW=Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_1a6915832/code')
B=R.parent/'phone_norm_validation_20261013/idl-real-recovery-v2'
B.mkdir(exist_ok=False)
N=R/'prebuilts/build-tools/linux-x86/bin/ninja'
OUT=R/'out/rk3568'
TOOL=RAW/'out/rk3568/clang_x64/ability/idl_tool'
commands=[]
for file in [OUT/'toolchain.ninja',OUT/'ohos_clang_arm64/toolchain.ninja']:
 if file.exists():
  with file.open(encoding='utf-8') as h:
   for line in h:
    if line.startswith('  command = ') and '/idl_tool/idl.py ' in line:commands.append(shlex.split(line.split(' = ',1)[1].strip()))
assert len(commands)==141

def arg(command,name):return command[command.index(name)+1]
def escaped(s):return str(s).replace('$','$$').replace(' ','$ ').replace(':','$:')
def state(files):return {str(p):(hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns) for p in files}
lines=[]; groups=[];src=set()
for i,command in enumerate(commands):
 command[1]=str((OUT/command[1]).resolve())
 command[command.index('--idl-tool-path')+1]=str(TOOL)
 for flag in ['--dst-path','--dst-file','--depfile','--output-root']:
  old=arg(command,flag)
  command[command.index(flag)+1]=','.join(str(B/(OUT/p).resolve().relative_to(OUT)) for p in old.split(','))
 outputs=[Path(p) for p in arg(command,'--dst-file').split(',')]
 groups.append(outputs)
 source=[Path(p) for p in arg(command,'--src-idl').split(',')]
 src.update(source)
 inputs=source+[Path(command[1]),TOOL/'idl']
 lines+=['rule idl'+str(i),'  command = '+shlex.join(command).replace('$','$$'), '  description = IDL '+str(i), '  depfile = '+escaped(arg(command,'--depfile')),'  restat = 1','build '+' '.join(escaped(p.relative_to(B)) for p in outputs)+': idl'+str(i)+' '+' '.join(escaped(p) for p in inputs)]
(B/'build.ninja').write_text('\n'.join(lines)+'\n',encoding='utf-8')
allout=sorted({p for g in groups for p in g}); before_source=state(sorted(src)); results=[]

def save(): (B/'status.json').write_text(json.dumps({'rules':len(commands),'outputs':len(allout),'results':results},indent=2)+'\n',encoding='utf-8')
def run(phase,empty=False):
 t=time.monotonic()
 with (B/(phase+'.log')).open('wb') as log:p=subprocess.run([str(N),'-C',str(B),'-j','2'],stdout=log,stderr=subprocess.STDOUT)
 text=(B/(phase+'.log')).read_text(encoding='utf-8',errors='replace')
 row={'phase':phase,'exit_code':p.returncode,'seconds':time.monotonic()-t,'no_work':'ninja: no work to do.' in text};results.append(row);save();print(row,flush=True)
 assert p.returncode==0, text[-3000:]
 if empty:assert row['no_work']
def remove(paths):
 for p in paths:
  assert p.resolve().is_relative_to(B) and p.is_file() and not p.is_symlink();p.unlink()
run('initial');first=state(allout)
run('unchanged',True)
removed={g[0] for g in groups};remove(removed);run('partial-clean');after=state(allout)
assert {p:v[0] for p,v in first.items()}=={p:v[0] for p,v in after.items()}
assert all(first[str(p)]==after[str(p)] for p in allout if p not in removed)
run('after-partial-clean',True)
remove(allout);run('full-clean');after=state(allout)
assert {p:v[0] for p,v in first.items()}=={p:v[0] for p,v in after.items()}
run('after-full-clean',True)
assert before_source==state(sorted(src))
(B/'passed.json').write_text(json.dumps({'passed':True,'rules':len(commands),'outputs':len(allout),'source_unchanged':True,'raw_tool_sha256':hashlib.sha256((TOOL/'idl').read_bytes()).hexdigest(),'scope':'Actual IDL commands extracted from product GN, isolated Ninja outputs and raw baseline compiler; does not replace product graph validation.'},indent=2)+'\n',encoding='utf-8')
