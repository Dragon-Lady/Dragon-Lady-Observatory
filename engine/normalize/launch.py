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
    provider    = config.get('manufacturer', {}) or {}
    provider_name = (provider.get('name', '') if isinstance(provider, dict)
                     else launch.get('launch_service_provider', {}).get('name', 'Unknown')) or 'Unknown'

    pad         = launch.get('pad', {}) or {}
    site        = pad.get('name', '')
    location    = pad.get('location', {}) or {}
    lat         = float(location.get('latitude_deg', 0) or 0)
    lon         = float(location.get('longitude_deg', 0) or 0)

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
