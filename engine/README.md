# engine/ — ingest + anomaly detection (Rocky + Ice Man lane)

Python. The running process that turns live data into tiered, evidence-bearing
records the viewer reads.

Suggested structure (fill in as wired):

```
engine/
  sources/        one polite poller per source (space_track, celestrak, launch_library, noaa_swpc, esa_neocc)
  normalize/      raw source payloads -> the unified record (schema/record.md)
  detect/         anomaly detectors per category (maneuver, conjunction, decay, neo_close_approach, space_weather_severe, ...)
  tier.py         tier assignment (DE T1/T2/T3 grammar) + watchlist escalation
  freshness.py    staleness_risk computation + the promotion gate
  store/          record store the viewer reads
  poll.py         the loop: poll deltas -> normalize -> detect -> tier -> store
```

Contract to honor: emit records exactly per [`../schema/record.md`](../schema/record.md).
Sources + posture: [`../docs/DATA_SOURCES.md`](../docs/DATA_SOURCES.md). The
freshness gate (don't promote on stale data without corroboration) is the
load-bearing false-positive defense — implement it in `freshness.py` and have
`detect/` honor it.

Politeness: cache catalogs, poll deltas, respect Space-Track terms. Secrets in
`.env` only (gitignored).
