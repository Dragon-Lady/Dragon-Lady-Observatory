"""
catalog.py — emit data/catalog/tle.json for the globe viewer.

One lightweight file, all CelesTrak objects, TLE lines preserved so
satellite.js can propagate positions client-side. This is the starfield
backdrop; records/ is the signal layer on top.
"""

import json
from pathlib import Path

CATALOG_DIR = Path(__file__).parents[2] / 'data' / 'catalog'

# Objects that always get a full record written (beyond anomalies + watchlist).
# NORAD IDs pinned to static identity per the watchlist discipline.
NOTABLE_NORAD = {
    25544,   # ISS
    20580,   # Hubble
    48274,   # Tiangong (CSS)
    43657,   # Starlink-1 (representative)
    27607,   # Envisat (large debris — high-profile reentry candidate)
}


def write_tle_bundle(tle_records: list[dict]) -> Path:
    """
    Write data/catalog/tle.json from parsed TLE text records.
    Input: list of {'norad_id', 'name', 'tle1', 'tle2'} from celestrak.fetch_tle_records().
    Output: compact JSON file satellite.js reads for client-side propagation.
    Returns the path written.
    """
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)

    bundle = []
    for rec in tle_records:
        tle1 = rec.get('tle1', '')
        tle2 = rec.get('tle2', '')
        if not tle1 or not tle2:
            continue
        bundle.append({
            'norad_id': rec.get('norad_id', 0),
            'name':     rec.get('name', ''),
            'tle1':     tle1,
            'tle2':     tle2,
        })

    out = CATALOG_DIR / 'tle.json'
    out.write_text(json.dumps(bundle, separators=(',', ':')), encoding='utf-8')
    return out


def is_notable(norad_id: int) -> bool:
    return norad_id in NOTABLE_NORAD
