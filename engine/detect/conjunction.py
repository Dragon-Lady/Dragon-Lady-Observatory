"""
detect/conjunction.py -- CDM-based conjunction / close approach detector.

Tiers conjunctions by Pc + miss distance per standard ops screening bands.
Returns None for routine/background conjunctions (Pc < 1e-5, large miss).
"""

import re
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# James's final tiering spec (CONJUNCTION_TIERING_FINAL_SPEC_MAY28_2026.md):
# T1: miss < 1km  OR  at least one object is an active payload (not debris x debris)
# T2: debris x debris with elevated Pc (>= 1e-5) and miss >= 1km
# T3/skip: everything else -- not emitted
_MISS_T1_KM    = 1.0    # sub-km miss -> T1 regardless of type
_PC_DEBRIS_T2  = 1e-5   # Pc floor for debris x debris to qualify as T2

# Types that count as active/operational payloads for T1.
_ACTIVE_TYPES = frozenset({'payload', 'satellite'})


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def _safe_name(sat_id: str, sat_name: str) -> str:
    """Use name if available, fall back to NORAD ID."""
    n = (sat_name or '').strip()
    return n if n and n != sat_id else sat_id


def _tle_entry(norad_str: str, name: str, tle_by_norad: dict | None) -> dict:
    """Build one object entry for location.objects, with TLEs if available."""
    entry = {
        'norad_id': int(norad_str) if norad_str.isdigit() else norad_str,
        'name':     name,
        'tle1':     '',
        'tle2':     '',
    }
    if tle_by_norad and norad_str.isdigit():
        tle = tle_by_norad.get(int(norad_str), {})
        entry['tle1'] = tle.get('tle1', '')
        entry['tle2'] = tle.get('tle2', '')
    return entry


def from_cdm(cdm: dict, sources: list[dict],
             tle_by_norad: dict | None = None,
             type_by_norad: dict | None = None) -> dict | None:
    """
    Normalize a Space-Track CDM record to a unified conjunction record.

    Returns None for background conjunctions (Pc < 1e-5 and miss > 5 km).
    Tier is set by Pc + miss distance; the caller may override via watchlist.
    """
    # Space-Track CDM field names vary by endpoint version — try all known variants
    sat1_id = str(
        cdm.get('SAT_1_ID') or cdm.get('SAT1_ID') or
        cdm.get('OBJECT_DESIGNATOR_1') or cdm.get('OBJECT1_ID') or ''
    ).strip()
    sat2_id = str(
        cdm.get('SAT_2_ID') or cdm.get('SAT2_ID') or
        cdm.get('OBJECT_DESIGNATOR_2') or cdm.get('OBJECT2_ID') or ''
    ).strip()
    sat1_name = str(
        cdm.get('SAT_1_NAME') or cdm.get('SAT1_NAME') or
        cdm.get('OBJECT_NAME_1') or cdm.get('OBJECT1_NAME') or ''
    ).strip()
    sat2_name = str(
        cdm.get('SAT_2_NAME') or cdm.get('SAT2_NAME') or
        cdm.get('OBJECT_NAME_2') or cdm.get('OBJECT2_NAME') or ''
    ).strip()

    # Last resort: dump all string-valued keys so we can see what's actually in the CDM
    if not sat1_name and not sat2_name and not sat1_id and not sat2_id:
        str_keys = {k: v for k, v in cdm.items() if isinstance(v, str) and v.strip()}
        print(f'[conjunction] CDM field debug: {list(str_keys.keys())[:15]}')

    tca = cdm.get('TCA', _now_iso())

    # MISS_DISTANCE in Space-Track CDM is in METERS (CCSDS standard).
    # Convert to km for all threshold comparisons and record output.
    miss_m  = float(cdm.get('MISS_DISTANCE', cdm.get('MIN_RNG', cdm.get('MISS', 9_999_999))) or 9_999_999)
    miss_km = miss_m / 1000.0

    pc      = float(cdm.get('COLLISION_PROBABILITY', cdm.get('PC', 0)) or 0)
    rel_vel = float(cdm.get('RELATIVE_SPEED',        cdm.get('REL_SPEED', 0)) or 0)
    regime  = str(cdm.get('ORBIT_REGIME', 'LEO') or 'LEO')

    # Prefer CDM object types directly; only fall back to an optional map.
    def _obj_type(norad_str: str, cdm_type, fallback: str = 'unknown') -> str:
        if cdm_type not in (None, ''):
            return str(cdm_type).strip().lower()
        if type_by_norad and norad_str.isdigit():
            return str(type_by_norad.get(int(norad_str), fallback)).strip().lower()
        return fallback

    type1 = _obj_type(sat1_id, cdm.get('SAT1_OBJECT_TYPE') or cdm.get('SAT_1_OBJECT_TYPE'))
    type2 = _obj_type(sat2_id, cdm.get('SAT2_OBJECT_TYPE') or cdm.get('SAT_2_OBJECT_TYPE'))
    either_active = (type1 in _ACTIVE_TYPES) or (type2 in _ACTIVE_TYPES)
    both_debris = type1 == 'debris' and type2 == 'debris'

    # James's final spec:
    # T1: miss < 1km  OR  active payload involved
    # T2: debris x debris, elevated Pc, miss >= 1km
    # else: not emitted
    if miss_km < _MISS_T1_KM or either_active:
        tier      = 'T1'
        anom_kind = 'conjunction_high_pc'
    elif both_debris and pc >= _PC_DEBRIS_T2 and miss_km >= _MISS_T1_KM:
        tier      = 'T2'
        anom_kind = 'conjunction_high_pc'
    else:
        return None  # routine background — not emitted

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
            'pc':                    pc,
            'relative_velocity_kms': rel_vel,
            'regime':                regime,
            'objects': [
                _tle_entry(sat1_id, a_label, tle_by_norad),
                _tle_entry(sat2_id, b_label, tle_by_norad),
            ],
        },
        'tier':      tier,
        'watchlist': False,
        'anomalies': anomalies,
    }
