from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).parent
MAIN = Path(r'D:\workspace\Openharmony-Incremental-Compilation')
DEST = MAIN / 'docs/evidence/20261018-build-common-rootcause'
DEST.mkdir(parents=True, exist_ok=True)
verification = json.loads((ROOT / 'publication-verification.json').read_text(encoding='utf-8'))
published = json.loads((ROOT / 'publication.json').read_text(encoding='utf-8'))
assert verification['head'] == published['after']
plan = json.loads((ROOT / 'plan.json').read_text(encoding='utf-8'))
plan['published'] = True
(ROOT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

for source in ROOT.rglob('*'):
    if not source.is_file() or '__pycache__' in source.parts:
        continue
    relative = source.relative_to(ROOT)
    target = DEST / relative
    assert target.resolve().is_relative_to(DEST.resolve())
    if source.suffix not in ['.gz', '.bundle']:
        source.read_bytes().decode('utf-8')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)

now = datetime.now(timezone.utc).isoformat()
diagnosis = {
    'checked_utc': now, 'build_pr': 7006,
    'build_head': '3dc5695a126e2c9b3de9336ad8a290d2b66c8d29',
    'failed_gate': 'https://dcp.openharmony.cn/workbench/cicd/detail/6ad576e764650f998bfeab08/runlist',
    'ace_revision_in_failed_manifest': '9e0f9e58a243d7aeab672c317a2322dc37efd1a7',
    'npm_install_step_skipped': False, 'build_pr_changes_npm_configuration': False,
    'reproduced_mechanism': 'npm6 retains an older local-package dependency graph in the root lockfile; install returns 0 but build-common is absent',
    'fixture_is_actual_ci_lockfile': False,
    'failed_worker_node_modules_obtained': False,
    'actual_ci_root_cause': 'unconfirmed; pipeline resource unavailable',
    'fixed_source_pr': verification['pr'], 'fixed_source_head': verification['head'],
    'dco_signed': True, 'exact_gate_source_stale_lock_reproduction': True,
    'fixed_stale_lock_compile_exit': 0, 'fixed_no_lock_compile_exit': 0,
    'full_sdk_build_run': False, 'gate_manually_triggered': False,
    'review_reply_posted': False, 'automation_status': 'PAUSED',
    'group_boundary': 'ACE #7210 uses build Issue #4704; build #7006 uses Issue #4682. Standalone #7006 will not automatically apply unmerged ACE #7210.'}
(DEST / 'diagnosis.json').write_text(json.dumps(diagnosis, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

state_path = MAIN / 'docs/evidence/20261015-companion-prs/monitor-state.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
assert state['automation_status'] == 'PAUSED'
for group in state['groups']:
    for member in group.get('members', []):
        if member.get('repo') == 'developtools_ace_ets2bundle' and member.get('number') == 7210:
            assert member['head'] == published['before']
            member['previous_revision'] = dict(member)
            member.update(head=published['after'], previous_head=published['before'],
                          status='not_triggered_current_head', codecheck_status='not_run_current_head',
                          done=False, active_gate=False, final_report_pending=False,
                          last_checked_utc=verification['checked_utc'],
                          source_update_evidence='../20261018-build-common-rootcause/publication-verification.json')
            member.pop('result_comment_id', None)
            member.pop('result_at', None)
            group['status'] = 'not_triggered_current_heads'
            group['done'] = False
for member in state['other_existing_prs']:
    if member.get('repo') == 'build' and member.get('number') == 7006:
        assert member['head'] == diagnosis['build_head']
        member['failure']['dependency_reproduction_evidence'] = '../20261018-build-common-rootcause/diagnosis.json'
        member['progress'] = 'An npm6 stale-lock mechanism was reproduced against the exact ACE source in the failed manifest and fixed in ACE #7210. Actual CI lockfile and links remain unavailable; #7006 unchanged, no gate retry.'
state['build_common_dependency_evidence'] = '../20261018-build-common-rootcause/diagnosis.json'
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

attributes = MAIN / '.gitattributes'
content = attributes.read_text(encoding='utf-8')
for pattern in ['docs/evidence/20261018-build-common-rootcause/**/*.log -text -whitespace',
                'docs/evidence/20261018-build-common-rootcause/*.log -text -whitespace',
                'docs/evidence/20261018-build-common-rootcause/*.patch -text -whitespace',
                'docs/evidence/20261018-build-common-rootcause/failed-gate-source/** -text -whitespace',
                'docs/evidence/20261018-build-common-rootcause/before/** -text -whitespace',
                'docs/evidence/20261018-build-common-rootcause/*.gz binary',
                'docs/evidence/20261018-build-common-rootcause/*.bundle binary']:
    if pattern not in content.splitlines():
        content += pattern + '\n'
attributes.write_text(content, encoding='utf-8')
digests = {str(path.relative_to(DEST)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
           for path in sorted(DEST.rglob('*')) if path.is_file() and path.name != 'artifact-sha256.json'}
(DEST / 'artifact-sha256.json').write_text(json.dumps(digests, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Archived', len(digests), 'files; monitor keeps #7006 failed and marks #7210 new head not triggered.')
