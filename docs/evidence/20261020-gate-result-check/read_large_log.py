from pathlib import Path
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).parent
url='https://cidownload.openharmony.cn/Artifacts/dayu200_tdd/20261020-1-00694/log/build.log.zip'
request=urllib.request.Request(url,headers={'Range':'bytes=-2097152'})
with urllib.request.urlopen(request,timeout=50) as response:
    metadata={'url':url,'status':response.status,'content_range':response.headers.get('Content-Range'),
              'length':response.headers.get('Content-Length'),'type':response.headers.get('Content-Type')}
    raw=response.read(2097153)
metadata['bytes_read']=len(raw)
metadata['initial_magic']=raw[:8].hex()
if metadata['status']==206:
    (ROOT/'6999-dayu200_tdd-tail.raw').write_bytes(raw)
    lines=raw.decode('utf-8',errors='replace').splitlines()
    clean=[]
    for i,line in enumerate(lines):
        if len(line)<1700 and not re.search(r'authorization|credential|password|access.?token|secret|auth_info|private.?key|environment|\bexport\b',line,re.I):
            if i>len(lines)-50 or re.search(r'ninja: error|FAILED: |Timeout|timeout|timed out|Killed|Finished: |Maximum execution|interrupted',line):
                clean.append({'tail_line':i+1,'text':line})
    metadata['excerpts']=clean[-60:]
else:
    metadata['excerpts']=[]
    metadata['note']='Server ignored the range; response was not downloaded in full.'
(ROOT/'6999-dayu200_tdd-range.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(metadata,ensure_ascii=False))
