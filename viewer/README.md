# viewer/ — globe/sky surface + cards (Oracle lane)

The calm public face: a living globe/sky with layer toggles and tier-sorted
cards. Reads the engine's record store; renders observation-only.

Planned shape:

```
viewer/
  globe/          3D globe + orbit propagation (satellite.js: TLE -> position)
  layers/         toggles: orbital / neo / space_weather / launch_reentry
  cards/          tier-then-freshness sorted list + detail pane
  detail/         provenance block + anomaly evidence + "view original source"
  watchlist/      pin/unpin + "Watched" view (persisted client-side)
  search/         by name / topic
```

Design grammar: Dragon Eye tiers/cards/status + the Osiris-style globe/layers/
cards reference. Dark-default, low-fatigue. Renders records per
[`../schema/record.md`](../schema/record.md); degrades gracefully on absent
optional fields (no empty sections). Auto-generated content always labeled.

The viewing layer needs no server of its own — TLE propagation is client-side; the
engine supplies the records.
