"""
launch_library.py — Launch Library 2 (The Space Devs) poller.

No key required for the public tier; set LL2_API_KEY in .env for higher
rate limits. Fetches upcoming launches and recent reentries.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parents[2] / 'data' / 'cache' / 'launch_library'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_BASE = 'https://ll.thespacedevs.com/2.2.0'
_UPCOMING = f'{_BASE}/launch/upcoming/?format=json&limit=25&ordering=net'
_REENTRIES = f'{_BASE}/event/upcoming/?format=json&type=8'  # type 8 = reentry

_SESSION = requests.Session()
_SESSION.headers.update({'User-Agent': 'DragonEye-StarsEdition/1.0'})


def _auth_header() -> dict:
    key = os.environ.get('LL2_API_KEY', '')
    return {'Authorization': f'Token {key}'} if key else {}


def _fetch(url: str, cache_name: str, max_age_hours: float = 1.0) -> dict | None:
    cache_path = CACHE_DIR / f'{cache_name}.json'

    if cache_path.exists():
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_h < max_age_hours:
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass

    try:
        r = _SESSION.get(url, headers=_auth_header(), timeout=30)
        r.raise_for_status()
        data = r.json()
        cache_path.write_text(json.dumps(data), encoding='utf-8')
        return data
    except Exception as e:
        print(f'[ll2] fetch error ({cache_name}): {e}')
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass
    return None


def fetch_upcoming_launches(max_age_hours: float = 1.0) -> list[dict]:
    data = _fetch(_UPCOMING, 'upcoming_launches', max_age_hours=max_age_hours)
    return data.get('results', []) if data else []


def fetch_upcoming_reentries(max_age_hours: float = 1.0) -> list[dict]:
    data = _fetch(_REENTRIES, 'upcoming_reentries', max_age_hours=max_age_hours)
    return data.get('results', []) if data else []


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def source_entry(retrieved_at: str = None) -> dict:
    return {
        'name': 'launch-library-2',
        'url': 'https://thespacedevs.com/',
        'retrieved_at': retrieved_at or now_iso(),
    }
