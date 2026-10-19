from pathlib import Path
import base64
import gzip
import json
import subprocess

ROOT = Path(__file__).parent
REPO = Path(r'D:\workspace\repositories\companion-prs-20261015\developtools_ace_ets2bundle')
REVISION = '9e0f9e58a243d7aeab672c317a2322dc37efd1a7'
archive = subprocess.check_output(['git', '-C', str(REPO), 'archive', REVISION, 'ets1.2'])
compressed = gzip.compress(archive, mtime=0)
(ROOT / 'failed-gate-ets1.2.tar.gz').write_bytes(compressed)
script = (ROOT / 'verify_fix_remote.py').read_text(encoding='utf-8')
script = script.replace("archive_bytes = subprocess.check_output(['git', '-C', str(ACE), 'archive', 'HEAD', 'ets1.2'])",
                        "archive_bytes = gzip.decompress(base64.b64decode(SOURCE_ARCHIVE_B64))")
script = script.replace('import hashlib\n', 'import hashlib\nimport gzip\n')
script = script.replace("'fixture_boundary': 'Synthetic older local-package graph; not the unavailable CI package-lock.json.'",
                        "'source_revision': '" + REVISION + "', 'fixture_boundary': 'Exact failed-gate tracked source; synthetic old lock, not the CI lockfile.'")
source = "SOURCE_ARCHIVE_B64 = " + repr(base64.b64encode(compressed).decode('ascii')) + '\n' + script
command = ['ssh', '-p', '42247', '-i', r'C:\Users\31854\.ssh\id_ed25519',
           '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
           'root@119.3.182.128', 'python3 -']
result = subprocess.run(command, input=source.encode('utf-8'), capture_output=True, timeout=300)
output = result.stdout.decode('utf-8', errors='backslashreplace')
(ROOT / 'exact-gate-run.stdout.log').write_text(output, encoding='utf-8')
(ROOT / 'exact-gate-run.stderr.log').write_text(result.stderr.decode('utf-8', errors='backslashreplace'), encoding='utf-8')
print(output)
if result.returncode:
    raise SystemExit(result.returncode)
