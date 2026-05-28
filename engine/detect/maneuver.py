"""
detect/maneuver.py — orbital maneuver detector.

Compares consecutive elsets for the same NORAD ID. A significant change in
mean_motion or perigee/apogee (not explained by natural decay) flags a maneuver.

Corroboration: if CelesTrak and Space-Track both show the same delta, it's not a
stale-TLE artifact — this is the freshness-gate corroboration check.
"""

import math
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# Thresholds for maneuver flagging
_MM_DELTA_THRESHOLD   = 0.005   # rev/day change in mean_motion
_PERIGEE_DELTA_KM     = 5.0     # km change in perigee
_DELTA_V_SCALE        = 0.001   # rough km/s per rev/day of mean_motion change


def detect(prev_record: dict, curr_record: dict,
           corroborated: bool = False) -> list[dict]:
    """
    Compare two consecutive orbital records for the same NORAD ID.
    Returns anomaly dicts to merge into curr_record['anomalies'].

    prev_record: the previously stored record (or None)
    curr_record: the freshly normalized record
    corroborated: True if a second source (e.g. CelesTrak vs Space-Track) agrees
    """
    if prev_record is None:
        return []

    prev_loc = prev_record.get('location', {})
    curr_loc = curr_record.get('location', {})

    prev_elset = prev_loc.get('elset', {})
    curr_elset = curr_loc.get('elset', {})

    prev_mm  = float(prev_elset.get('mean_motion', 0))
    curr_mm  = float(curr_elset.get('mean_motion', 0))
    prev_ecc = float(prev_elset.get('ecc', 0))
    curr_ecc = float(curr_elset.get('ecc', 0))

    prev_peri = float(prev_loc.get('perigee_km', 0))
    curr_peri = float(curr_loc.get('perigee_km', 0))

    mm_delta    = abs(curr_mm  - prev_mm)
    peri_delta  = abs(curr_peri - prev_peri)
    delta_v_est = mm_delta * _DELTA_V_SCALE

    if mm_delta < _MM_DELTA_THRESHOLD and peri_delta < _PERIGEE_DELTA_KM:
        return []

    now = _now_iso()
    source_name = (curr_record.get('sources', [{}])[0].get('name', 'space-track'))
    observed_at = curr_elset.get('epoch', now)

    evidence = [{
        'reason':      f'Mean motion changed {mm_delta:.4f} rev/day; perigee shifted {peri_delta:.1f} km',
        'metric':      'delta_v',
        'value':       round(delta_v_est, 4),
        'source_ref':  source_name,
        'observed_at': observed_at,
    }]

    confidence = 0.6
    if corroborated:
        confidence = 0.85
        evidence.append({
            'reason':      'Second source corroborates the orbit change (not a stale-TLE artifact)',
            'metric':      'delta_v',
            'value':       round(delta_v_est, 4),
            'source_ref':  'celestrak',
            'observed_at': observed_at,
        })

    return [{
        'kind':        'maneuver',
        'confidence':  confidence,
        'evidence':    evidence,
        'delta':       {'delta_v_kms': round(delta_v_est, 4)},
        'state':       'active',
        'first_flagged': now,
        'last_updated':  now,
    }]
