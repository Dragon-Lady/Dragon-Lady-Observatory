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

# CelesTrak GP catalog — JSON format for orbital element normalization.
# NOTE: this format does NOT include TLE_LINE1/TLE_LINE2 text.
# Use fetch_tle_records() for the TLE text bundle (satellite.js needs raw TLE).
_GP_CATALOG  = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json'

# CelesTrak TLE text format — 3-line format (name / tle1 / tle2) for the globe bundle.
_TLE_CATALOG = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'

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
    Fetch GP orbital elements (JSON format) for normalization.
    Returns list of GP records with MEAN_MOTION, ECCENTRICITY, etc.
    Does NOT include TLE text lines — use fetch_tle_records() for that.
    """
    data = _fetch_json(_GP_CATALOG, 'satcat', max_age_hours=max_age_hours)
    return data or []


def fetch_tle_records(max_age_hours: float = 4.0) -> list[dict]:
    """
    Fetch TLE text format and parse into records with tle1/tle2 fields.
    This is what the globe bundle (satellite.js) needs.
    Returns list of {'norad_id', 'name', 'tle1', 'tle2'} dicts.
    """
    cache_path = CACHE_DIR / 'tle_text.txt'

    if cache_path.exists():
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600
        if age_h < max_age_hours:
            return _parse_tle_text(cache_path.read_text(encoding='utf-8', errors='replace'))

    try:
        r = _SESSION.get(_TLE_CATALOG, timeout=60)
        r.raise_for_status()
        text = r.text
        cache_path.write_text(text, encoding='utf-8')
        return _parse_tle_text(text)
    except Exception as e:
        print(f'[celestrak] TLE fetch error: {e}')
        if cache_path.exists():
            return _parse_tle_text(cache_path.read_text(encoding='utf-8', errors='replace'))
    return []


def _parse_tle_text(text: str) -> list[dict]:
    """Parse 3-line TLE text format into list of records."""
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    records = []
    i = 0
    while i + 2 < len(lines):
        name = lines[i].strip()
        tle1 = lines[i + 1].strip()
        tle2 = lines[i + 2].strip()
        if tle1.startswith('1 ') and tle2.startswith('2 '):
            try:
                norad = int(tle1[2:7].strip())
            except ValueError:
                norad = 0
            records.append({
                'name':    name,
                'norad_id': norad,
                'tle1':    tle1,
                'tle2':    tle2,
            })
            i += 3
        else:
            i += 1
    return records


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def source_entry(retrieved_at: str = None) -> dict:
    return {
        'name': 'celestrak',
        'url': 'https://celestrak.org/',
        'retrieved_at': retrieved_at or now_iso(),
    }
