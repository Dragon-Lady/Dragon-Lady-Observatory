"""
poll.py — the main engine loop.

Polls each source, normalizes, detects anomalies, tiers, checks watchlist,
applies the freshness gate, and writes records to data/records/.

Run:
    python -m engine.poll              # one-shot pass
    python -m engine.poll --loop 300  # continuous, 300s between passes
"""

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Bootstrap .env before any imports that read env vars
from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[1] / '.env')

from engine.sources import celestrak, noaa_swpc, launch_library, space_track
from engine.normalize import orbital as norm_orbital
from engine.normalize import space_weather as norm_sw
from engine.normalize import launch as norm_launch
from engine.detect import maneuver as det_maneuver
from engine.detect import conjunction as det_conjunction
from engine.detect import space_weather as det_sw
from engine.freshness import may_promote
from engine.tier import assign_tier
from engine.watchlist import is_watchlisted
from engine.store.writer import write_record, load_record


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def run_pass():
    print(f'[poll] pass started {_now_iso()}')
    written = 0

    # ── 1. Space weather (NOAA SWPC — no key, runs immediately) ──────────────
    print('[poll] fetching NOAA SWPC...')
    retrieved_sw = _now_iso()
    sw_source = [noaa_swpc.source_entry(retrieved_sw)]

    for peak in _extract_flare_peaks(noaa_swpc.fetch_xray()):
        rec = norm_sw.from_xray_peak(peak, sw_source)
        anomalies = det_sw.detect_flare(rec)
        if anomalies:
            rec['anomalies'] = anomalies
            rec['tier'] = assign_tier(anomalies, watchlist_hit=is_watchlisted(rec))
            write_record(rec)
            written += 1
            print(f'  [T{rec["tier"][-1]}] flare {rec["names"][0]}')

    for kp_val, ts in _extract_kp_readings(noaa_swpc.fetch_kp()):
        rec = norm_sw.from_kp(kp_val, ts, sw_source)
        anomalies = det_sw.detect_geomagnetic(rec)
        if anomalies or kp_val >= 5:
            rec['anomalies'] = anomalies
            rec['tier'] = assign_tier(anomalies, watchlist_hit=is_watchlisted(rec))
            write_record(rec)
            written += 1
            print(f'  [T{rec["tier"][-1]}] Kp={kp_val} {ts}')

    # ── 2. Launches (Launch Library 2 — no key) ────────────────────────────────
    print('[poll] fetching Launch Library 2...')
    retrieved_ll = _now_iso()
    ll_source = [launch_library.source_entry(retrieved_ll)]

    for launch in launch_library.fetch_upcoming_launches():
        rec = norm_launch.from_ll2_launch(launch, ll_source)
        wl  = is_watchlisted(rec)
        rec['watchlist'] = wl
        rec['tier'] = assign_tier([], watchlist_hit=wl)
        write_record(rec)
        written += 1

    # ── 3. Orbital — CelesTrak (no key, bootstrap) ────────────────────────────
    print('[poll] fetching CelesTrak catalog...')
    retrieved_ct = _now_iso()
    ct_source = [celestrak.source_entry(retrieved_ct)]
    ct_catalog = celestrak.fetch_gp_catalog()
    print(f'  CelesTrak: {len(ct_catalog)} objects')

    ct_by_norad: dict[int, dict] = {}

    for gp in ct_catalog:
        try:
            rec = norm_orbital.from_gp(gp, ct_source)
            ct_by_norad[rec['location']['norad_id']] = rec
        except Exception:
            continue

    # ── 4. Orbital — Space-Track (primary, needs .env creds) ─────────────────
    print('[poll] fetching Space-Track GP catalog...')
    retrieved_st = _now_iso()
    st_source = [space_track.source_entry(retrieved_st)]
    st_catalog = space_track.fetch_gp_catalog()
    print(f'  Space-Track: {len(st_catalog)} objects')

    for gp in st_catalog:
        try:
            sources = [space_track.source_entry(retrieved_st)]
            norad = int(gp.get('NORAD_CAT_ID', 0))
            if norad in ct_by_norad:
                sources.append(celestrak.source_entry(retrieved_ct))

            rec = norm_orbital.from_gp(gp, sources)
            wl  = is_watchlisted(rec)
            rec['watchlist'] = wl

            prev = load_record(rec['id'])
            corroborated = norad in ct_by_norad

            anomalies = det_maneuver.detect(prev, rec, corroborated=corroborated)
            stale = rec['freshness']['staleness_risk']

            filtered = [a for a in anomalies
                        if may_promote(stale, _anomaly_tier(a['kind']), corroborated)]

            rec['anomalies'] = filtered
            rec['tier'] = assign_tier(filtered, watchlist_hit=wl)

            write_record(rec)
            written += 1

            if filtered:
                print(f'  [T{rec["tier"][-1]}] maneuver {rec["names"][0]}')

        except Exception:
            continue

    # ── 5. Conjunctions (Space-Track CDM) ─────────────────────────────────────
    print('[poll] fetching Space-Track CDMs...')
    cdm_source = [space_track.source_entry(_now_iso())]
    for cdm in space_track.fetch_cdm():
        try:
            rec = det_conjunction.from_cdm(cdm, cdm_source)
            if rec:
                wl = is_watchlisted(rec)
                rec['watchlist'] = wl
                rec['tier'] = assign_tier(rec['anomalies'], watchlist_hit=wl)
                write_record(rec)
                written += 1
                print(f'  [T{rec["tier"][-1]}] conjunction {rec["names"][0]}')
        except Exception:
            continue

    print(f'[poll] pass done — {written} records written {_now_iso()}')
    return written


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_flare_peaks(xray_data: list) -> list[dict]:
    """Find flux peaks from the GOES X-ray time series (M-class and above)."""
    M_THRESHOLD = 1e-4
    peaks = []
    prev_flux = 0.0
    in_peak = False
    peak = {}

    for row in xray_data:
        try:
            flux = float(row.get('flux', 0) or 0)
        except (TypeError, ValueError):
            continue
        ts = row.get('time_tag', '')

        if flux >= M_THRESHOLD:
            if not in_peak:
                in_peak = True
                peak = {'time_tag': ts, 'flux': flux, 'onset': ts}
            elif flux > peak.get('flux', 0):
                peak.update({'time_tag': ts, 'flux': flux})
        elif in_peak:
            if peak:
                peaks.append(peak)
            in_peak = False
            peak = {}
        prev_flux = flux

    if in_peak and peak:
        peaks.append(peak)

    return peaks


def _extract_kp_readings(kp_data: list) -> list[tuple[float, str]]:
    """Extract (kp_value, time_tag) tuples for storm-level readings."""
    readings = []
    STORM_THRESHOLD = 5.0
    for row in kp_data:
        try:
            if isinstance(row, list) and len(row) >= 2:
                ts, kp = row[0], row[1]
            elif isinstance(row, dict):
                ts  = row.get('time_tag', '')
                kp  = row.get('kp_index', row.get('Kp', 0))
            else:
                continue
            kp_val = float(kp)
            if kp_val >= STORM_THRESHOLD:
                readings.append((kp_val, str(ts)))
        except (TypeError, ValueError):
            continue
    return readings


def _anomaly_tier(kind: str) -> str:
    from engine.tier import T1_KINDS, T2_KINDS
    if kind in T1_KINDS:
        return 'T1'
    if kind in T2_KINDS:
        return 'T2'
    return 'T3'


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stars Edition engine poll loop.')
    parser.add_argument('--loop', type=int, default=0,
                        help='Seconds between passes (0 = one-shot).')
    args = parser.parse_args()

    if args.loop:
        print(f'[poll] continuous mode, interval={args.loop}s')
        while True:
            try:
                run_pass()
            except KeyboardInterrupt:
                print('[poll] stopped')
                sys.exit(0)
            except Exception as e:
                print(f'[poll] pass error: {e}')
            time.sleep(args.loop)
    else:
        run_pass()
