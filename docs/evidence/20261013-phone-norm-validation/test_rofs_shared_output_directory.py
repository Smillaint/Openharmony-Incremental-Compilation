from pathlib import Path
import json,subprocess,hashlib
R=Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code');B=R.parent/'phone_norm_validation_20261013/rofs-regression';case=B/'shared-assets-output';case.mkdir();assets=case/'assets';assets.mkdir();cwd=case/'cwd';cwd.mkdir();(assets/'data.json').write_text('{"value":1}\n',encoding='utf-8')
c=json.loads((B/'before.json').read_text(encoding='utf-8'))[0]['command'];c[1]=str(R/'foundation/graphic/graphic_3d/lume/LumeEngine/tools/CompilerAsset.sh');c[4]=str(assets);c[9]=str(assets);out=assets/c[10]
def state():return (hashlib.sha256(out.read_bytes()).hexdigest(),out.stat().st_mtime_ns)
def run(name):
 with (case/(name+'.log')).open('wb') as f:subprocess.run(c,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
run('initial');first=state();run('with-generated-object');assert state()==first
(assets/'.unrelated.stamp').write_text('metadata',encoding='utf-8');run('with-unrelated-entry');assert state()==first
(assets/'.unrelated.stamp').unlink();run('after-unrelated-entry-removed');assert state()==first
assert not list(cwd.glob('.rofs.*'))
p=B/'after.json';s=json.loads(p.read_text(encoding='utf-8'));s['results'].append({'shared_assets_and_output_directory':True,'first_output_creation_keeps_repeated_bytes_and_mtime':True,'unrelated_directory_entries_keep_output_stable':True,'sha256':first[0]});p.write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
print('PASS shared input/output directory, first generated object and unrelated entries do not change ROFS bytes or mtime')
