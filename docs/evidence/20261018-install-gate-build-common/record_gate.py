from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).parent
MAIN = Path(r'D:\workspace\Openharmony-Incremental-Compilation')
DEST = MAIN / 'docs/evidence/20261018-install-gate-build-common'
record = json.loads((ROOT / 'gate-receipt.json').read_text(encoding='utf-8'))
assert record['status'] == 'started' and record['commands_submitted'] == 1
assert record['gate_current_status'] == 'pending'
changed = subprocess.check_output(['git','-C',str(MAIN),'diff','--name-only']).decode('utf-8').splitlines()
assert changed in [[], ['README.md']], 'Unexpected handoff changes before recording'
subprocess.run(['git','-C',str(MAIN),'tag','backup/install-gate-build-common-20261018'],check=True)
DEST.mkdir(parents=True, exist_ok=True)
for source in ROOT.iterdir():
    if source.is_file():
        if source.suffix != '.png':
            source.read_bytes().decode('utf-8')
        shutil.copyfile(source, DEST / source.name)

state_path = MAIN / 'docs/evidence/20261015-companion-prs/monitor-state.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
assert state['automation_status'] == 'PAUSED'
expected = {(m['repo'], m['number']): m['head'] for m in record['members']}
group = next(item for item in state['groups'] if item['name'] == 'Install')
group['previous_gate_before_20261018_dependency_fix'] = {
    key: value for key, value in group.items() if key not in ['members', 'previous_gate_before_20261018_dependency_fix']}
group.update(status='started', done=False, url=record['url'], active_gate=True,
             gate_matches_current_heads=True, final_report_pending=True, codecheck_status='pending',
             command_id=record['command_id'], receipt_id=record['receipt_id'],
             last_checked_utc=record['checked_utc'], head_verified=True,
             progress='Latest three HEADs verified in gate; pending. One start build command submitted.',
             current_gate_evidence='../20261018-install-gate-build-common/gate-receipt.json')
for member in group['members']:
    assert member['head'] == expected[(member['repo'], member['number'])]
    member.update(status='pending', done=False, active_gate=True,
                  codecheck_status='pending', final_report_pending=True,
                  last_checked_utc=record['checked_utc'], url=record['url'])
state['last_manual_action_utc'] = record['checked_utc']
state['manual_action_evidence'] = '../20261018-install-gate-build-common/gate-receipt.json'
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')

doc = MAIN / 'docs/oct18-build-common-dependency.md'
text = doc.read_text(encoding='utf-8')
text += '\n## 修复后的一次门禁触发\n\n'
text += ('2026-10-18 追加触发安装组一次门禁，命令评论 `194464499`，机器人开始回执 `194464617`。'
         '回执时间为北京时间 2026-10-19 12:04:05。任务为 [' + record['gate_id'] + '](' + record['url'] + ')。\n\n')
text += '任务成员与实际 HEAD 已从门禁接口回读核对：\n\n'
text += '| PR | HEAD |\n| --- | --- |\n'
for member in record['members']:
    text += '| ' + member['repo'] + ' #' + str(member['number']) + ' | `' + member['head'] + '` |\n'
text += ('\n受理时状态为 pending，仅表示门禁已启动并等待调度，静态检查、编译和测试均未确认通过。'
         '#7006 不在本次联合任务中。自动巡检保持暂停，检视回复未发送。\n')
doc.write_text(text, encoding='utf-8', newline='\n')
print('Recorded one started gate and three current HEADs; automation remains paused.')
