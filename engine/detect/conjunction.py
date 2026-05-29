"""
detect/conjunction.py -- CDM-based conjunction / close approach detector.

Tiers conjunctions by Pc + miss distance per standard ops screening bands.
Returns None for routine/background conjunctions (Pc < 1e-5, large miss).
"""

import re
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# Pc screening bands (probability of collision)
_PC_T1   = 1e-4    # T1: Pc >= 1e-4 (1 in 10,000) -- genuinely high risk
_PC_T2   = 1e-5    # T2: 1e-5 <= Pc < 1e-4
_PC_MIN  = 1e-5    # below this: don't emit a record (background noise)

# Miss distance secondary gates (km)
_MISS_T1 = 1.0     # < 1 km with any non-trivial Pc -> T1
_MISS_T2 = 5.0     # < 5 km -> at least T2 regardless of Pc


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def _safe_name(sat_id: str, sat_name: str) -> str:
    """Use name if available, fall back to NORAD ID."""
    n = (sat_name or '').strip()
    return n if n and n != sat_id else sat_id


def from_cdm(cdm: dict, sources: list[dict]) -> dict | None:
    """
    Normalize a Space-Track CDM record to a unified conjunction record.

    Returns None for background conjunctions (Pc < 1e-5 and miss > 5 km).
    Tier is set by Pc + miss distance; the caller may override via watchlist.
    """
    sat1_id   = str(cdm.get('SAT1_ID',   '') or cdm.get('OBJECT1_ID',   '') or '').strip()
    sat2_id   = str(cdm.get('SAT2_ID',   '') or cdm.get('OBJECT2_ID',   '') or '').strip()
    sat1_name = str(cdm.get('SAT1_NAME', '') or cdm.get('OBJECT1_NAME', '') or '').strip()
    sat2_name = str(cdm.get('SAT2_NAME', '') or cdm.get('OBJECT2_NAME', '') or '').strip()

    tca     = cdm.get('TCA', _now_iso())
    miss_km = float(cdm.get('MISS_DISTANCE',        cdm.get('MISS',      9999)) or 9999)
    pc      = float(cdm.get('COLLISION_PROBABILITY', cdm.get('PC',           0)) or 0)
    rel_vel = float(cdm.get('RELATIVE_SPEED',        cdm.get('REL_SPEED',    0)) or 0)
    regime  = str(cdm.get('ORBIT_REGIME', 'LEO') or 'LEO')

    # Skip pure background — Pc too low and miss too large to be meaningful
    if pc < _PC_MIN and miss_km > _MISS_T2:
        return None

    # Determine tier from Pc + miss distance
    if pc >= _PC_T1 or (miss_km < _MISS_T1 and pc > 0):
        tier      = 'T1'
        anom_kind = 'conjunction_high_pc'
    elif pc >= _PC_T2 or miss_km < _MISS_T2:
        tier      = 'T2'
        anom_kind = 'conjunction_high_pc'
    else:
        return None  # below both gates

    now          = _now_iso()
    a_label      = _safe_name(sat1_id, sat1_name)
    b_label      = _safe_name(sat2_id, sat2_name)
    display_name = f'{a_label} x {b_label}'   # ASCII-safe
    record_id    = f'orbital-conj-{_slug(sat1_id or "unk")}-{_slug(sat2_id or "unk")}'
    retrieved_at = sources[0]['retrieved_at'] if sources else now

    confidence = min(0.97, pc * 5000 + 0.4) if pc > 0 else 0.6

    anomalies = [{
        'kind':       anom_kind,
        'confidence': round(confidence, 3),
        'evidence':   [{
            'reason':      f'Miss distance {miss_km:.3f} km; Pc {pc:.2e}',
            'metric':      'miss_distance',
            'value':       miss_km,
            'source_ref':  'space-track',
            'observed_at': now,
        }],
        'delta': {
            'miss_distance_km':         miss_km,
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
        'names':          [display_name],
        'description':    f'Predicted close approach: {display_name}. Auto-record.',
        'topics':         ['conjunction', regime.lower()],
        'sources':        sources,
        'freshness':      {'last_update': retrieved_at, 'staleness_risk': 'low'},
        'related_ids':    [],
        'location': {
            'tca':                   tca,
            'miss_distance_km':      miss_km,
            'relative_velocity_kms': rel_vel,
            'regime':                regime,
        },
        'tier':      tier,
        'watchlist': False,
        'anomalies': anomalies,
    }
