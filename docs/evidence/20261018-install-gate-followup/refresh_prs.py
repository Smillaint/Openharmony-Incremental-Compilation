from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import urllib.request

ROOT = Path(__file__).parent
state = json.loads(Path(r'D:\workspace\Openharmony-Incremental-Compilation\docs\evidence\20261015-companion-prs\monitor-state.json').read_text(encoding='utf-8'))
members = [member for group in state['groups'] for member in group['members']]
members += state['other_existing_prs']
members = {(member['repo'], member['number']): member for member in members}


def fetch(item):
    (repo, number), previous = item
    url = 'https://api.gitcode.com/api/v5/repos/openharmony/' + repo + '/pulls/' + str(number)
    with urllib.request.urlopen(url, timeout=45) as response:
        pr = json.loads(response.read().decode('utf-8'))
    destination = ROOT / 'prs' / (repo + '-' + str(number) + '.json')
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(pr, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    return {'repo': repo, 'number': number, 'state': pr['state'], 'merged': pr.get('merged'),
            'merged_at': pr.get('merged_at'), 'head': pr['head']['sha'],
            'head_unchanged': pr['head']['sha'] == previous['head'],
            'labels': [label['name'] for label in pr.get('labels', [])]}


results = list(ThreadPoolExecutor(max_workers=4).map(fetch, members.items()))
record = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'prs': results}
(ROOT / 'current-pr-summary.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(record, ensure_ascii=True))
