"""
space_track.py — Space-Track.org poller (USSF 18th Space Control Squadron).

THE authoritative source for the orbital catalog, elsets, conjunction data
(CDM), and decay predictions. Free registration at space-track.org required.

Credentials: set SPACETRACK_USER and SPACETRACK_PASS in .env (gitignored).
Never commit. Cache aggressively — Space-Track enforces usage limits.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parents[2] / 'data' / 'cache' / 'space_track'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_BASE   = 'https://www.space-track.org'
_LOGIN  = f'{_BASE}/ajaxauth/login'
_LOGOUT = f'{_BASE}/ajaxauth/logout'

# Key query endpoints
_GP_ALL  = f'{_BASE}/basicspacedata/query/class/gp/EPOCH/>now-30/orderby/NORAD_CAT_ID/format/json'
_CDM     = f'{_BASE}/basicspacedata/query/class/cdm_public/orderby/TCA asc/format/json'
_DECAY   = f'{_BASE}/basicspacedata/query/class/decay/DECAY/>now-7/orderby/NORAD_CAT_ID/format/json'

_SESSION = requests.Session()
_logged_in = False


def _login() -> bool:
    global _logged_in
    user = os.environ.get('SPACETRACK_USER', '')
    pw   = os.environ.get('SPACETRACK_PASS', '')
    if not user or not pw:
        print('[space-track] credentials not set — skipping (set SPACETRACK_USER / SPACETRACK_PASS in .env)')
        return False
    try:
        r = _SESSION.post(_LOGIN, data={'identity': user, 'password': pw}, timeout=20)
        r.raise_for_status()
        _logged_in = True
        return True
    except Exception as e:
        print(f'[space-track] login error: {e}')
        return False


def _fetch(url: str, cache_name: str, max_age_hours: float = 4.0) -> list[dict]:
    cache_path = CACHE_DIR / f'{cache_name}.json'

    if cache_path.exists():
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_h < max_age_hours:
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass

    global _logged_in
    if not _logged_in and not _login():
        return []

    try:
        r = _SESSION.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        cache_path.write_text(json.dumps(data), encoding='utf-8')
        return data
    except Exception as e:
        print(f'[space-track] fetch error ({cache_name}): {e}')
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass
    return []


def fetch_gp_catalog(max_age_hours: float = 4.0) -> list[dict]:
    """Fetch GP element sets for all objects with recent epochs."""
    return _fetch(_GP_ALL, 'gp_catalog', max_age_hours=max_age_hours)


def fetch_cdm(max_age_hours: float = 1.0) -> list[dict]:
    """Fetch public Conjunction Data Messages."""
    return _fetch(_CDM, 'cdm', max_age_hours=max_age_hours)


def fetch_decay(max_age_hours: float = 2.0) -> list[dict]:
    """Fetch objects with predicted decay in the next 7 days."""
    return _fetch(_DECAY, 'decay', max_age_hours=max_age_hours)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def source_entry(retrieved_at: str = None) -> dict:
    return {
        'name': 'space-track',
        'url': 'https://www.space-track.org/',
        'retrieved_at': retrieved_at or now_iso(),
    }
