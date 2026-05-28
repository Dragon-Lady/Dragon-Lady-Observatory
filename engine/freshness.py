"""
freshness.py — staleness_risk computation + the anomaly promotion gate.

This is the primary false-positive defense: a stale TLE looks exactly like a
maneuver, so anomalies on high-staleness subjects are NOT promoted to T1/T2
unless a corroborating source agrees.
"""

from datetime import datetime, timezone

# Hours after retrieval before staleness escalates, by domain.
_CADENCE = {
    'orbital':        (24, 72),    # medium after 24h, high after 72h
    'space_weather':  (1,  4),
    'neo':            (168, 720),  # 7d / 30d
    'launch_reentry': (1,  6),
}


def _age_hours(ts_iso: str) -> float:
    if not ts_iso:
        return float('inf')
    try:
        ts = datetime.fromisoformat(ts_iso.replace('Z', '+00:00'))
        return (datetime.now(timezone.utc) - ts).total_seconds() / 3600
    except Exception:
        return float('inf')


def staleness_risk(domain: str, retrieved_at_iso: str, elset_epoch_iso: str = None) -> str:
    """Return 'low' | 'medium' | 'high' for a record's freshness."""
    med_h, high_h = _CADENCE.get(domain, (24, 72))

    age = _age_hours(retrieved_at_iso)
    if domain == 'orbital' and elset_epoch_iso:
        age = max(age, _age_hours(elset_epoch_iso))

    if age >= high_h:
        return 'high'
    if age >= med_h:
        return 'medium'
    return 'low'


def may_promote(staleness: str, target_tier: str, corroborated: bool) -> bool:
    """
    Freshness gate: block T1/T2 promotion on a high-staleness subject unless
    a second source corroborates. CelesTrak-vs-Space-Track agreement is the
    natural corroboration check for orbital records.
    """
    if staleness == 'high' and target_tier in ('T1', 'T2') and not corroborated:
        return False
    return True
