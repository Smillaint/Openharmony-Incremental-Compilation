from pathlib import Path
import ast, json, os, subprocess

ROOT=Path(__file__).parent
REPOS=Path(r'D:\workspace\repositories\pr-maintenance-20261015')
ARCH=Path(r'D:\workspace\Openharmony-Incremental-Compilation\patches\20261013-source-handoff')
STATE=json.loads((ROOT/'state.json').read_text(encoding='utf-8'))['results']
COMP=json.loads((ROOT/'comparison.json').read_text(encoding='utf-8'))
ENV={**os.environ,'GIT_AUTHOR_NAME':'Smillick','GIT_AUTHOR_EMAIL':'3185479846@qq.com','GIT_COMMITTER_NAME':'Smillick','GIT_COMMITTER_EMAIL':'3185479846@qq.com'}
SUBJECTS={6982:'Refresh IDL output tracking and clean recovery',7046:'Complete install output stability and rule dependencies',853:'Move JS builds into out and declare CSS inputs',22:'Update generated airscan sources for current upstream patches'}

def run(repo,*args,data=None,env=None):
    p=subprocess.run(['git','-C',str(repo),*args],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env or ENV)
    if p.returncode: raise RuntimeError(p.stderr.decode('utf-8','replace')+p.stdout.decode('utf-8','replace'))
    return p.stdout

def text(repo,*args,**kwargs):return run(repo,*args,**kwargs).decode('utf-8','strict').strip()

updates=[]
for c in COMP:
    n=c['number'];name=c['repo']
    if n not in SUBJECTS:continue
    repo=REPOS/name
    tree=c['desired_tree']
    files=c['files'][:]
    if n==7046:
        index=ROOT/'install-complete.index'
        env={**ENV,'GIT_INDEX_FILE':str(index)}
        run(repo,'read-tree',tree,env=env)
        helper=run(repo,'diff','--binary','--full-index',c['source_base'],'archive/validated','--','scripts/util/file_utils.py')
        run(repo,'apply','--cached','--3way','-',data=helper,env=env)
        # Add only the two install-rule input lines, keeping unrelated BUILD.gn changes out.
        gn=run(repo,'show',tree+':ohos/packages/BUILD.gn').decode('utf-8','strict')
        needle='''      _merged_sa_profile_zipfile,
      _system_install_info_file,
'''
        if gn.count(needle)!=1:raise RuntimeError('Install input anchor is not unique')
        gn=gn.replace(needle,needle+'''      "//build/system_arm64e_whitelist.json",
      "//build/ohos/packages/rules/categorized-libraries.json",
''')
        blob=text(repo,'hash-object','-w','--stdin',data=gn.encode('utf-8'))
        run(repo,'update-index','--add','--cacheinfo',f'100644,{blob},ohos/packages/BUILD.gn',env=env)
        tree=text(repo,'write-tree',env=env)
        files+=['ohos/packages/BUILD.gn','scripts/util/file_utils.py']
    pr=next(x for x in STATE if x['repo']==name and x['number']==n)
    old=pr['pr']['head']['sha'];upstream=text(repo,'rev-parse','upstream/master')
    changed=text(repo,'diff','--name-only',upstream,tree).splitlines()
    if sorted(changed)!=sorted(files):raise RuntimeError(f'Unexpected files in {name} #{n}: {changed}')
    for path in files:
        content=run(repo,'show',tree+':'+path)
        decoded=content.decode('utf-8','strict')
        if path.endswith('.py'):ast.parse(decoded,filename=path)
        if any(line.startswith(('<<<<<<<','=======','>>>>>>>')) for line in decoded.splitlines()):raise RuntimeError('Conflict marker '+path)
    run(repo,'diff','--check',upstream,tree)
    message=SUBJECTS[n]+'\n\nRefresh the existing PR with the preserved incremental-build repairs while retaining current upstream changes.\n\nSigned-off-by: Smillick <3185479846@qq.com>\n'
    commit=text(repo,'commit-tree',tree,'-p',old,'-p',upstream,data=message.encode('utf-8'))
    branch=f'fix/pr-{n}-refresh-20261015'
    run(repo,'update-ref',f'refs/heads/{branch}',commit)
    run(repo,'merge-base','--is-ancestor',old,commit)
    patch=run(repo,'diff','--binary','--full-index',upstream,commit)
    (ROOT/f'{name}-{n}-updated.patch').write_bytes(patch)
    run(repo,'bundle','create',str(ROOT/f'{name}-{n}-updated.bundle'),f'refs/heads/{branch}',f'^refs/heads/before/pr-{n}-20261015',f'^refs/remotes/upstream/master')
    entry={'repo':name,'number':n,'url':pr['pr']['html_url'],'branch':pr['pr']['head']['ref'],'local_branch':branch,'before':old,'commit':commit,'upstream':upstream,'files':changed,'stat':text(repo,'diff','--stat',upstream,commit),'dco':'Signed-off-by: Smillick <3185479846@qq.com>'}
    updates.append(entry)
    print(json.dumps(entry,ensure_ascii=False),flush=True)
(ROOT/'prepared.json').write_text(json.dumps(updates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
