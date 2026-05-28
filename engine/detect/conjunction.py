"""
detect/conjunction.py — CDM-based conjunction / close approach detector.

Reads Space-Track CDM (Conjunction Data Message) records and emits
conjunction records with the high-Pc anomaly when the miss distance or
probability of collision crosses the screening threshold.
"""

import re
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# Screening thresholds
_PC_THRESHOLD          = 1e-4     # probability of collision
_MISS_KM_THRESHOLD     = 1.0     # miss distance in km


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def from_cdm(cdm: dict, sources: list[dict]) -> dict | None:
    """
    Normalize a Space-Track CDM record to a unified conjunction record,
    with a conjunction_high_pc anomaly if thresholds are met.

    Returns None if the CDM does not clear the screening threshold.
    """
    sat1_id = str(cdm.get('SAT1_ID', '') or cdm.get('OBJECT1_ID', ''))
    sat2_id = str(cdm.get('SAT2_ID', '') or cdm.get('OBJECT2_ID', ''))
    tca     = cdm.get('TCA', _now_iso())
    miss_km = float(cdm.get('MISS_DISTANCE', cdm.get('MISS', 9999)) or 9999)
    pc      = float(cdm.get('COLLISION_PROBABILITY', cdm.get('PC', 0)) or 0)
    rel_vel = float(cdm.get('RELATIVE_SPEED', cdm.get('REL_SPEED', 0)) or 0)
    regime  = cdm.get('ORBIT_REGIME', 'LEO')

    if miss_km > _MISS_KM_THRESHOLD and pc < _PC_THRESHOLD:
        return None

    now = _now_iso()
    record_id = f'orbital-conj-{_slug(sat1_id)}-{_slug(sat2_id)}'
    retrieved_at = sources[0]['retrieved_at'] if sources else now

    anomalies = [{
        'kind':        'conjunction_high_pc',
        'confidence':  min(0.95, pc * 1000 + 0.5) if pc > 0 else 0.75,
        'evidence':    [{
            'reason':      f'Miss distance {miss_km:.3f} km; Pc {pc:.2e}',
            'metric':      'miss_distance',
            'value':       miss_km,
            'source_ref':  'space-track',
            'observed_at': now,
        }],
        'delta': {
            'miss_distance_km':        miss_km,
            'probability_of_collision': pc,
        },
        'state':        'active',
        'first_flagged': now,
        'last_updated':  now,
    }]

    return {
        'schema_version': 1,
        'id':             record_id,
        'domain':         'orbital',
        'type':           'conjunction',
        'names':          [f'Conjunction {sat1_id} × {sat2_id}'],
        'description':    'Predicted close approach between two catalogued objects. Auto-record.',
        'topics':         ['conjunction', regime.lower()],
        'sources':        sources,
        'freshness':      {'last_update': retrieved_at, 'staleness_risk': 'low'},
        'related_ids':    [],
        'location': {
            'tca':                 tca,
            'miss_distance_km':    miss_km,
            'relative_velocity_kms': rel_vel,
            'regime':              regime,
        },
        'tier':      'T1',
        'watchlist': False,
        'anomalies': anomalies,
    }
