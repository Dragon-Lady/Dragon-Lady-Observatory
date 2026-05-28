"""
celestrak.py — CelesTrak TLE poller (no API key required).

Primary role: no-key bootstrap so the engine runs before Space-Track creds
are provisioned. Secondary role: corroboration source for the freshness gate
(CelesTrak-vs-Space-Track agreement = not a stale-TLE artifact).

Caches the catalog locally in data/cache/celestrak/ and polls GP deltas only.
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parents[2] / 'data' / 'cache' / 'celestrak'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# CelesTrak GP (General Perturbations) catalog — confirmed working JSON endpoint.
# Returns full GP elements: NORAD_CAT_ID, OBJECT_NAME, OBJECT_TYPE, EPOCH,
# MEAN_MOTION, ECCENTRICITY, INCLINATION, TLE_LINE1, TLE_LINE2, etc.
_GP_CATALOG = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json'

_SESSION = requests.Session()
_SESSION.headers.update({'User-Agent': 'DragonEye-StarsEdition/1.0'})


def _fetch_json(url: str, cache_name: str, max_age_hours: float = 2.0) -> list[dict] | None:
    """Fetch JSON from url, using local cache if fresh enough."""
    cache_path = CACHE_DIR / f'{cache_name}.json'

    if cache_path.exists():
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_h < max_age_hours:
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass

    try:
        r = _SESSION.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        cache_path.write_text(json.dumps(data), encoding='utf-8')
        return data
    except Exception as e:
        print(f'[celestrak] fetch error ({url}): {e}')
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding='utf-8'))
            except Exception:
                pass
    return None


def fetch_gp_catalog(max_age_hours: float = 4.0) -> list[dict]:
    """
    Fetch the CelesTrak satellite catalog (GP elements, JSON format).
    Returns list of satcat records. Falls back to cache on error.
    """
    data = _fetch_json(_GP_CATALOG, 'satcat', max_age_hours=max_age_hours)
    return data or []


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def source_entry(retrieved_at: str = None) -> dict:
    return {
        'name': 'celestrak',
        'url': 'https://celestrak.org/',
        'retrieved_at': retrieved_at or now_iso(),
    }
