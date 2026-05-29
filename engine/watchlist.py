"""
watchlist.py — load the watchlist and check records against it.

Anchors on static identity: norad_id / intl_designator / neo_designation.
Never ephemeral state (callsign, TLE hash, etc.) — Dragon Eye's lock-by-
registration rule applied to space objects.
"""

import json
from pathlib import Path


_WATCHLIST_PATH = Path(__file__).parents[1] / 'config' / 'watchlist.json'
_EXAMPLE_PATH   = Path(__file__).parents[1] / 'config' / 'watchlist.example.json'
_watchlist: list[dict] | None = None


def _load() -> list[dict]:
    global _watchlist
    if _watchlist is not None:
        return _watchlist
    # Only load the real watchlist.json — never fall back to the example file.
    # The example is documentation, not live config. Baseline objects (ISS etc.)
    # sit at T3 until explicitly added to watchlist.json.
    if _WATCHLIST_PATH.exists():
        try:
            data = json.loads(_WATCHLIST_PATH.read_text(encoding='utf-8'))
            _watchlist = data.get('entries', [])
        except Exception:
            _watchlist = []
    else:
        _watchlist = []
    return _watchlist


def is_watchlisted(record: dict) -> bool:
    """
    Return True if any watchlist entry matches this record's static identity.
    Matching is exact on the anchored field; no fuzzy / partial match.
    """
    entries = _load()
    loc = record.get('location', {})
    domain = record.get('domain', '')

    for entry in entries:
        m = entry.get('match', {})

        if 'norad_id' in m and loc.get('norad_id') == m['norad_id']:
            return True
        if 'intl_designator' in m and loc.get('intl_designator') == m['intl_designator']:
            return True
        if ('neo_designation' in m and domain == 'neo'
                and loc.get('designation') == m['neo_designation']):
            return True

    return False
