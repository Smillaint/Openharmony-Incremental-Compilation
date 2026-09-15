from pathlib import Path
import tempfile,subprocess,os,time
root=Path('/srv/workspace/openharmony_master_default_20260906175718_huawei_10dfe505f/code')
script=root/'build/templates/kernel/linux-6.6/make_ko.sh'
with tempfile.TemporaryDirectory(prefix='ko-regression-') as tmp:
 p=Path(tmp);src=p/'src';src.mkdir();out=p/'out';out.mkdir();proj=p/'project'
 for d in ['build/templates/kernel/linux-6.6','out/kernel/OBJ/linux-6.6/certs','out/kernel/OBJ/linux-6.6/scripts']:(proj/d).mkdir(parents=True,exist_ok=True)
 (proj/'build/templates/kernel/linux-6.6/Makefile').write_text('# fixture\n')
 (proj/'out/kernel/OBJ/linux-6.6/certs/signing_key.pem').write_text('fixture, not a key\n')
 tools=p/'tools';tools.mkdir();make=tools/'make';make.write_text('#!/bin/bash\nif [ "$1" != "clean" ]; then cp "$FIXTURE_PAYLOAD" kosample.ko; fi\n');make.chmod(0o755)
 sign=proj/'out/kernel/OBJ/linux-6.6/scripts/sign-file';sign.write_text('#!/bin/bash\nexit "${SIGN_FAIL:-0}"\n');sign.chmod(0o755)
 payload=p/'payload';payload.write_bytes(b'original module');env=dict(os.environ,PATH=str(tools)+':'+os.environ['PATH'],FIXTURE_PAYLOAD=str(payload))
 cmd=['bash',str(script),str(src),'kosample',str(out),str(proj),'rk3568','arm64','ko_sample']
 def run(fail=False):
  result=subprocess.run(cmd,env=dict(env,SIGN_FAIL='1' if fail else '0'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  assert (result.returncode!=0)==fail,result.stdout
 dest=out/'kosample.ko';run();assert dest.read_bytes()==payload.read_bytes();print('PASS initial publish')
 old=dest.stat().st_mtime_ns;time.sleep(.05);run();assert dest.stat().st_mtime_ns==old;print('PASS same content preserves mtime')
 payload.write_bytes(b'changed module');run();assert dest.read_bytes()==payload.read_bytes();assert dest.stat().st_mtime_ns!=old;print('PASS changed input publishes')
 dest.unlink();run();assert dest.read_bytes()==payload.read_bytes();print('PASS missing output restored')
 old=dest.read_bytes(),dest.stat().st_mtime_ns;payload.write_bytes(b'unpublished module');run(True);assert (dest.read_bytes(),dest.stat().st_mtime_ns)==old;print('PASS signing failure preserves output')
