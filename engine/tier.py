"""
tier.py — Dragon Eye T1/T2/T3 assignment + watchlist escalation.

Mirrors DE's display grammar: T1 always red, T2 subcategory colors, T3 background.
Watchlist hits auto-escalate one tier.
"""

T1_KINDS = frozenset({
    'conjunction_high_pc',
    'decay_imminent',
    'space_weather_severe',
    'new_object',
    'rpo',
})

T2_KINDS = frozenset({
    'maneuver',
    'neo_close_approach',
    'catalog_change',
    'unexpected_brightening',
})


def escalate_tier(tier: str) -> str:
    """Escalate one tier step for watchlist hits."""
    if tier == 'T3':
        return 'T2'
    if tier == 'T2':
        return 'T1'
    return 'T1'


def assign_tier(anomalies: list, watchlist_hit: bool = False) -> str:
    """
    T1: any active T1-class anomaly.
    T2: any active T2-class anomaly, no T1.
    T3: background.
    Watchlist hit escalates one tier.
    """
    tier = 'T3'

    for a in anomalies:
        if a.get('state') in ('resolved', 'dismissed'):
            continue
        kind = a.get('kind', '')
        if kind in T1_KINDS:
            tier = 'T1'
            break
        if kind in T2_KINDS and tier == 'T3':
            tier = 'T2'

    if watchlist_hit:
        tier = escalate_tier(tier)

    return tier
