"""
launch.py — normalize Launch Library 2 records to unified schema.
"""

import re
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def from_ll2_launch(launch: dict, sources: list[dict]) -> dict:
    name        = launch.get('name', 'Unknown Launch')
    status_name = launch.get('status', {}).get('name', 'Unknown') if isinstance(launch.get('status'), dict) else str(launch.get('status', ''))
    net         = launch.get('net', _now_iso())
    window_end  = launch.get('window_end', net)

    rocket      = launch.get('rocket', {}) or {}
    config      = rocket.get('configuration', {}) or {}
    vehicle     = config.get('name', 'Unknown Vehicle')

    # LL2 puts the operator in launch_service_provider, not rocket.configuration.manufacturer
    lsp         = launch.get('launch_service_provider', {}) or {}
    provider_name = lsp.get('name', '') or 'Unknown'

    # Pad coords live directly on pad (strings), not nested under location
    pad         = launch.get('pad', {}) or {}
    site        = pad.get('name', '')
    try:
        lat = float(pad.get('latitude') or 0)
        lon = float(pad.get('longitude') or 0)
    except (TypeError, ValueError):
        lat, lon = 0.0, 0.0

    # Fall back to pad.location if direct fields are absent
    if lat == 0.0 and lon == 0.0:
        loc_obj = pad.get('location', {}) or {}
        try:
            lat = float(loc_obj.get('latitude_deg') or loc_obj.get('latitude') or 0)
            lon = float(loc_obj.get('longitude_deg') or loc_obj.get('longitude') or 0)
        except (TypeError, ValueError):
            lat, lon = 0.0, 0.0

    record_id   = f'launch-{_slug(name)[:60]}'
    retrieved_at = sources[0]['retrieved_at'] if sources else _now_iso()

    orbit       = launch.get('mission', {}) or {}
    orbit_name  = orbit.get('orbit', {}) or {}
    orbit_abbr  = (orbit_name.get('abbrev', '') if isinstance(orbit_name, dict) else '').lower()
    topics      = ['launch']
    if orbit_abbr:
        topics.append(orbit_abbr)

    return {
        'schema_version': 1,
        'id':             record_id,
        'domain':         'launch_reentry',
        'type':           'launch',
        'names':          [name],
        'description':    f'Scheduled orbital launch. Auto-record.',
        'topics':         topics,
        'sources':        sources,
        'freshness':      {'last_update': retrieved_at, 'staleness_risk': 'low'},
        'related_ids':    [],
        'location': {
            'provider':     provider_name,
            'vehicle':      vehicle,
            'site':         site,
            'lat':          lat,
            'lon':          lon,
            'window_start': net,
            'window_end':   window_end,
            'status':       status_name,
        },
        'tier':      'T3',
        'watchlist': False,
        'anomalies': [],
    }
