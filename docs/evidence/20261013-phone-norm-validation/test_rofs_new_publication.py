from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code');B=R.parent/'phone_norm_validation_20261013/rofs-regression';script=R/'foundation/graphic/graphic_3d/lume/LumeEngine/tools/CompilerAsset.sh'
records=json.loads((B/'before.json').read_text(encoding='utf-8'));results=[]
def state(p):return (hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mtime_ns)
def run(command,cwd,log):
 with log.open('wb') as f:return subprocess.run(command,cwd=cwd,stdout=f,stderr=subprocess.STDOUT).returncode
for i,record in enumerate(records):
 c=record['command'];c[1]=str(script);cwd=Path(record['cwd']);out=Path(record['output']);old=state(out)
 for n in range(2):assert run(c,cwd,cwd.parent/f'new-{n}.log')==0;assert state(out)==old
 out.unlink();assert run(c,cwd,cwd.parent/'missing-output.log')==0;assert state(out)[0]==old[0]
 out.unlink();out.parent.rmdir();assert run(c,cwd,cwd.parent/'missing-directory.log')==0;assert state(out)[0]==old[0]
 assert not list(cwd.glob('.rofs.*'))
 results.append({'name':record['name'],'same_bytes_as_product':True,'repeat_keeps_mtime':True,'missing_file_recovers':True,'missing_directory_recovers':True,'staging_cleaned':True})
case=B/'changed-assets';case.mkdir();(case/'source').mkdir();(case/'cwd').mkdir();data=case/'source/data.json';data.write_text('{"value":1}\n',encoding='utf-8')
c=list(records[0]['command']);c[1]=str(script);c[4]=str(case/'source');c[9]=str(case/'output');out=case/'output'/c[10]
assert run(c,case/'cwd',case/'initial.log')==0;first=state(out)
data.write_text('{"value":2}\n',encoding='utf-8');assert run(c,case/'cwd',case/'changed.log')==0;second=state(out);assert first[0]!=second[0]
assert run(c,case/'cwd',case/'stable.log')==0;assert state(out)==second
fake=case/'fake-tool';fake.mkdir();tool=fake/'LumeAssetCompiler';c[2]=str(fake)
for name,body in [('failed', '#!/bin/bash\nprintf partial > "${9}_32.o"\nexit 17\n'),('missing', '#!/bin/bash\nexit 0\n')]:
 tool.write_text(body,encoding='utf-8');tool.chmod(0o755)
 assert run(c,case/'cwd',case/(name+'.log'))!=0
 assert state(out)==second
 assert not list((case/'cwd').glob('.rofs.*'))
results.append({'changed_input_changes_output':True,'unchanged_input_keeps_mtime':True,'compiler_failure_preserves_output':True,'missing_declared_output_preserves_output':True})
(B/'after.json').write_text(json.dumps({'passed':True,'results':results},indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))
