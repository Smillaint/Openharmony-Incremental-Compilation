from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).parent
REPO = Path(r'D:\workspace\Openharmony-Incremental-Compilation')
EVIDENCE = REPO / 'docs/evidence/20261020-review-replies-gates'
plan = json.loads((ROOT / 'plan.json').read_text(encoding='utf-8'))
report = json.loads((ROOT / 'receipts.json').read_text(encoding='utf-8'))
results = report['results']
assert len(results) == 8
assert all(len(x['commands']) == 1 and len(x['events']) == 1 and len(x['receipts']) == 1 for x in results)
assert all(x['head_unchanged'] and x['events'][0]['head_members_match'] for x in results)
assert all(len(r['matches']) == 1 for x in results for r in x['replies'])
assert sum(len(x['replies']) for x in results) == 8
assert sum(len(x['events'][0]['actual']) for x in results) == 14

def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')

def save(path, data):
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

EVIDENCE.mkdir(parents=True, exist_ok=True)
for source in ROOT.iterdir():
    if source.is_file() and source.suffix in {'.json', '.py', '.png'}:
        shutil.copy2(source, EVIDENCE / source.name)

replies = []
for result in results:
    for reply in result['replies']:
        expected = next(x for x in plan['replies'] if x['parent_id'] == reply['parent_id'])
        assert expected['parent']['resolved'] == reply['resolved'], 'Discussion resolution state changed'
        posted = reply['matches'][0]
        replies.append({'number': result['number'], 'parent_id': reply['parent_id'],
                        'reply_id': posted['id'], 'discussion_id': reply['discussion_id'],
                        'body': posted['body'], 'created_at': posted['created_at'],
                        'resolved': reply['resolved']})
save(EVIDENCE / 'reply-verification.json', replies)

names = {6982: 'IDL', 6999: '校验、host、parts 聚合', 7134: 'loader',
         6965: 'SA 三项', 6974: 'HAP', 7009: 'NOTICE 收集', 7048: 'NOTICE 配套', 22: 'airscan'}
rows = []
versions = []
for result, item in zip(results, plan['gates']):
    event = result['events'][0]
    pr_url = f"https://gitcode.com/openharmony/{result['repo']}/merge_requests/{result['number']}"
    issue_url = f"https://gitcode.com/openharmony/{item['issue_repo']}/issues/{item['issue']}"
    rows.append(f"| {names[result['number']]} | [{result['repo']} #{result['number']}]({pr_url}) | [#{item['issue']}]({issue_url}) | {len(item['members'])} | [门禁任务]({event['url']}) | `{event['status']}` |")
    for member in item['members']:
        versions.append(f"| [{member['repo']} #{member['url'].rsplit('/', 1)[1]}]({member['url']}) | `{member['head']}` |")

reply_rows = []
for reply in replies:
    reply_rows.append(f"| build #{reply['number']} | `{reply['parent_id']}` | `{reply['reply_id']}` | {reply['created_at']} |")

handoff = '''# 检视回复与修订版门禁（2026-10-20）

八条检视回复已按确认稿发布到 ringking0 的原评论线程：build #6982 五条、#6999 两条、#7134 一条。逐条核对正文、作者和所属 discussion，没有重复回复。讨论解决状态未改动，#7134 的该条意见此前已由 ringking0 标为已解决，其余七条保留未解决状态。

本轮给尚无最新提交完整门禁结果的八个组各发送一次 `start build`，覆盖十四条 PR。八条命令均有机器人启动回执，DCP 事件中的所有 PR、HEAD 与正式 Issue 分组完全吻合。当前均为排队状态，启动不代表静态、编译或冒烟通过。

没有修改源码、PR 正文、Issue 关联或源分支，也没有合入 PR。所有已有 DCO 提交保留。自动巡检仍为暂停状态。

## 门禁任务

查询时间：QUERY_TIME。日期采用 America/Los_Angeles，原始 GitCode 回执保留其北京时间。

| 分组 | 触发入口 | Issue | PR 数 | 实际任务 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
GATE_ROWS

IDL 六仓和 HAP 两仓各只在一个入口触发；配套 PR 没有分别重复启动。#7048 和 airscan #22 在此前快照中也没有当前 HEAD 门禁回执，因此本轮一起补跑。

安装组（build #7046、ace #7210、graphic_3d #676）已有最新提交门禁回执，停在 ace 十条术语告警，本轮未重触发。SDK split、JS/CSS、iptables 保留现有通过结果。build #7006 已于 `2026-10-19T22:03:32+08:00` 合入，未重跑。

## 本轮验证的源码版本

| PR | HEAD |
| --- | --- |
VERSION_ROWS

## 检视回复回执

八条正文见[保留的确认稿](pr-drafts/20261018-ringking0-replies.md)，原始父评论、discussion、正文及回复时间见[逐条回读证据](evidence/20261020-review-replies-gates/reply-verification.json)。

| PR | 原评论 ID | 回复 ID | 发布时间 |
| --- | --- | --- | --- |
REPLY_ROWS

原有重叠修改的合入边界继续沿用[检视整改记录](oct18-review-fixes.md)：签名模板在 #6974/#6999 一致；公共 JSON 工具在 #6965/#6999/#7009/#7046/#7134 一致；#6999 的旧 IDL 修改保留原范围。某条合入后，其余 PR 仍需对目标分支重新比较已合入的 hunk，不能直接将所有 PR 整文件互相覆盖。

## 证据与 Git 保存

- [计划与原评论](evidence/20261020-review-replies-gates/plan.json)、[命令、机器人回执和事件版本核对](evidence/20261020-review-replies-gates/receipts.json)。
- `evidence/20261020-review-replies-gates/before-*.json`、`after-*.json` 保存启动前后公开 PR 与评论快照；`gate-*.json` 保存八个 DCP 事件原文。
- [loader 回复截图](evidence/20261020-review-replies-gates/reply-7134.png)；其余页面截图与只读核对脚本放在同目录。
- 修改前归档仓标签：`backup/review-replies-gates-20261020`，指向 `3b09f1ab3afc0d2fca179800521ca0138a2b7025`。
- 归档分支：`agent/document-action-incremental-fixes`。交接提交使用 `Signed-off-by: Smillick <3185479846@qq.com>`，与修改前标签一起同步 GitHub。
- 本地操作目录：`D:/workspace/archives/20261020-review-replies-gates/`。

后续手动查看上述八个实际任务即可；没有为本轮恢复自动巡检，也没有设置失败后自动重试。
'''
handoff = handoff.replace('QUERY_TIME', report['queried_utc']).replace('GATE_ROWS', '\n'.join(rows)).replace('VERSION_ROWS', '\n'.join(versions)).replace('REPLY_ROWS', '\n'.join(reply_rows))
write(REPO / 'docs/oct20-review-replies-and-gates.md', handoff)

draft_path = REPO / 'docs/pr-drafts/20261018-ringking0-replies.md'
draft = draft_path.read_text(encoding='utf-8')
old_status = '状态：代码修订已推送，下面八条回复尚未发送，也未将讨论标为已解决。新提交均带 `Signed-off-by: Smillick <3185479846@qq.com>`。'
new_status = '状态：2026-10-20 八条回复已按下列原文发布到对应检视线程，正文及所属 discussion 均已回读核对。讨论解决状态未改动。新提交均带 `Signed-off-by: Smillick <3185479846@qq.com>`。回复 ID、门禁任务和提交版本见[发布交接](../oct20-review-replies-and-gates.md)。'
assert old_status in draft
write(draft_path, draft.replace(old_status, new_status, 1))

readme_path = REPO / 'README.md'
readme = readme_path.read_text(encoding='utf-8')
intro = '本仓库记录 OpenHarmony `rk3568/phone` 增量构建中重复 Action 的根因、代码修改、PR 与验证证据。'
update = '[2026-10-20 检视回复与修订版门禁](docs/oct20-review-replies-and-gates.md)：**8 条检视回复已发布；8 组完整门禁已各触发一次，覆盖 14 条 PR。** 所有任务的 HEAD、配套 PR 与 Issue 分组均已核对，当前排队，尚无最终通过结果。build #7006 已合入；安装组暂保留术语告警，自动巡检保持暂停。'
assert intro in readme
write(readme_path, readme.replace(intro, intro + '\n\n' + update, 1))

for rel in ['docs/oct18-review-fixes.md', 'docs/oct18-idl-encoding-compatibility.md', 'docs/oct15-companion-pr-submission.md']:
    path = REPO / rel
    source = path.read_text(encoding='utf-8')
    first, rest = source.split('\n', 1)
    followup = '\n2026-10-20 后续：[检视回复与修订版门禁](oct20-review-replies-and-gates.md)记录八条已发布回复和八组新任务；以下内容保留各自阶段的历史状态。\n'
    write(path, first + '\n' + followup + rest)

state_path = REPO / 'docs/evidence/20261015-companion-prs/monitor-state.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
assert state['automation_status'] == 'PAUSED'
now = report['queried_utc']
for result, item in zip(results, plan['gates']):
    event = result['events'][0]
    target = next((x for x in state['groups'] if x['trigger_repo'] == item['repo'] and x['trigger_number'] == item['number']), None)
    if target is None:
        target = next(x for x in state['other_existing_prs'] if x['repo'] == item['repo'] and x['number'] == item['number'])
    target['before_manual_gate_20261020'] = {k: deepcopy(v) for k,v in target.items() if k in {'status','done','head','url','active_gate','last_checked_utc','members'}}
    target.update({'status': event['status'], 'done': False, 'url': event['url'],
                   'active_gate': True, 'head_verified': True, 'gate_matches_current_heads': True,
                   'final_report_pending': True, 'last_checked_utc': now,
                   'command_id': result['commands'][0]['id'], 'receipt_id': result['receipts'][0]['id'],
                   'started_at': result['receipts'][0]['created_at'],
                   'trigger_reason': 'Manual request after approved review replies; one full gate for each pending revision group.',
                   'evidence': '../20261020-review-replies-gates/receipts.json',
                   'progress': 'One full gate accepted; exact current member heads verified. Queued, no final result.'})
    target.pop('note', None)
    target.pop('verification', None)
    for member in target.get('members', []):
        expected = next(m for m in item['members'] if m['repo'] == member['repo'] and m['url'].endswith('/'+str(member['number'])))
        assert expected['head'] == member['head']
        member.update({'status': event['status'], 'done': False, 'active_gate': True,
                       'final_report_pending': True, 'last_checked_utc': now,
                       'url': event['url'], 'codecheck_status': 'pending'})
        member.pop('result_comment_id', None)
        member.pop('passed_at', None)
    target['codecheck_status'] = 'pending'

merged_path = Path(r'D:\workspace\archives\20261020-pr-status\build-7006-pr.json')
merged = json.loads(merged_path.read_text(encoding='utf-8'))
assert merged['state'] == 'merged'
save(EVIDENCE / 'build-7006-merged.json', merged)
old7006 = next(x for x in state['other_existing_prs'] if x['repo']=='build' and x['number']==7006)
old7006.update({'status':'merged','done':True,'active_gate':False,'final_report_pending':False,
                'merged_at':merged['merged_at'],'last_checked_utc':now,
                'progress':'Full gate passed and PR merged; no new gate triggered.',
                'merge_evidence':'../20261020-review-replies-gates/build-7006-merged.json'})
state.update({'last_manual_action_utc': now,
              'manual_action_evidence': '../20261020-review-replies-gates/receipts.json',
              'last_manual_snapshot': '../20261020-review-replies-gates/receipts.json',
              'current_pr_snapshot': '../20261020-review-replies-gates/receipts.json',
              'last_checked_utc': now})
save(state_path, state)
print(json.dumps({'replies':len(replies),'gate_groups':len(results),'pr_members':14,'automation_status':state['automation_status'],'handoff':str(REPO/'docs/oct20-review-replies-and-gates.md')},ensure_ascii=True))
