"""
space_weather.py — normalize NOAA SWPC data to unified records.

Handles X-ray flux (flares) and Kp index (geomagnetic storms).
"""

import re
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def _flare_class(flux: float) -> str:
    """Convert GOES X-ray flux (W/m^2) to flare class string."""
    if flux >= 1e-3:
        return f'X{flux/1e-3:.1f}'
    if flux >= 1e-4:
        return f'M{flux/1e-4:.1f}'
    if flux >= 1e-5:
        return f'C{flux/1e-5:.1f}'
    if flux >= 1e-6:
        return f'B{flux/1e-6:.1f}'
    return f'A{flux/1e-7:.1f}'


def from_xray_peak(peak: dict, sources: list[dict]) -> dict:
    """
    Normalize a GOES X-ray peak event to a unified space_weather record.
    `peak` is derived from the xrays JSON feed by the flare detector.
    Expected keys: time_tag, flux, region (optional), onset (optional).
    """
    ts      = peak.get('time_tag', _now_iso())
    flux    = float(peak.get('flux', 0))
    region  = peak.get('region', 'unknown')
    onset   = peak.get('onset', ts)
    f_class = _flare_class(flux)

    record_id = f'spacewx-flare-{_slug(f_class)}-{_slug(ts[:13])}'

    retrieved_at = sources[0]['retrieved_at'] if sources else _now_iso()

    topics = ['space_weather', 'flare']
    if flux >= 1e-3:
        topics.append('x_class')
    elif flux >= 1e-4:
        topics.append('m_class')

    return {
        'schema_version': 1,
        'id':             record_id,
        'domain':         'space_weather',
        'type':           'flare',
        'names':          [f'{f_class} flare — {region}'],
        'description':    f'Solar flare detected by GOES. Class {f_class}. Auto-record.',
        'topics':         topics,
        'sources':        sources,
        'freshness':      {'last_update': retrieved_at, 'staleness_risk': 'low'},
        'related_ids':    [],
        'location': {
            'region':    region,
            'intensity': f_class,
            'onset':     onset,
            'peak':      ts,
        },
        'tier':      'T3',
        'watchlist': False,
        'anomalies': [],
    }


def from_kp(kp_value: float, time_tag: str, sources: list[dict]) -> dict:
    """Normalize a Kp index reading to a unified space_weather record."""
    record_id = f'spacewx-kp-{_slug(time_tag[:13])}'
    retrieved_at = sources[0]['retrieved_at'] if sources else _now_iso()

    topics = ['space_weather', 'geomagnetic']
    if kp_value >= 8:
        topics.append('severe')
    elif kp_value >= 5:
        topics.append('storm')

    return {
        'schema_version': 1,
        'id':             record_id,
        'domain':         'space_weather',
        'type':           'geomagnetic',
        'names':          [f'Kp {kp_value}'],
        'description':    f'Geomagnetic Kp index reading: {kp_value}. Auto-record.',
        'topics':         topics,
        'sources':        sources,
        'freshness':      {'last_update': retrieved_at, 'staleness_risk': 'low'},
        'related_ids':    [],
        'location': {
            'region':    'global',
            'intensity': f'Kp{kp_value}',
            'onset':     time_tag,
            'peak':      time_tag,
        },
        'tier':      'T3',
        'watchlist': False,
        'anomalies': [],
    }
