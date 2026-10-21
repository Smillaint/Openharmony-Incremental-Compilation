from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import io
import json
import re
import sys
import tarfile
import urllib.request
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent
summary = json.loads((ROOT/'summary.json').read_text(encoding='utf-8'))
targets=[]
for event in summary['events']:
    if event['scope']!='new_eight' or event['result']!='failed': continue
    for build in event['builds']:
        if build['buildTarget']=='dayu600_7885' or event['number']==6999 and build['buildTarget'] in {'dayu200_tdd','x86_64_virt_tdd'}:
            artifact=build['debug'].get('Artifacts')
            if artifact: targets.append({'pr':event['number'],'target':build['buildTarget'],'url':'https://cidownload.openharmony.cn/'+artifact+'/log/build.log.zip'})

SENSITIVE = re.compile(r'authorization|credential|password|access.?token|secret|auth_info|private.?key|export\s|environment|^.*\b(?:ACCESS_KEY|AK|SK|TOKEN|PASSWORD)\s*=',re.I)
ERROR = re.compile(r'FAILED:|\berror:|ninja: (?:build stopped|error)|Traceback|ecotest|testTaskId|trigger_ecotest|pipeline running timeout|timed out|timeout|BUILD_STATUS|build failed|build success',re.I)

def fetch(item):
    stem=str(item['pr'])+'-'+item['target']
    try:
        with urllib.request.urlopen(item['url'],timeout=60) as response:
            raw=response.read(64*1024*1024+1)
        if len(raw)>64*1024*1024: raise RuntimeError('Compressed log exceeds 64 MiB')
        (ROOT/(stem+'.log.archive')).write_bytes(raw)
        stream=io.BytesIO(raw)
        if zipfile.is_zipfile(stream):
            stream.seek(0)
            with zipfile.ZipFile(stream) as z:
                name=next(x for x in z.namelist() if not x.endswith('/'))
                body=z.read(name)
        else:
            stream.seek(0)
            with tarfile.open(fileobj=stream) as t:
                member=next(m for m in t if m.isfile())
                body=t.extractfile(member).read()
        lines=body.decode('utf-8',errors='replace').splitlines()
        safe=lambda line: len(line)<1800 and not SENSITIVE.search(line)
        hits=[i for i,line in enumerate(lines) if safe(line) and ERROR.search(line)]
        first_fail=next((i for i,line in enumerate(lines) if re.search(r'FAILED:|ninja: error|Traceback',line) and safe(line)),None)
        indexes=set(hits[-45:])
        if first_fail is not None:
            indexes.update(range(max(0,first_fail-3),min(len(lines),first_fail+18)))
        indexes.update(i for i in range(max(0,len(lines)-12),len(lines)) if safe(lines[i]))
        excerpts=[{'line':i+1,'text':lines[i]} for i in sorted(indexes) if safe(lines[i])]
        result={**item,'archive_sha256':hashlib.sha256(raw).hexdigest(),'lines':len(lines),'first_fail_line':None if first_fail is None else first_fail+1,'excerpts':excerpts}
    except Exception as exc:
        result={**item,'error':str(exc)}
    (ROOT/(stem+'-excerpt.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'pr':item['pr'],'target':item['target'],'error':result.get('error'),'lines':result.get('lines'),'first_fail_line':result.get('first_fail_line'),'excerpts':result.get('excerpts',[])},ensure_ascii=False),flush=True)
    return result

with ThreadPoolExecutor(max_workers=3) as executor:
    records=list(executor.map(fetch,targets))
(ROOT/'failure-logs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
