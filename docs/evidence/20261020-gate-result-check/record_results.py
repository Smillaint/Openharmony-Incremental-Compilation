from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import re
import shutil

ROOT=Path(__file__).parent
REPO=Path(r'D:\workspace\Openharmony-Incremental-Compilation')
DEST=REPO/'docs/evidence/20261020-gate-result-check'
DEST.mkdir(parents=True,exist_ok=True)
snapshot=json.loads((ROOT/'summary.json').read_text(encoding='utf-8'))
events=[e for e in snapshot['events'] if e['scope']=='new_eight']
assert len(events)==8 and all(e['matches_current_heads'] and e['matches_planned_members'] for e in events)
assert all(e['status']=='close' for e in events)
assert sum(e['result']=='success' for e in events)==3
assert all(c['result']=='pass' for e in events for c in e['codecheck'])
assert all(p['head_unchanged'] for p in snapshot['prs'])

def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def final_comment(event,repo,number):
    data=json.loads((ROOT/f'{repo}-{number}.json').read_text(encoding='utf-8'))
    candidates=[c for c in data['comments'] if c.get('user',{}).get('login')=='openharmony_ci'
                and event['id'] in c['body'] and ('代码门禁通过' in c['body'] or '代码门禁未通过' in c['body'])]
    assert candidates,(repo,number)
    return candidates[-1]

records=[]
for event in events:
    final=final_comment(event,event['repo'],event['number'])
    members=[]
    for url,head in event['head_members'].items():
        pr=next(p for p in snapshot['prs'] if p['url'].rstrip('/')==url)
        receipt=final_comment(event,pr['repo'],pr['number'])
        expected='代码门禁通过' if event['result']=='success' else '代码门禁未通过'
        assert expected in receipt['body']
        members.append({'repo':pr['repo'],'number':pr['number'],'head':head,'result_comment_id':receipt['id'],
                        'result_at':receipt['created_at'],'labels':pr['labels']})
    failed_rows=[]
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>',final['body'],re.S):
        if 'failed' in row:
            failed_rows.append({'text':re.sub('<[^>]+>',' ',row).strip(),'ignored':'IGNORE' in row})
    classification='passed' if event['result']=='success' else ('failed_pipeline_timeout_and_ecotest_timeout' if event['number']==6999 else 'failed_ecotest_timeout')
    records.append({'repo':event['repo'],'number':event['number'],'id':event['id'],'url':event['url'],
                    'status':classification,'result':event['result'],'heads_match':True,'codecheck_status':'passed',
                    'result_comment_id':final['id'],'result_at':final['created_at'],
                    'members':members,'failed_rows':failed_rows})

logs=json.loads((ROOT/'failure-logs.json').read_text(encoding='utf-8'))
ecotest=[]
for log in logs:
    if log['target']!='dayu600_7885':continue
    hit=next(x for x in log['excerpts'] if 'trigger_ecotest result 200 ' in x['text'])
    task=json.loads(hit['text'].split('trigger_ecotest result 200 ',1)[1])
    assert task['status']=='Success'
    ecotest.append({'pr':log['pr'],'task_id':task['taskId'],'block_id':task['blockId'],
                    'trigger_line':hit['line'],'trigger_evidence':hit['text'],'build_log':log['url'],
                    'build_finished_success':any('Finished: SUCCESS' in x['text'] for x in log['excerpts'])})
assert len(ecotest)==5 and all(x['build_finished_success'] for x in ecotest)
diagnosis={'queried_utc':snapshot['queried_utc'],'new_groups':records,'ecotest':ecotest,
           'summary':{'passed_groups':3,'failed_groups':5,'matched_pr_members':14,'new_static_failure':False,
                      'overall_passed_open_prs':8,'merged_prs':1,'failed_open_prs':14,'running_groups':0},
           'limitations':['Five EcoTest tasks were accepted successfully but returned no test report. Device allocation, flashing and test execution details are unavailable; exact timeout cause is not confirmed.',
                          'Build #6999 dayu200_tdd completed all 357163 Ninja tasks and reported rk3568 build success at 21:20 Beijing time, but exceeded the gate timeout and later could not write results to mongo.',
                          'Build #6999 x86 precise target inspector/test/unittest.stamp has no producer. The final report explicitly marks this compile failure IGNORE; no precise/inspector change appears in the PR diff.']}
save(ROOT/'diagnosis.json',diagnosis)

# Public PR/events and filtered excerpts are suitable for the handoff. Raw logs remain local.
for source in ROOT.iterdir():
    if source.suffix in {'.json','.py'} and source.is_file(): shutil.copy2(source,DEST/source.name)

local_time=datetime.fromisoformat(snapshot['queried_utc']).astimezone(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M %Z')
names={6982:'IDL 六仓',6999:'校验、host、parts',7134:'loader',6965:'SA 三项',6974:'HAP 两仓',7009:'NOTICE 收集',7048:'NOTICE 配套',22:'airscan'}
rows=[]
for record in records:
    number=record['number']; label=f"{record['repo']} #{number}"
    pr_url=f"https://gitcode.com/openharmony/{record['repo']}/merge_requests/{number}"
    reason='通过' if record['result']=='success' else ('dayu600 冒烟超时；dayu200_tdd 流水线超时' if number==6999 else 'dayu600 冒烟超时')
    rows.append(f"| {names[number]} | [{label}]({pr_url}) | 通过 | {reason} | [任务]({record['url']}) |")
task_rows=[]
for t in ecotest:
    task_rows.append(f"| #{t['pr']} | `{t['task_id']}` | 空 | 成功 | [构建日志]({t['build_log']}) |")

doc=f'''# 修订版门禁结果复核（2026-10-20）

查询时间：{local_time}（`{snapshot['queried_utc']}`）。八组最新修订门禁全部结束，三组通过、五组失败。十四条组内 PR 的当前 HEAD 与事件实测 HEAD 一致，十四条 DCO 和静态检查均通过；没有新的静态告警。

本轮只查询门禁、评论和公开构建日志，未修改源码、回复检视、合入或重触发任务。自动巡检继续暂停。

## 八组实际结果

| 分组 | PR 入口 | 静态 | 最终结果 / 阻断项 | 门禁 |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

通过组的 `master_inner_build`、`ohos-sdk-codearts-new` 等失败行均由最终回执明确标注 `IGNORE`，没有把这些行误计成阻断故障。五个失败组则都有未忽略的 `dayu600_7885` 测试超时。

## dayu600 的五次超时

五组编译、打包、上传均成功，公开日志末尾为 `Finished: SUCCESS`。EcoTest 接口均返回 HTTP 200、`status=Success`，取得了真实任务 ID；随后门禁以 `ecotest timeout` 结束，没有测试报告、用例断言或失败堆栈。

| 触发 PR | EcoTest 任务 | blockId | 构建阶段 | 日志 |
| --- | --- | --- | --- | --- |
{chr(10).join(task_rows)}

现有证据定位到测试服务执行/回报超时，不能进一步认定是设备分配、刷机、用例执行还是回报链路，也不能仅凭超时认定源码绝对无关。下一步应由 EcoTest 平台根据上述任务 ID 查询 `L2_P7885_DOOR` 的设备、刷机和执行记录；没有据此修改增量构建脚本或自动重试。

## #6999 的额外失败

`dayu200_tdd` 在日志中完成 `357163/357163` 个 Ninja 任务，随后于北京时间 `2026-10-20 21:20:14` 显示 `rk3568 build success`，主构建耗时 `13242.84 s`。DCP 于 `21:27:09` 将流水线判为 `pipeline running timeout`。产物约 15.97 GB，后续 `21:38:13` 上传成功，但 `21:38:19` 回写结果报 `currentStatus error, can not upload result to mongo`，最终退出失败。

因此本次不是编译器报错导致该项失败：编译完成后还需要打包、上传，整个任务超过平台时限；回写错误发生在其后。运行缓慢的进一步资源原因没有从日志确认。[日志尾部精确证据](evidence/20261020-gate-result-check/6999-dayu200_tdd-final-signals.json)。

此外 `x86_64_virt_tdd` 的首个真实错误是：

```text
ninja: error: 'clang_x64/obj/arkcompiler/toolchain/inspector/test/unittest.stamp', needed by 'precise', missing and no known rule to make it
```

该项在最终回执被明确标为 `failed(IGNORE)(compile failed)`，不是本组阻断项。#6999 的实际二十个修改文件没有 precise 或 inspector 规则改动，当前按精确构建目标图兼容问题记录；没有凭缺目标错误扩大增量修复范围。[首错片段](evidence/20261020-gate-result-check/6999-x86-first-error.json)、[实际 PR diff](evidence/20261020-gate-result-check/build-6999-files.json)。

## 其余 PR 和检视

本次回读全部二十三条相关 PR：八条开放 PR 有当前提交的完整门禁通过记录；十四条开放 PR 被本轮超时或既有安装组静态告警阻断；build #7006 已合入。没有运行中的组，也没有 HEAD 变化。

- SDK split（build #7049、interface_sdk-js #36540）、JS/CSS（jsframework #853、css-what #29）、iptables #62 继续通过。
- 安装组（build #7046、ace #7210、graphic_3d #676）状态未变化，ace 仍为十条术语告警，未重新触发。
- 本轮新通过且审查人列表包含 ringking0 的 PR：[loader #7134](https://gitcode.com/openharmony/build/merge_requests/7134)、[NOTICE #7009](https://gitcode.com/openharmony/build/merge_requests/7009)、[NOTICE 配套 #7048](https://gitcode.com/openharmony/build/merge_requests/7048)。当前三条的 ringking0 `accept=false`，门禁通过不代表检视批准。#7134 先前批准在源码修订后已重置。

## 证据与保存

[逐组诊断与最终回执 ID](evidence/20261020-gate-result-check/diagnosis.json)、[公开 API 原始快照](evidence/20261020-gate-result-check/summary.json)以及同目录 `gate-*.json`、逐 PR JSON、过滤后的日志片段保留查询时状态。所有十四条 PR 的最终回执均已逐条核对，不仅依据标签判断。

原始日志和分段尾部仅保存在 `D:/workspace/archives/20261020-gate-check-034956Z/`，没有把完整环境输出放入归档仓。检查前 Git 标签为 `backup/gate-result-check-20261020`，指向 `d9a2e484af204003708c51cec1cae40309c61605`。归档提交保留 Smillick DCO，并同步既有 GitHub 分支。
'''
(REPO/'docs/oct20-gate-results.md').write_text(doc,encoding='utf-8',newline='\n')

readme=REPO/'README.md'
text=readme.read_text(encoding='utf-8')
intro='本仓库记录 OpenHarmony `rk3568/phone` 增量构建中重复 Action 的根因、代码修改、PR 与验证证据。'
new='[2026-10-20 修订版门禁结果](docs/oct20-gate-results.md)：**新跑八组中，loader #7134、NOTICE #7009、#7048 通过，其余五组被 dayu600 冒烟超时阻断；十四条静态均通过。** #6999 另有 dayu200_tdd 全部编译完成后的流水线超时及结果回写失败。二十三条 PR 的当前提交已回读，无新源码修改或自动重试；自动巡检保持暂停。'
assert intro in text
readme.write_text(text.replace(intro,intro+'\n\n'+new,1),encoding='utf-8',newline='\n')
handoff=REPO/'docs/oct20-review-replies-and-gates.md'
text=handoff.read_text(encoding='utf-8')
first,rest=text.split('\n',1)
handoff.write_text(first+'\n\n后续[门禁结果复核](oct20-gate-results.md)：八组已结束，三组通过、五组失败；以下保留启动时的排队快照。\n'+rest,encoding='utf-8',newline='\n')

state_path=REPO/'docs/evidence/20261015-companion-prs/monitor-state.json'
state=json.loads(state_path.read_text(encoding='utf-8'))
assert state['automation_status']=='PAUSED'
for record in records:
    target=next((g for g in state['groups'] if g['trigger_repo']==record['repo'] and g['trigger_number']==record['number']),None)
    if target is None:target=next(p for p in state['other_existing_prs'] if p['repo']==record['repo'] and p['number']==record['number'])
    target['gate_start_snapshot_20261020']={k:deepcopy(v) for k,v in target.items() if k in {'status','done','active_gate','last_checked_utc','final_report_pending'}}
    passed=record['result']=='success'
    target.update({'status':record['status'],'done':passed,'active_gate':False,'final_report_pending':False,
                   'gate_matches_current_heads':True,'head_verified':True,'last_checked_utc':snapshot['queried_utc'],
                   'result_comment_id':record['result_comment_id'],'result_at':record['result_at'],
                   'codecheck_status':'passed','result_evidence':'../20261020-gate-result-check/diagnosis.json',
                   'progress':'Current HEAD final gate passed.' if passed else 'Final gate blocked by EcoTest timeout; #6999 also has a pipeline timeout after compilation success. No automatic retry.'})
    if passed:target['passed_at']=record['result_at']
    else:
        target['failure']={'classification':record['status'],'stage':'EcoTest' if record['number']!=6999 else 'EcoTest and pipeline duration limit/result reporting',
                           'evidence':'../20261020-gate-result-check/diagnosis.json',
                           'details':'Current static checks passed; final receipts confirm timeouts. Exact device/test timeout cause remains unconfirmed.'}
    for member in target.get('members',[]):
        matched=next(m for m in record['members'] if m['repo']==member['repo'] and m['number']==member['number'])
        member.update({'status':record['status'],'done':passed,'active_gate':False,'final_report_pending':False,
                       'last_checked_utc':snapshot['queried_utc'],'result_comment_id':matched['result_comment_id'],
                       'result_at':matched['result_at'],'codecheck_status':'passed'})
        if passed:member['passed_at']=matched['result_at']
state.update({'last_checked_utc':snapshot['queried_utc'],'last_manual_snapshot':'../20261020-gate-result-check/summary.json',
              'current_pr_snapshot':'../20261020-gate-result-check/summary.json'})
save(state_path,state)
print(json.dumps({'groups':len(records),'passed':3,'failed':5,'ecotest_tasks':[t['task_id'] for t in ecotest],
                  'local_query_time':local_time,'automation':state['automation_status']},ensure_ascii=True))
