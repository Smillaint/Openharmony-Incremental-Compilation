from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import base64
import hashlib
import json
import urllib.request

ROOT = Path(__file__).parent
REVISION = '9e0f9e58a243d7aeab672c317a2322dc37efd1a7'
API = 'https://api.gitcode.com/api/v5/repos/openharmony/developtools_ace_ets2bundle/contents/'
FILES = ['ets1.2/package.json', 'ets1.2/interop/package.json',
         'ets1.2/libarkts/package.json', 'ets1.2/common/package.json',
         'ets1.2/compat/package.json', 'ets1.2/build-common/package.json',
         'ets1.2/common/tsconfig.json', 'ets1.2/compat/tsconfig.json',
         'ets1.2/build-common/tsconfig.json', 'ets1.2/interop/tsconfig.json']


def request(name):
    url = API + name + '?ref=' + REVISION
    with urllib.request.urlopen(url, timeout=45) as response:
        return json.loads(response.read().decode('utf-8'))


def save(name):
    result = request(name)
    content = base64.b64decode(result['content'])
    content.decode('utf-8')
    destination = ROOT / 'failed-gate-source' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(),
            'api': API + name + '?ref=' + REVISION}


with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(save, FILES))
listing = request('ets1.2')
entries = [{'name': item['name'], 'type': item['type']} for item in listing]
result = {'revision': REVISION, 'files': records, 'directory_entries': entries}
(ROOT / 'failed-gate-source.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=True))
