from pathlib import Path
import base64

ROOT = Path(__file__).parent
payloads = {name: base64.b64encode((ROOT / 'wrappers' / (name + '.py')).read_bytes()).decode('ascii')
            for name in ['legacy', 'strict', 'repaired']}
(ROOT / 'verify_remote.py').write_text('PAYLOADS=' + repr(payloads) + '\n'
    + (ROOT / 'verify_remote_body.py').read_text(encoding='utf-8'), encoding='utf-8')
