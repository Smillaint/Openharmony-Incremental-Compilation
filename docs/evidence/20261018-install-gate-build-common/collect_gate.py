from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import urllib.request

ROOT = Path(__file__).parent
API = 'https://api.gitcode.com/api/v5/repos/openharmony/'
MEMBERS = [('developtools_ace_ets2bundle', 7210), ('build', 7046), ('graphic_graphic_3d', 676)]


def get(url):
    with urllib.request.urlopen(url, timeout=45) as response:
        return json.loads(response.read().decode('utf-8'))


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                            encoding='utf-8', newline='\n')


def fetch(member):
    repo, number = member
    comments = get(API + repo + '/pulls/' + str(number) + '/comments?per_page=100&page=1')
    save('after-' + repo + '-comments.json', comments)
    return member, comments


comments_by_member = dict(ThreadPoolExecutor(max_workers=3).map(fetch, MEMBERS))
before = json.loads((ROOT / 'before-ace-comments.json').read_text(encoding='utf-8'))
old_ids = {comment['id'] for comment in before}
new = [comment for comment in comments_by_member[MEMBERS[0]] if comment['id'] not in old_ids]
commands = [comment for comment in new if comment.get('user', {}).get('login') == 'SmillySmillick'
            and comment.get('body', '').strip() == 'start build']
assert len(commands) == 1 and commands[0]['id'] == 194464499
receipts = [comment for comment in new if comment.get('user', {}).get('login') == 'openharmony_ci'
            and '\u95e8\u7981\u6784\u5efa\u5f00\u59cb' in comment.get('body', '')]
record = {'checked_utc': datetime.now(timezone.utc).isoformat(),
          'trigger_repo': MEMBERS[0][0], 'trigger_number': MEMBERS[0][1],
          'command_id': commands[0]['id'], 'command_created_at': commands[0]['created_at'],
          'commands_submitted': 1, 'issue': 'https://gitcode.com/openharmony/build/issues/4704',
          'status': 'command_submitted_waiting_receipt', 'automation_status': 'PAUSED',
          'review_reply_posted': False, 'new_bot_comments': [comment for comment in new
              if comment.get('user', {}).get('login') == 'openharmony_ci']}
if receipts:
    assert len(receipts) == 1
    receipt = receipts[0]
    ids = set(re.findall(r'dcp\.openharmony\.cn/workbench/cicd/detail/([a-f0-9]+)/runlist', receipt['body']))
    assert len(ids) == 1
    gate_id = ids.pop()
    event = get('https://dcp.openharmony.cn/api/codecheckAccess/ci-portal/v1/event/' + gate_id)
    save('event.json', event)
    expected = {('developtools_ace_ets2bundle', 7210): '92f3fe9598c24f6118774101968176b20fc7b342',
                ('build', 7046): 'a82a8a03bd3a43c23c186d4ed32cd2602c010c93',
                ('graphic_graphic_3d', 676): '57e960e087a2f0aefbcc5f21b0f88b6cefc354f0'}
    actual = {(item['repoName'], int(item['url'].rsplit('/', 1)[-1])): item['headCommitId']
              for item in event['data']['prMsg']}
    assert actual == expected, 'Gate membership or HEAD changed'
    record.update(status='started', gate_id=gate_id,
                  url='https://dcp.openharmony.cn/workbench/cicd/detail/' + gate_id + '/runlist',
                  receipt_id=receipt['id'], receipt_created_at=receipt['created_at'],
                  gate_current_status=event['data']['currentStatus'],
                  members=[{'repo': repo, 'number': number, 'head': head}
                           for (repo, number), head in actual.items()])
save('gate-receipt.json', record)
print(json.dumps({key: value for key, value in record.items() if key != 'new_bot_comments'}, ensure_ascii=True))
