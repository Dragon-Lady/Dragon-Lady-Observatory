"""
orbital.py — normalize CelesTrak / Space-Track GP records to unified record.

Handles both CelesTrak satcat JSON and Space-Track GP JSON (same GP schema).
"""

import re
from datetime import datetime, timezone

from engine.freshness import staleness_risk


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def _regime(mean_motion: float, ecc: float) -> str:
    """Classify orbit regime from mean motion (rev/day) + eccentricity."""
    if ecc > 0.25:
        return 'HEO'
    if mean_motion >= 11.25:
        return 'LEO'
    if mean_motion >= 0.8:
        return 'MEO'
    return 'GEO'


def _apogee_perigee(mean_motion: float, ecc: float) -> tuple[float, float]:
    """Rough apogee/perigee in km from mean_motion (rev/day) + eccentricity."""
    MU = 398600.4418  # km^3/s^2
    RE = 6371.0
    n_rad_s = mean_motion * 2 * 3.14159265 / 86400
    try:
        a = (MU / (n_rad_s ** 2)) ** (1 / 3)
    except ZeroDivisionError:
        return 0, 0
    apogee  = a * (1 + ecc) - RE
    perigee = a * (1 - ecc) - RE
    return round(apogee, 1), round(perigee, 1)


def from_gp(gp: dict, sources: list[dict]) -> dict:
    """
    Normalize a CelesTrak/Space-Track GP record to unified schema.
    `gp` is one entry from the JSON catalog (CCSDS GP format).
    `sources` is the list of source entries already built by the caller.
    """
    norad    = int(gp.get('NORAD_CAT_ID', 0))
    intl_des = gp.get('OBJECT_ID', '') or gp.get('INTLDES', '')
    name     = gp.get('OBJECT_NAME', '') or gp.get('SATNAME', f'NORAD-{norad}')
    epoch    = gp.get('EPOCH', _now_iso())
    mm       = float(gp.get('MEAN_MOTION', 0))
    ecc      = float(gp.get('ECCENTRICITY', 0))
    inc      = float(gp.get('INCLINATION', 0))
    tle1     = gp.get('TLE_LINE1', '')
    tle2     = gp.get('TLE_LINE2', '')

    obj_type_raw = gp.get('OBJECT_TYPE', '') or gp.get('OBJECT_TYPE', '')
    type_map = {
        'PAYLOAD': 'satellite',
        'ROCKET BODY': 'rocket_body',
        'DEBRIS': 'debris',
        'UNKNOWN': 'satellite',
    }
    obj_type = type_map.get(obj_type_raw.upper(), 'satellite')

    apogee, perigee = _apogee_perigee(mm, ecc)
    regime = _regime(mm, ecc)

    record_id = f'orbital-{norad}-{_slug(name)}'

    retrieved_at = sources[0]['retrieved_at'] if sources else _now_iso()
    stale = staleness_risk('orbital', retrieved_at, elset_epoch_iso=epoch)

    topics = [regime.lower()]
    if obj_type == 'debris':
        topics.append('debris')
    if obj_type == 'rocket_body':
        topics.append('rocket_body')

    names = [name]
    if str(norad):
        names.append(str(norad))
    if intl_des:
        names.append(intl_des)

    return {
        'schema_version': 1,
        'id':             record_id,
        'domain':         'orbital',
        'type':           obj_type,
        'names':          names,
        'description':    f'{obj_type.replace("_", " ").title()} in {regime}. Auto-record.',
        'topics':         topics,
        'sources':        sources,
        'freshness':      {'last_update': retrieved_at, 'staleness_risk': stale},
        'related_ids':    [],
        'location': {
            'norad_id':         norad,
            'intl_designator':  intl_des,
            'elset': {
                'epoch':        epoch,
                'tle1':         tle1,
                'tle2':         tle2,
                'mean_motion':  mm,
                'ecc':          ecc,
                'inc':          inc,
            },
            'apogee_km':  apogee,
            'perigee_km': perigee,
            'regime':     regime,
        },
        'tier':      'T3',
        'watchlist': False,
        'anomalies': [],
    }
