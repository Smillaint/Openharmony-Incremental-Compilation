from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import urllib.request

ROOT = Path(__file__).parent
plan = json.loads((ROOT / 'plan.json').read_text(encoding='utf-8'))

def get(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        return json.loads(response.read().decode('utf-8'))

def save(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def fetch(item):
    repo, number = item['repo'], item['number']
    prefix = f'https://api.gitcode.com/api/v5/repos/openharmony/{repo}/pulls/{number}'
    comments = get(prefix + '/comments?per_page=100&page=1')
    assert len(comments) < 100
    pr = get(prefix)
    save(f'after-{repo}-{number}.json', {'pr': pr, 'comments': comments})
    replies = []
    for expected in plan['replies']:
        if repo != 'build' or number != expected['number']:
            continue
        parent = next(x for x in comments if x['id'] == expected['parent_id'])
        found = [x for x in parent.get('reply', []) if x.get('user', {}).get('login') == 'SmillySmillick' and x['body'].strip() == expected['body']]
        replies.append({'parent_id': parent['id'], 'discussion_id': parent['discussion_id'], 'resolved': parent.get('resolved'), 'matches': found})
    new = [x for x in comments if x['id'] > item['latest_comment_id']]
    commands = [x for x in new if x.get('user', {}).get('login') == 'SmillySmillick' and x['body'].strip() == 'start build']
    receipts = [x for x in new if x.get('user', {}).get('login') == 'openharmony_ci' and '门禁构建开始' in x.get('body', '')]
    events = []
    for receipt in receipts:
        for gate_id in set(re.findall(r'dcp\.openharmony\.cn/workbench/cicd/detail/([a-f0-9]+)/runlist', receipt['body'])):
            event = get('https://dcp.openharmony.cn/api/codecheckAccess/ci-portal/v1/event/' + gate_id)
            save('gate-' + gate_id + '.json', event)
            data = event.get('data') or {}
            actual = {x['url'].rstrip('/'): x['headCommitId'] for x in data.get('prMsg', [])}
            expected = {x['url'].rstrip('/'): x['head'] for x in item['members']}
            events.append({'id': gate_id, 'url': 'https://dcp.openharmony.cn/workbench/cicd/detail/' + gate_id + '/runlist', 'status': data.get('currentStatus'), 'result': data.get('result'), 'head_members_match': actual == expected, 'actual': actual, 'comment_url': data.get('commentUrl')})
    return {'repo': repo, 'number': number, 'head': pr['head']['sha'], 'head_unchanged': pr['head']['sha'] == item['head'], 'state': pr['state'], 'replies': replies, 'commands': commands, 'receipts': receipts, 'events': events, 'other_new_comments': [x for x in new if x not in commands and x not in receipts]}

results = list(ThreadPoolExecutor(max_workers=4).map(fetch, plan['gates']))
report = {'queried_utc': datetime.now(timezone.utc).isoformat(), 'results': results}
save('receipts.json', report)
print(json.dumps([{'pr': x['repo'] + '#' + str(x['number']), 'replies': [len(r['matches']) for r in x['replies']], 'commands': len(x['commands']), 'events': x['events'], 'other_new': [c['body'][:160] for c in x['other_new_comments']]} for x in results], ensure_ascii=True))
