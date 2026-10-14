from pathlib import Path
import shlex,subprocess,hashlib,json,shutil
R=Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code');OUT=R/'out/rk3568';B=R.parent/'phone_norm_validation_20261013/rofs-regression';B.mkdir(exist_ok=False)
script=R/'foundation/graphic/graphic_3d/lume/LumeEngine/tools/CompilerAsset.sh';shutil.copy2(script,B/'CompilerAsset.before.sh')
commands=[]
with (OUT/'toolchain.ninja').open(encoding='utf-8',errors='replace') as h:
 for line in h:
  if line.startswith('  command = ') and '/CompilerAsset.sh ' in line:
   command=shlex.split(line.split(' = ',1)[1].strip())
   actual=(OUT/command[9]/command[10]).resolve()
   if actual.is_file():commands.append((command,actual))
results=[]
for i,(original,actual) in enumerate(commands):
 case=B/str(i);case.mkdir();(case/'output').mkdir();(case/'cwd').mkdir()
 command=list(original);command[1]=str(B/'CompilerAsset.before.sh')
 for index in [2,4]:command[index]=str((OUT/command[index]).resolve())
 command[9]=str(case/'output');target=case/'output'/command[10]
 before=(hashlib.sha256(actual.read_bytes()).hexdigest(),actual.stat().st_mtime_ns)
 for round in range(2):
  with (case/f'old-{round}.log').open('wb') as log:subprocess.run(command,cwd=case/'cwd',stdout=log,stderr=subprocess.STDOUT,check=True)
  state=(hashlib.sha256(target.read_bytes()).hexdigest(),target.stat().st_mtime_ns)
  if round==0:first=state
  else:assert state[0]==first[0] and state[1]!=first[1], 'Expected same bytes and unnecessary rewrite'
 assert before==(hashlib.sha256(actual.read_bytes()).hexdigest(),actual.stat().st_mtime_ns)
 assert state[0]==before[0], 'Golden object differs'
 results.append({'name':original[8],'actual':str(actual),'same_bytes_as_product':True,'old_repeat_rewrites':True,'command':command,'cwd':str(case/'cwd'),'output':str(target)})
(B/'before.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print('PASS',len(results),'real ROFS targets, same bytes as product; old script rewrites on repeat')
