"""
esa_neocc.py — ESA NEOCC (Near Earth Object Coordination Centre) poller.

STATUS: API shape pending confirmation. See DATA_SOURCES.md note.

ESA NEOCC portal: https://neo.ssa.esa.int/
The REST API structure needs verification against their live docs before
the fetch URLs are finalized. Using MPC (Minor Planet Center) as the
working fallback until confirmed.

TODO Rocky: visit https://neo.ssa.esa.int/ -> API / Developer docs tab,
confirm endpoint paths for:
  - Close approach list (current + upcoming)
  - Risk list (Palermo + Torino scale)
  - Object orbit parameters by designation
Then update _CA_URL, _RISK_URL below and remove this TODO block.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parents[2] / 'data' / 'cache' / 'neocc'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ESA NEOCC — confirm these endpoints before using
_NEOCC_BASE = 'https://neo.ssa.esa.int'
_CA_URL     = f'{_NEOCC_BASE}/PSDB-portlet/download?file=close_approaches'  # UNCONFIRMED

# MPC fallback — confirmed working, no key
_MPC_CLOSE  = 'https://minorplanetcenter.net/mpc/search_orbits?limit=50&e=-2'

_SESSION = requests.Session()
_SESSION.headers.update({'User-Agent': 'DragonEye-StarsEdition/1.0'})


def _fetch_mpc_close(max_age_hours: float = 6.0) -> list[dict]:
    """MPC close approaches fallback — works immediately, no key."""
    cache_path = CACHE_DIR / 'mpc_close.json'

    if cache_path.exists():
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_h < max_age_hours:
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass

    try:
        r = _SESSION.get(_MPC_CLOSE, timeout=30)
        r.raise_for_status()
        data = r.json()
        rows = data if isinstance(data, list) else data.get('data', [])
        cache_path.write_text(json.dumps(rows), encoding='utf-8')
        return rows
    except Exception as e:
        print(f'[neocc/mpc] fetch error: {e}')
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass
    return []


def fetch_close_approaches(max_age_hours: float = 6.0) -> list[dict]:
    """
    Fetch NEO close approach data.
    Currently uses MPC fallback; will switch to ESA NEOCC once API confirmed.
    """
    return _fetch_mpc_close(max_age_hours=max_age_hours)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def source_entry(retrieved_at: str = None) -> dict:
    return {
        'name': 'esa-neocc',
        'url': 'https://neo.ssa.esa.int/',
        'retrieved_at': retrieved_at or now_iso(),
    }
