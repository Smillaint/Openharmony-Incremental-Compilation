from pathlib import Path
import base64
import json

ROOT = Path(__file__).parent
plan = json.loads((ROOT / 'plan.json').read_text(encoding='utf-8'))
path = Path(plan['repo']) / 'ets1.2/package.json'
data = path.read_bytes()
data.decode('utf-8')
(ROOT / 'files/ets1.2').mkdir(parents=True, exist_ok=True)
(ROOT / 'files/ets1.2/package.json').write_bytes(data)
source = 'EXPECTED_ORIGINAL_HASH=' + repr(plan['before_sha256']) + '\n'
source += 'FIXED_PACKAGE_B64=' + repr(base64.b64encode(data).decode('ascii')) + '\n'
source += (ROOT / 'stale_lock_remote.py').read_text(encoding='utf-8')
(ROOT / 'verify_fix_remote.py').write_text(source, encoding='utf-8')
