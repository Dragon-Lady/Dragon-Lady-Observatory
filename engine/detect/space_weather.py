"""
detect/space_weather.py — anomaly detectors for space weather domain.

Detects: space_weather_severe (X-class flares, Kp >= 8).
"""

from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# X-ray flux thresholds (W/m^2)
_X_CLASS_THRESHOLD = 1e-3   # X1.0+
_M_CLASS_THRESHOLD = 1e-4   # M1.0+ (T2)

# Kp thresholds
_KP_SEVERE = 8    # G4-G5 storm -> T1
_KP_STORM  = 5    # G1+ storm   -> T2


def detect_flare(record: dict) -> list[dict]:
    """
    Detect severe space weather from a flare record.
    Returns a list of anomaly dicts (0 or 1) to merge into record['anomalies'].
    """
    loc     = record.get('location', {})
    flux    = _intensity_to_flux(loc.get('intensity', ''))
    if flux is None:
        return []

    now = _now_iso()

    if flux >= _X_CLASS_THRESHOLD:
        return [{
            'kind':       'space_weather_severe',
            'confidence': 0.99,
            'evidence':   [{
                'reason':      'X-class flare; potential radio blackout and radiation event',
                'metric':      'flux',
                'value':       flux,
                'source_ref':  record['sources'][0]['name'] if record.get('sources') else 'noaa-swpc',
                'observed_at': loc.get('peak', now),
            }],
            'delta':        {'flux_change': loc.get('intensity', '')},
            'state':        'active',
            'first_flagged': now,
            'last_updated':  now,
        }]

    return []


def detect_geomagnetic(record: dict) -> list[dict]:
    """Detect severe geomagnetic storm from a Kp record."""
    loc   = record.get('location', {})
    kp_str = loc.get('intensity', '').replace('Kp', '')
    try:
        kp = float(kp_str)
    except (ValueError, TypeError):
        return []

    now = _now_iso()
    if kp >= _KP_SEVERE:
        return [{
            'kind':       'space_weather_severe',
            'confidence': 0.95,
            'evidence':   [{
                'reason':      f'Severe geomagnetic storm Kp={kp} (G{int(kp)-3})',
                'metric':      'flux',
                'value':       kp,
                'source_ref':  record['sources'][0]['name'] if record.get('sources') else 'noaa-swpc',
                'observed_at': loc.get('onset', now),
            }],
            'delta':        {'kp': kp},
            'state':        'active',
            'first_flagged': now,
            'last_updated':  now,
        }]

    return []


def _intensity_to_flux(intensity: str) -> float | None:
    """Parse flare class string (e.g. 'X1.2') to W/m^2."""
    if not intensity:
        return None
    c = intensity[0].upper()
    try:
        val = float(intensity[1:])
    except (ValueError, IndexError):
        return None
    scales = {'X': 1e-3, 'M': 1e-4, 'C': 1e-5, 'B': 1e-6, 'A': 1e-7}
    base = scales.get(c)
    if base is None:
        return None
    return val * base
