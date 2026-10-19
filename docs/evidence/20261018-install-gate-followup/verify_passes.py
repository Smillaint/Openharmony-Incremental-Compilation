from datetime import datetime, timezone
from pathlib import Path
import io
import json
import re
import tarfile
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent


def download(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


event = json.loads(download('https://dcp.openharmony.cn/api/codecheckAccess/ci-portal/v1/event/6ad58a7364650f998b07fb47').decode('utf-8'))
(ROOT / 'hisysevent-retry-event.json').write_text(json.dumps(event, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
assert event['data']['result'] == 'success'
assert event['data']['prMsg'][0]['headCommitId'] == '3dc5695a126e2c9b3de9336ad8a290d2b66c8d29'
sdk = json.loads((ROOT / 'sdk-event.json').read_text(encoding='utf-8'))['data']
assert sdk['result'] == 'success'
sdk_heads = {item['repoName']: item['headCommitId'] for item in sdk['prMsg']}
assert sdk_heads == {'build': '72115384f783e09832216c951e7743b944fd5893',
                     'interface_sdk-js': '7b42242e2fec2fba4fd33b469d8bbf0bf49ab209'}

url = 'https://cidownload.openharmony.cn/Artifacts/ohos-sdk/20261019-1-00501/log/build.log.zip'
raw = download(url)
(ROOT / 'hisysevent-success-build.log.zip').write_bytes(raw)
with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
    members = [member for member in archive if member.isfile()]
    assert len(members) == 1
    content = archive.extractfile(members[0]).read().decode('utf-8')
manifest_urls = sorted(set(re.findall(r'https://cidownload\.openharmony\.cn/tag/[^\s\x27\x22]+/manifest\.xml', content)))
assert len(manifest_urls) == 1
manifest = download(manifest_urls[0])
manifest.decode('utf-8')
(ROOT / 'hisysevent-success-manifest.xml').write_bytes(manifest)
projects = [dict(project.attrib) for project in ET.fromstring(manifest).iter('project')
            if project.get('name') in ['build', 'developtools_ace_ets2bundle']]
selected_lines = []
for number, line in enumerate(content.splitlines(), 1):
    if len(line) < 1500 and ('process npm_install' in line or 'run npm install in ' in line and 'ets1.2' in line
                            or 'ACTION //developtools/ace_ets2bundle/ets1.2/interop:interop_compile' in line):
        selected_lines.append({'line': number, 'text': line})
record = {'checked_utc': datetime.now(timezone.utc).isoformat(),
          'hisysevent_pass_gate': event['data']['id'], 'hisysevent_head': event['data']['prMsg'][0]['headCommitId'],
          'hisysevent_passed': True, 'retry_trigger_user': event['data'].get('triggerUser'),
          'hisysevent_sdk_success_log': url, 'success_manifest_url': manifest_urls[0],
          'success_projects': projects, 'success_install_and_interop_lines': selected_lines,
          'sdk_split_gate': sdk['id'], 'sdk_split_passed': True, 'sdk_split_heads': sdk_heads}
(ROOT / 'pass-verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(record, ensure_ascii=True))
