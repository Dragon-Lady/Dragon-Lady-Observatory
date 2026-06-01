"""
test_detectors.py — arm the catch before Space-Track creds land.

Feeds synthetic orbital data through the full pipeline:
  maneuver detector -> freshness gate -> tier assignment

Proves the catch logic before the live switch gets flipped.
Run: python -m engine.tests.test_detectors
"""

import sys
from datetime import datetime, timezone, timedelta


def _iso(delta_hours: float = 0) -> str:
    t = datetime.now(timezone.utc) + timedelta(hours=delta_hours)
    return t.strftime('%Y-%m-%dT%H:%M:%SZ')


def _make_orbital_record(norad_id: int, mean_motion: float, ecc: float,
                          perigee_km: float, apogee_km: float,
                          staleness: str = 'low',
                          sources: list = None,
                          epoch_offset_hours: float = 0) -> dict:
    """Build a minimal orbital record for detector testing."""
    epoch = _iso(-abs(epoch_offset_hours))
    retrieved = _iso(-0.5)
    return {
        'schema_version': 1,
        'id': f'orbital-{norad_id}-test',
        'domain': 'orbital',
        'type': 'satellite',
        'names': [f'TEST-{norad_id}', str(norad_id)],
        'description': 'Synthetic test record.',
        'topics': ['leo'],
        'sources': sources or [{'name': 'space-track', 'url': 'https://www.space-track.org/', 'retrieved_at': retrieved}],
        'freshness': {'last_update': retrieved, 'staleness_risk': staleness},
        'related_ids': [],
        'location': {
            'norad_id': norad_id,
            'intl_designator': '2025-099B',
            'elset': {
                'epoch': epoch,
                'tle1': '',
                'tle2': '',
                'mean_motion': mean_motion,
                'ecc': ecc,
                'inc': 53.0,
            },
            'apogee_km':  apogee_km,
            'perigee_km': perigee_km,
            'regime':     'LEO',
        },
        'tier':      'T3',
        'watchlist': False,
        'anomalies': [],
    }


def _pass(name: str):
    print(f'  PASS  {name}')


def _fail(name: str, detail: str):
    print(f'  FAIL  {name}: {detail}')
    return False


def run_all() -> bool:
    from engine.detect import maneuver as det_maneuver
    from engine.detect import conjunction as det_conjunction
    from engine.detect import space_weather as det_sw
    from engine.freshness import may_promote, staleness_risk
    from engine.tier import assign_tier
    from engine.normalize import space_weather as norm_sw

    ok = True
    print('\n-- Maneuver detector ------------------------------------------')

    # T1: clean maneuver — perigee raised 22km, corroborated by CelesTrak
    prev = _make_orbital_record(90211, mean_motion=14.21, ecc=0.0021,
                                perigee_km=568, apogee_km=612)
    curr = _make_orbital_record(90211, mean_motion=14.22, ecc=0.0018,
                                perigee_km=590, apogee_km=614,
                                sources=[
                                    {'name': 'space-track', 'url': 'https://www.space-track.org/', 'retrieved_at': _iso()},
                                    {'name': 'celestrak',   'url': 'https://celestrak.org/',       'retrieved_at': _iso()},
                                ])

    anomalies = det_maneuver.detect(prev, curr, corroborated=True)
    if not anomalies:
        ok = _fail('maneuver detected', 'no anomaly returned for 22km perigee raise')
    else:
        a = anomalies[0]
        if a['kind'] != 'maneuver':
            ok = _fail('maneuver kind', f'got {a["kind"]}')
        else:
            _pass('maneuver kind = maneuver')
        if a['confidence'] < 0.8:
            ok = _fail('maneuver confidence', f'corroborated confidence should be >= 0.8, got {a["confidence"]}')
        else:
            _pass(f'corroborated confidence = {a["confidence"]}')
        if len(a['evidence']) < 2:
            ok = _fail('maneuver evidence', f'corroborated should have 2 evidence items, got {len(a["evidence"])}')
        else:
            _pass(f'evidence items = {len(a["evidence"])} (space-track + celestrak)')
        tier = assign_tier(anomalies)
        if tier != 'T2':
            ok = _fail('maneuver tier', f'expected T2, got {tier}')
        else:
            _pass('maneuver tier = T2')

    # T2: no maneuver — orbit unchanged
    same = _make_orbital_record(90211, mean_motion=14.21, ecc=0.0021,
                                perigee_km=568, apogee_km=612)
    no_anom = det_maneuver.detect(same, same, corroborated=False)
    if no_anom:
        ok = _fail('no maneuver on stable orbit', f'got {len(no_anom)} anomalies on unchanged orbit')
    else:
        _pass('no anomaly on stable orbit')

    # T3: no previous record -> no detection (first observation, no baseline)
    first = det_maneuver.detect(None, curr, corroborated=False)
    if first:
        ok = _fail('no maneuver without baseline', 'should not flag on first observation')
    else:
        _pass('no anomaly without baseline')

    print('\n-- Freshness gate ---------------------------------------------')

    # High staleness + T1 target + no corroboration -> BLOCKED
    blocked = not may_promote('high', 'T1', corroborated=False)
    if not blocked:
        ok = _fail('freshness gate blocks', 'high staleness T1 without corroboration should be blocked')
    else:
        _pass('high staleness T1 blocked without corroboration')

    # High staleness + T1 + corroborated -> ALLOWED
    allowed = may_promote('high', 'T1', corroborated=True)
    if not allowed:
        ok = _fail('freshness gate allows corroborated', 'corroborated should pass even on high staleness')
    else:
        _pass('high staleness T1 allowed when corroborated')

    # Low staleness -> always allowed
    always = may_promote('low', 'T1', corroborated=False)
    if not always:
        ok = _fail('freshness gate low staleness', 'low staleness should always promote')
    else:
        _pass('low staleness always promotes')

    # Stale TLE maneuver -> blocked without corroboration
    stale_prev = _make_orbital_record(99999, 14.0, 0.002, 560, 600, staleness='high')
    stale_curr = _make_orbital_record(99999, 14.05, 0.0015, 582, 603, staleness='high')
    stale_anom = det_maneuver.detect(stale_prev, stale_curr, corroborated=False)
    if stale_anom:
        target_tier = 'T2'  # maneuver is T2
        stale_curr['anomalies'] = stale_anom
        promoted = may_promote('high', target_tier, corroborated=False)
        if promoted:
            ok = _fail('stale maneuver gate', 'stale maneuver without corroboration should not promote to T2')
        else:
            _pass('stale maneuver blocked without corroboration (freshness gate holds)')
    else:
        _pass('stale orbit: detector correctly found no maneuver (within threshold)')

    print('\n-- Tier assignment --------------------------------------------')

    cases = [
        ([{'kind': 'conjunction_close_approach', 'state': 'active'}], False, 'T1'),
        ([{'kind': 'maneuver',            'state': 'active'}], False, 'T2'),
        ([],                                                    False, 'T3'),
        ([],                                                    True,  'T2'),  # watchlist escalates T3->T2
        ([{'kind': 'maneuver', 'state': 'active'}],            True,  'T1'),  # watchlist escalates T2->T1
        ([{'kind': 'maneuver', 'state': 'resolved'}],          False, 'T3'),  # resolved = no escalation
    ]
    for anomalies, wl, expected in cases:
        got = assign_tier(anomalies, watchlist_hit=wl)
        label = f'{[a["kind"] for a in anomalies]} wl={wl}'
        if got != expected:
            ok = _fail(f'tier {label}', f'expected {expected}, got {got}')
        else:
            _pass(f'tier {expected}: {label}')

    print('\n-- Conjunction detector ---------------------------------------')

    st_src = [{'name': 'space-track', 'url': 'https://www.space-track.org/', 'retrieved_at': _iso()}]

    # T1: active payload involved AND miss < 2km (conservative payload gate)
    cdm_active = {
        'SAT1_ID': '25544', 'SAT2_ID': '37820',
        'SAT1_OBJECT_TYPE': 'PAYLOAD', 'SAT2_OBJECT_TYPE': 'DEBRIS',
        'TCA': _iso(3), 'MISS_DISTANCE': '1500',  # 1500m = 1.5km -- payload + tight miss
        'COLLISION_PROBABILITY': '0.0001', 'RELATIVE_SPEED': '11.3',
        'ORBIT_REGIME': 'LEO',
    }
    rec_active = det_conjunction.from_cdm(cdm_active, st_src)
    if not rec_active or rec_active['tier'] != 'T1':
        ok = _fail('T1: active payload', f'payload + 1.5km miss should be T1, got {rec_active and rec_active["tier"]}')
    else:
        _pass('T1: active payload + miss < 2km -> T1')
        kind = rec_active['anomalies'][0]['kind']
        if kind != 'conjunction_close_approach':
            ok = _fail('conjunction kind: payload close approach', f'expected conjunction_close_approach, got {kind}')
        else:
            _pass('conjunction kind = conjunction_close_approach for payload-involved close approach')

    # T1: sub-km miss even for debris x debris
    cdm_subkm = {
        'SAT1_ID': '90211', 'SAT2_ID': '37820',
        'SAT1_OBJECT_TYPE': 'DEBRIS', 'SAT2_OBJECT_TYPE': 'DEBRIS',
        'TCA': _iso(3), 'MISS_DISTANCE': '420',  # 420m = 0.42 km
        'COLLISION_PROBABILITY': '0.0012', 'RELATIVE_SPEED': '11.3',
        'ORBIT_REGIME': 'LEO',
    }
    rec_subkm = det_conjunction.from_cdm(cdm_subkm, st_src)
    if not rec_subkm or rec_subkm['tier'] != 'T1':
        ok = _fail('T1: sub-km debris miss', f'sub-km miss should be T1, got {rec_subkm and rec_subkm["tier"]}')
    else:
        _pass('T1: sub-km miss (420m) -> T1 even for debris x debris')
        ev = rec_subkm['anomalies'][0]['evidence'][0]
        if abs(float(ev['value']) - 0.42) > 0.01:
            ok = _fail('miss distance conversion', f'expected 0.42 km, got {ev["value"]}')
        else:
            _pass('MISS_DISTANCE meters->km conversion correct (420m -> 0.42km)')

    # T2: debris x debris, elevated Pc, large miss
    cdm_debris = {
        'SAT1_ID': '90211', 'SAT2_ID': '37820',
        'SAT1_OBJECT_TYPE': 'DEBRIS', 'SAT2_OBJECT_TYPE': 'DEBRIS',
        'TCA': _iso(3), 'MISS_DISTANCE': '5000',  # 5km
        'COLLISION_PROBABILITY': '0.00002', 'RELATIVE_SPEED': '11.3',
        'ORBIT_REGIME': 'LEO',
    }
    rec_debris = det_conjunction.from_cdm(cdm_debris, st_src)
    if not rec_debris or rec_debris['tier'] != 'T2':
        ok = _fail('T2: debris x debris', f'debris x debris elevated Pc should be T2, got {rec_debris and rec_debris["tier"]}')
    else:
        _pass('T2: debris x debris + elevated Pc -> T2 (amber)')

    # 202km SL-3 R/B x PSLV case: rocket_body x rocket_body, large miss, Pc 9e-4
    # Should NOT be T1 (no active payload, miss >> 1km); T2 only if Pc elevated
    cdm_202km = {
        'SAT1_ID': '11111', 'SAT2_ID': '22222',
        'SAT1_OBJECT_TYPE': 'ROCKET BODY', 'SAT2_OBJECT_TYPE': 'ROCKET BODY',
        'TCA': _iso(3), 'MISS_DISTANCE': '202000',  # 202km in meters
        'COLLISION_PROBABILITY': '0.0009', 'RELATIVE_SPEED': '11.3',
        'ORBIT_REGIME': 'LEO',
    }
    rec_202 = det_conjunction.from_cdm(cdm_202km, st_src)
    if rec_202 and rec_202.get('tier') == 'T1':
        ok = _fail('no T1 for 202km miss', '202km miss rocket_body x rocket_body should not be T1')
    else:
        tier_202 = rec_202['tier'] if rec_202 else 'None (not emitted)'
        _pass(f'202km SL-3 R/B case -> {tier_202} (not T1, red stays honest)')

    # alert_class: payload-involved -> 'alert', debris x debris -> 'close_pass'
    if rec_active:
        ac = rec_active.get('location', {}).get('alert_class')
        if ac != 'alert':
            ok = _fail('alert_class: payload', f'expected alert, got {ac}')
        else:
            _pass('alert_class = alert for payload-involved conjunction')
    if rec_debris:
        ac = rec_debris.get('location', {}).get('alert_class')
        if ac != 'close_pass':
            ok = _fail('alert_class: debris', f'expected close_pass, got {ac}')
        else:
            _pass('alert_class = close_pass for debris x debris conjunction')

    # None: routine background
    cdm_background = {
        'SAT1_ID': '90211', 'SAT2_ID': '37820',
        'SAT1_OBJECT_TYPE': 'DEBRIS', 'SAT2_OBJECT_TYPE': 'DEBRIS',
        'TCA': _iso(3), 'MISS_DISTANCE': '500000',  # 500km
        'COLLISION_PROBABILITY': '0.000000001', 'RELATIVE_SPEED': '11.3',
        'ORBIT_REGIME': 'LEO',
    }
    no_conj = det_conjunction.from_cdm(cdm_background, st_src)
    if no_conj is not None:
        ok = _fail('background not emitted', '500km / negligible Pc debris should return None')
    else:
        _pass('background conjunction correctly not emitted')

    print('\n-- Space weather detector -------------------------------------')

    sw_src = [{'name': 'noaa-swpc', 'url': 'https://services.swpc.noaa.gov/', 'retrieved_at': _iso()}]
    x_rec = norm_sw.from_xray_peak({'time_tag': _iso(), 'flux': 1.5e-3, 'onset': _iso(-0.1)}, sw_src)
    x_anom = det_sw.detect_flare(x_rec)
    if not x_anom:
        ok = _fail('X-class flare detected', 'X1.5 should trigger space_weather_severe')
    else:
        tier = assign_tier(x_anom)
        if tier != 'T1':
            ok = _fail('X-class tier', f'expected T1, got {tier}')
        else:
            _pass('X-class flare -> space_weather_severe -> T1')

    m_rec = norm_sw.from_xray_peak({'time_tag': _iso(), 'flux': 2e-4, 'onset': _iso(-0.05)}, sw_src)
    m_anom = det_sw.detect_flare(m_rec)
    if m_anom:
        ok = _fail('M-class not severe', 'M-class should not trigger space_weather_severe')
    else:
        _pass('M-class flare: no severe anomaly (below X threshold)')

    print()
    return ok


if __name__ == '__main__':
    print('Stars Edition — detector smoke tests')
    print('=====================================')
    passed = run_all()
    if passed:
        print('ALL TESTS PASSED - catch logic armed. Flip the Space-Track switch.')
        sys.exit(0)
    else:
        print('SOME TESTS FAILED - fix before creds land.')
        sys.exit(1)
