from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess

ROOT = Path(__file__).parent
MAIN = Path(r'D:\workspace\Openharmony-Incremental-Compilation')
DEST = MAIN / 'docs/evidence/20261018-install-gate-followup'
assert not subprocess.check_output(['git','-C',str(MAIN),'status','--porcelain']).strip()
subprocess.run(['git','-C',str(MAIN),'tag','backup/install-gate-followup-20261018'],check=True)
DEST.mkdir(parents=True,exist_ok=True)
for source in ROOT.rglob('*'):
    if not source.is_file() or '__pycache__' in source.parts or source.name == 'hisysevent-success-build.log.zip':
        continue
    if source.suffix != '.png':
        source.read_bytes().decode('utf-8')
    target = DEST / source.relative_to(ROOT)
    assert target.resolve().is_relative_to(DEST.resolve())
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)

event = json.loads((ROOT/'event.json').read_text(encoding='utf-8'))['data']
passed = json.loads((ROOT/'pass-verification.json').read_text(encoding='utf-8'))
names = json.loads((ROOT/'filename-verification.json').read_text(encoding='utf-8'))
now = datetime.now(timezone.utc).isoformat()
summary = {'checked_utc':now,'installation_gate':event['id'],'installation_result':event['result'],
    'ace_head':names['head'],'ace_codecheck':'failed_words_only','alert_count':10,
    'alert_rule':'WordsTool.110 Intent','source_files_match_actual_gate_base':True,
    'gn_input_output_entries_retained':True,'build_and_graphic_codecheck':'passed',
    'installation_compile_started':False,'source_changed':False,
    'gate_triggered':False,'review_reply_posted':False,'automation_status':'PAUSED',
    'hisysevent_retry_gate':passed['hisysevent_pass_gate'],'hisysevent_result':'passed',
    'hisysevent_retry_trigger_user':'ohci1','sdk_split_gate':passed['sdk_split_gate'],'sdk_split_result':'passed',
    'actual_previous_sdk_missing_dependency_root_cause':'unconfirmed; same source revisions reran successfully without ACE #7210'}
(DEST/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
state_path = MAIN/'docs/evidence/20261015-companion-prs/monitor-state.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
assert state['automation_status']=='PAUSED'
for group in state['groups']:
    if group['name']=='Install':
        assert group['url'].endswith(event['id']+'/runlist')
        group.update(status='failed_static_check',done=False,active_gate=False,final_report_pending=False,
            codecheck_status='failed_ace_words_only',last_checked_utc=now,
            progress='Gate ended at static checks: ACE has ten existing filename terminology alerts; build and graphic CodeCheck passed. Compilation not started.',
            result_evidence='../20261018-install-gate-followup/summary.json')
        for member in group['members']:
            is_ace=member['number']==7210
            member.update(status='failed_static_check' if is_ace else 'blocked_by_group_static_failure',
                codecheck_status='failed_words_only' if is_ace else 'passed',active_gate=False,
                final_report_pending=False,done=False,last_checked_utc=now)
    elif group['name']=='SDK-split':
        for member in group['members']:
            assert member['head']==passed['sdk_split_heads'][member['repo']]
            member.update(status='passed',done=True,active_gate=False,final_report_pending=False,
                codecheck_status='passed',last_checked_utc=now,
                result_evidence='../20261018-install-gate-followup/sdk-event.json')
        group.update(status='passed',done=True,active_gate=False,final_report_pending=False,
            codecheck_status='passed',last_checked_utc=now,head_verified=True,gate_matches_current_heads=True,
            url='https://dcp.openharmony.cn/workbench/cicd/detail/'+passed['sdk_split_gate']+'/runlist',
            progress='Current SDK split HEADs passed the full gate; exact event and PR heads verified.',
            result_evidence='../20261018-install-gate-followup/sdk-event.json')
for member in state['other_existing_prs']:
    if member['repo']=='build' and member['number']==7006:
        assert member['head']==passed['hisysevent_head']
        member['previous_failed_gate']={key:value for key,value in member.items()
            if key not in ['previous_gate','previous_failed_gate']}
        member.pop('failure',None)
        member.update(status='passed',done=True,active_gate=False,final_report_pending=False,
            codecheck_status='passed',last_checked_utc=now,
            url='https://dcp.openharmony.cn/workbench/cicd/detail/'+passed['hisysevent_pass_gate']+'/runlist',
            result_comment_id=194455074,passed_at='2026-10-19T11:31:58+08:00',
            progress='ohci1 retried failed builds and the gate passed. Build and ACE revisions match the earlier failed SDK; no ACE #7210 patch was applied.',
            result_evidence='../20261018-install-gate-followup/pass-verification.json')
state['last_manual_snapshot']='../20261018-install-gate-followup/summary.json'
state['current_pr_snapshot']='../20261018-install-gate-followup/current-pr-summary.json'
state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
attributes=MAIN/'.gitattributes'
content=attributes.read_text(encoding='utf-8')
line='docs/evidence/20261018-install-gate-followup/hisysevent-success-manifest.xml -text -whitespace'
if line not in content.splitlines():
    attributes.write_text(content+line+'\n',encoding='utf-8',newline='\n')
print('Recorded static block, SDK split pass, and HiSysEvent retry pass; source and gates unchanged.')
