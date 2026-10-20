from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import urllib.request

ROOT = Path(__file__).parent
ROOT.mkdir(parents=True, exist_ok=True)
API = 'https://api.gitcode.com/api/v5/'
previous = json.loads(Path(r'D:\workspace\archives\20261020-pr-status\summary.json').read_text(encoding='utf-8'))
heads = {(pr['repo'],pr['number']):pr['head'] for pr in previous['prs']}
targets = [('build',6982,'build',4668),('build',6999,'build',4678),
           ('build',7134,'build',4761),('build',6965,'build',4657),
           ('build',6974,'build',4663),('build',7009,'build',4684),
           ('build',7048,'build',4705),('third_party_sane-airscan',22,'third_party_sane-airscan',19)]


def get(path):
    with urllib.request.urlopen(API+path,timeout=45) as response:
        return json.loads(response.read().decode('utf-8'))


def save(name,data):
    (ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def fetch(target):
    repo,number,issue_repo,issue=target
    prefix='repos/openharmony/'+repo+'/pulls/'+str(number)
    pr=get(prefix)
    comments=get(prefix+'/comments?per_page=100&page=1')
    assert len(comments)<100,'Comment pagination needed'
    issues=get(prefix+'/issues')
    members=get('repos/openharmony/'+issue_repo+'/issues/'+str(issue)+'/pull_requests')
    assert pr['state']=='open' and pr['head']['sha']==heads[(repo,number)]
    assert any(str(x.get('number'))==str(issue) for x in issues),'Formal issue missing'
    assert 'dco\u68c0\u67e5\u6210\u529f' in [x['name'] for x in pr['labels']]
    active=[{'url':x['html_url'],'head':x['head']['sha'],'state':x['state'],
             'repo':x['base']['repo']['name'],'base_ref':x['base']['ref']} for x in members if x['state']=='open']
    assert len({(x['repo'],x['base_ref']) for x in active})==len(active),'Duplicate repository/base branch'
    save('before-'+repo+'-'+str(number)+'.json',{'pr':pr,'comments':comments,'issues':issues,'members':members})
    return {'repo':repo,'number':number,'head':pr['head']['sha'],
            'issue_repo':issue_repo,'issue':issue,'members':active,
            'latest_comment_id':max([x['id'] for x in comments],default=0)}


gates=list(ThreadPoolExecutor(max_workers=4).map(fetch,targets))
draft=Path(r'D:\workspace\Openharmony-Incremental-Compilation\docs\pr-drafts\20261018-ringking0-replies.md').read_text(encoding='utf-8')
parents=[(6982,194418948),(6982,194419266),(6982,194419155),(6982,194419161),
         (6982,194419169),(6999,194419196),(6999,194419200),(7134,194419185)]
sections=re.findall(r'## build #\d+[^\n]*\n(.*?)(?=\n## |\Z)',draft,re.S)
assert len(sections)==8
replies=[]
for (number,parent),section in zip(parents,sections):
    body='\n'.join(line[2:] for line in section.splitlines() if line.startswith('> '))
    assert body
    data=json.loads((ROOT/('before-build-'+str(number)+'.json')).read_text(encoding='utf-8'))
    comment=next(x for x in data['comments'] if x['id']==parent)
    assert comment['user']['login']=='ringking0'
    assert not any(x.get('user',{}).get('login')=='SmillySmillick' and x.get('body','').strip()==body for x in data['comments']), 'Reply already present'
    replies.append({'number':number,'parent_id':parent,'body':body,'parent':comment})
plan={'prepared_utc':datetime.now(timezone.utc).isoformat(),'replies':replies,'gates':gates}
save('plan.json',plan)
print(json.dumps({'reply_count':len(replies),'gate_count':len(gates),'gates':gates,
                  'first_parent':{k:v for k,v in replies[0]['parent'].items() if k!='body'}},ensure_ascii=True))
