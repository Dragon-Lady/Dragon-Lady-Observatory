# Dragon Lady Observatory

A beautiful way to explore space from home. Dragon Lady Observatory brings the Dragon Eye
grammar — a living globe, layered views, tiered cards, clear provenance — to the
space domain: the satellites overhead, near-Earth objects passing by, space
weather, and launches, all on one calm surface, with **anomaly detection** that
surfaces what doesn't behave the way it should.

Observation and advisory only. It watches and explains; it does not act.

## What it shows

- **Orbital** — satellites, rocket bodies, and debris; maneuvers, close
  approaches (conjunctions), decays/reentries, and objects that don't fit.
- **Near-Earth objects** — asteroids and comets, close approaches, and
  newly-flagged trajectories.
- **Space weather** — solar flares, CMEs, geomagnetic storms.
- **Launches & reentries** — what's going up and what's coming down.

All four domains live in one unified record model with a `domain` discriminator,
so search, tiering, the watchlist, and the globe work the same across them.

## Architecture (at a glance)

- A **running engine** (Python) polls the data sources, normalizes records,
  runs anomaly detection, assigns tiers, and applies the watchlist.
- A **globe/sky viewer** renders objects client-side (TLE → position) with
  layer toggles and tier-sorted cards.
- A **freshness gate** is the primary false-positive defense: an anomaly is not
  promoted while its subject's data is stale unless a second source corroborates.

Full design: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
record model: [`schema/record.md`](schema/record.md) ·
data sources: [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Relationship to Dragon Eye

Dragon Lady Observatory (the viewer) is built on the Dragon Eye engine's *grammar* — T1/T2/T3 tiers, watchlist behavior, card patterns,
anomaly language — via shared conventions, but keeps a hard boundary: no shared
database, no filesystem coupling. This protects Dragon Eye's operational posture
and keeps the Observatory viewer simple to reason about on its own. (Formerly referred to internally as Stars Edition.)

## Layout

```
schema/      the unified record model (the producer/consumer contract)
docs/        architecture + data sources
engine/      Python: pollers, normalizers, anomaly detectors, tiering
viewer/      globe/sky UI + tier-sorted cards
config/      watchlist + runtime config (examples only; no secrets committed)
```

## Status

Design locked (schema consensus + data spine). Scaffolding stage. Not yet pushed
publicly; security clearance gates any public push. License TBD.
