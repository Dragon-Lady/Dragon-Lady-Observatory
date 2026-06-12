"""
noaa_swpc.py — NOAA Space Weather Prediction Center poller (no API key).

Fetches solar flare events, geomagnetic Kp index, and active alerts.
Caches locally; poll interval respects SWPC update cadences.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parents[2] / 'data' / 'cache' / 'swpc'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_BASE = 'https://services.swpc.noaa.gov'
_ENDPOINTS = {
    'xrays_7d':    f'{_BASE}/json/goes/primary/xrays-7-day.json',
    'kp_index':    f'{_BASE}/products/noaa-planetary-k-index.json',
    'alerts':      f'{_BASE}/products/alerts.json',
    'flares_3d':   f'{_BASE}/json/goes/primary/xrays-3-day.json',
}

_SESSION = requests.Session()
_SESSION.headers.update({'User-Agent': 'Dragon-Lady-Observatory/1.0'})


def _fetch(key: str, max_age_hours: float = 0.5) -> list | None:
    url = _ENDPOINTS[key]
    cache_path = CACHE_DIR / f'{key}.json'

    if cache_path.exists():
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_h < max_age_hours:
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass

    try:
        r = _SESSION.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        cache_path.write_text(json.dumps(data), encoding='utf-8')
        return data
    except Exception as e:
        print(f'[swpc] fetch error ({key}): {e}')
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass
    return None


def fetch_xray(max_age_hours: float = 0.25) -> list:
    """GOES X-ray flux (7-day). Used for flare detection."""
    return _fetch('xrays_7d', max_age_hours=max_age_hours) or []


def fetch_kp(max_age_hours: float = 0.5) -> list:
    """Planetary K-index. Used for geomagnetic storm detection."""
    return _fetch('kp_index', max_age_hours=max_age_hours) or []


def fetch_alerts(max_age_hours: float = 0.25) -> list:
    """SWPC alert/warning/watch products."""
    return _fetch('alerts', max_age_hours=max_age_hours) or []


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def source_entry(retrieved_at: str = None) -> dict:
    return {
        'name': 'noaa-swpc',
        'url': 'https://services.swpc.noaa.gov/',
        'retrieved_at': retrieved_at or now_iso(),
    }
