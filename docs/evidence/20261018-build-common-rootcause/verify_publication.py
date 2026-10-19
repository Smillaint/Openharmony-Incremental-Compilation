from pathlib import Path
from datetime import datetime, timezone
import json
import urllib.request

ROOT = Path(__file__).parent
plan = json.loads((ROOT / 'publication.json').read_text(encoding='utf-8'))
api = 'https://api.gitcode.com/api/v5/repos/openharmony/developtools_ace_ets2bundle/'


def get(path):
    with urllib.request.urlopen(api + path, timeout=45) as response:
        return json.loads(response.read().decode('utf-8'))


pr = get('pulls/7210')
commit = get('commits/' + plan['after'])
original = json.loads((ROOT / 'before-pr7210.json').read_text(encoding='utf-8'))
assert pr['state'] == 'open' and pr['head']['sha'] == plan['after']
assert pr['body'] == original['body'] and pr['title'] == original['title']
message = commit['commit']['message']
assert 'Signed-off-by: Smillick <3185479846@qq.com>' in message
record = {'checked_utc': datetime.now(timezone.utc).isoformat(),
          'pr': pr['html_url'], 'state': pr['state'], 'head': pr['head']['sha'],
          'before': plan['before'], 'dco_signed': True, 'title_unchanged': True,
          'body_unchanged': True, 'labels': pr['labels'],
          'gate_triggered_by_this_work': False, 'review_reply_posted': False}
(ROOT / 'post-publication-pr7210.json').write_text(json.dumps(pr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(ROOT / 'publication-verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=True))
