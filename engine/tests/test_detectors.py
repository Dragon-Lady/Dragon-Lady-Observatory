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
        ([{'kind': 'conjunction_high_pc', 'state': 'active'}], False, 'T1'),
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

    # MISS_DISTANCE in CDM is METERS. 420 m = 0.42 km, Pc 0.0012 -> T1 (AND-gate: both met)
    cdm_hit = {
        'SAT1_ID': '90211', 'SAT2_ID': '37820',
        'TCA': _iso(3), 'MISS_DISTANCE': '420',
        'COLLISION_PROBABILITY': '0.0012', 'RELATIVE_SPEED': '11.3',
        'ORBIT_REGIME': 'LEO',
    }
    st_src = [{'name': 'space-track', 'url': 'https://www.space-track.org/', 'retrieved_at': _iso()}]
    conj_rec = det_conjunction.from_cdm(cdm_hit, st_src)
    if not conj_rec:
        ok = _fail('conjunction detected', '420m miss / Pc 0.0012 should produce T1 record')
    else:
        if conj_rec['tier'] != 'T1':
            ok = _fail('conjunction tier', f'expected T1, got {conj_rec["tier"]}')
        else:
            _pass('conjunction tier = T1 (420m miss, Pc 0.0012, AND-gate met)')
        ev = conj_rec['anomalies'][0]['evidence'][0]
        if abs(float(ev['value']) - 0.42) > 0.01:
            ok = _fail('conjunction evidence value', f'expected 0.42 km, got {ev["value"]}')
        else:
            _pass('conjunction miss_distance in evidence = 0.42 km (converted from 420 m)')

    # James AND-gate: 202 km miss (202000 m) with high Pc -> NOT T1 (miss too large)
    cdm_202km = dict(cdm_hit, MISS_DISTANCE='202000', COLLISION_PROBABILITY='0.0009')
    no_t1 = det_conjunction.from_cdm(cdm_202km, st_src)
    if no_t1 and no_t1.get('tier') == 'T1':
        ok = _fail('AND-gate: 202km miss not T1', '202km miss should fail the <10km AND-gate')
    else:
        _pass('AND-gate holds: 202km miss does not glow red regardless of Pc')

    # Wide miss + negligible Pc -> None (background, not emitted)
    cdm_miss = dict(cdm_hit, MISS_DISTANCE='500000', COLLISION_PROBABILITY='0.000000001')
    no_conj = det_conjunction.from_cdm(cdm_miss, st_src)
    if no_conj is not None:
        ok = _fail('conjunction threshold', '500km miss / negligible Pc should return None')
    else:
        _pass('wide-miss / negligible-Pc CDM correctly returns None')

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
