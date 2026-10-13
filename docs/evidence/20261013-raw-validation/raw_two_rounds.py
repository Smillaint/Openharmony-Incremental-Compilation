#!/usr/bin/env python3
"""Record a clean build and one unchanged incremental build of the raw checkout."""

from pathlib import Path
import datetime
import fcntl
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import time

ROOT = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_1a6915832/code')
OLD = Path('/srv/workspace/openharmony_master_default_20261012175945_huawei_3f7104f86/code')
HERE = ROOT.parent / 'raw_validation_20261013'
CONFIG = OLD.parent / 'ab_incremental_20261013/variants.json'
COMMAND = ['bash', './build.sh', '-p', 'rk3568', '--build-target', 'make_all', '--ninja-args=-dexplain']


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def git(root, repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(root / repo), *args],
                                   env=dict(os.environ, GIT_OPTIONAL_LOCKS='0', **(env or {})))


def guard():
    assert ROOT.resolve() == ROOT and (ROOT / '.repo/manifest.xml').is_file()
    for name in ['ninja', 'gn', 'cc1', 'cc1plus']:
        assert subprocess.run(['pgrep', '-x', name], capture_output=True).returncode != 0, name
    for row in subprocess.check_output(['ps', '-eo', 'pid,args'], text=True, encoding='utf-8').splitlines()[1:]:
        pid, _, command = row.strip().partition(' ')
        if pid != str(os.getpid()):
            assert 'bash ./build.sh' not in command and '/build/hb/main.py' not in command, row


def sources(config):
    result = {}
    for name in config['paths']:
        p = ROOT / name
        assert not p.is_symlink(), name
        result[name] = None if not p.exists() else dict(
            sha256=hashlib.sha256(p.read_bytes()).hexdigest(), mode=p.stat().st_mode & 0o777)
    return result


def logs():
    for folder in [ROOT / 'out', ROOT / 'out/rk3568']:
        if folder.is_dir():
            for p in folder.iterdir():
                if p.is_file() and (p.suffix in ['.log', '.gn', '.json'] or p.name in ['.ninja_log', '.ninja_deps']):
                    yield p


def prepare():
    guard()
    assert not (HERE / 'prepared.json').exists(), 'Already prepared; do not clean again'
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    expected = {k: None if v is None else {field: v[field] for field in ['sha256', 'mode']}
                for k, v in config['variants']['baseline'].items()}
    assert sources(config) == expected, 'Raw source differs from the mounted original baseline'
    heads = {}
    for repo in (ROOT / '.repo/project.list').read_text(encoding='utf-8').splitlines():
        heads[repo] = git(ROOT, repo, 'rev-parse', 'HEAD').decode('utf-8').strip()
        assert heads[repo] == git(OLD, repo, 'rev-parse', 'HEAD').decode('utf-8').strip(), repo
    save(HERE / 'heads.json', heads)
    save(HERE / 'source-before.json', sources(config))
    shutil.copyfile(ROOT / '.repo/manifest.xml', HERE / 'manifest.xml')
    snapshots = {}
    for repo in config['heads']:
        directory = HERE / 'before' / repo.replace('/', '_')
        directory.mkdir(parents=True, exist_ok=True)
        environment = {'GIT_INDEX_FILE': str(directory / 'snapshot.index'),
                       'GIT_AUTHOR_NAME': 'SmillySmillick', 'GIT_COMMITTER_NAME': 'SmillySmillick',
                       'GIT_AUTHOR_EMAIL': 'SmillySmillick@users.noreply.github.com',
                       'GIT_COMMITTER_EMAIL': 'SmillySmillick@users.noreply.github.com'}
        git(ROOT, repo, 'read-tree', 'HEAD', env=environment)
        git(ROOT, repo, 'add', '-u', env=environment)
        tree = git(ROOT, repo, 'write-tree', env=environment).decode('utf-8').strip()
        commit = git(ROOT, repo, 'commit-tree', tree, '-p', heads[repo], '-m',
                     'Preserve raw checkout before build comparison', env=environment).decode('utf-8').strip()
        ref = 'refs/heads/backup/before-raw-comparison-20261013'
        git(ROOT, repo, 'update-ref', ref, commit)
        (directory / 'worktree.patch').write_bytes(git(ROOT, repo, 'diff', '--binary', heads[repo], commit))
        snapshots[repo] = dict(head=heads[repo], snapshot=commit, ref=ref)
    save(HERE / 'snapshots.json', snapshots)
    out = ROOT / 'out'
    assert out.parent == ROOT and out.resolve() == out and not out.is_symlink()
    for line in Path('/proc/self/mountinfo').read_text(encoding='utf-8').splitlines():
        mount = line.split()[4].replace('\\040', ' ')
        assert mount != str(out) and not mount.startswith(str(out) + '/'), mount
    hashes = {}
    with tarfile.open(HERE / 'before-clean-logs.tar.gz', 'w:gz') as archive:
        for path in logs():
            name = path.relative_to(out).as_posix()
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            archive.add(path, arcname=name)
    with tarfile.open(HERE / 'before-clean-logs.tar.gz') as archive:
        for name, digest in hashes.items():
            assert hashlib.sha256(archive.extractfile(name).read()).hexdigest() == digest
    save(HERE / 'before-clean-log-hashes.json', hashes)
    guard()
    print('CLEANING', out, 'saved_logs', len(hashes), flush=True)
    started = time.monotonic()
    subprocess.run(['rm', '-rf', '--one-file-system', '--', str(out)], check=True)
    assert not os.path.lexists(out) and sources(config) == expected
    save(HERE / 'prepared.json', dict(root=str(ROOT), prepared_utc=utc(), out_absent=True,
         clean_seconds=time.monotonic() - started, project_heads_matched=len(heads),
         baseline_paths_matched=len(expected), command=COMMAND))
    print('PREPARED', HERE, flush=True)


def run():
    guard()
    assert (HERE / 'prepared.json').is_file() and not (ROOT / 'out').exists()
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    assert sources(config) == json.loads((HERE / 'source-before.json').read_text(encoding='utf-8'))
    child = None

    def interrupt(signum, frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signum)
        raise SystemExit(128 + signum)

    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
        signal.signal(sig, interrupt)
    for phase in ['full', 'increment1']:
        guard()
        folder = HERE / phase
        folder.mkdir()
        before = sources(config)
        save(folder / 'source-before.json', before)
        status = dict(phase=phase, state='running', root=str(ROOT), command=COMMAND,
                      started_utc=utc(), runner_pid=os.getpid())
        started = time.monotonic()
        with (folder / 'console.log').open('wb', buffering=0) as console:
            child = subprocess.Popen(COMMAND, cwd=ROOT, stdin=subprocess.DEVNULL,
                                     stdout=console, stderr=subprocess.STDOUT, start_new_session=True)
            status['build_pid'] = child.pid
            save(HERE / 'status.json', status)
            save(folder / 'status.json', status)
            print('START', phase, child.pid, status['started_utc'], flush=True)
            code = child.wait()
        status.update(state='complete' if code == 0 else 'failed', exit_code=code,
                      wall_seconds=time.monotonic() - started, finished_utc=utc())
        save(HERE / 'status.json', status)
        save(folder / 'status.json', status)
        for path in logs():
            destination = folder / 'build-state' / path.relative_to(ROOT / 'out')
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        after = sources(config)
        save(folder / 'source-after.json', after)
        print('END', json.dumps(status), flush=True)
        if code != 0:
            return code
        if phase == 'increment1':
            status['managed_source_unchanged'] = before == after
            save(folder / 'status.json', status)
    status.update(state='complete', rounds_completed=2)
    save(HERE / 'status.json', status)
    return 0


if __name__ == '__main__':
    HERE.mkdir(exist_ok=True)
    with (HERE / 'run.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if sys.argv[1:] == ['prepare']:
            prepare()
        elif sys.argv[1:] == ['run']:
            raise SystemExit(run())
        else:
            raise SystemExit('Usage: raw_two_rounds.py {prepare|run}')
