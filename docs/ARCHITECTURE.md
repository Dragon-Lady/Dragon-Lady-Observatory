# Stars Edition — Architecture

Distilled from the Oracle ⇄ James consensus (2026-05-28). This is the build plan;
the wiring fills it in.

## Posture

Observation / advisory only. Anomaly detection is the primary job: surface what
doesn't belong or behaves strangely, and explain why. No active recon, no
operator actions, no claims the data can't support.

## Shape: a running engine + a viewer

Stars Edition is **not** a static site (unlike Open UAP, whose corpus is static
after ingest). Space data is live, and anomaly detection is inherently a running
process — continuous ingest + comparison against prior state. So:

```
   data sources ──▶ POLLERS ──▶ NORMALIZE ──▶ ANOMALY DETECT ──▶ TIER + WATCHLIST ──▶ record store
                    (engine, Python)                                                      │
                                                                                          ▼
                                                                              VIEWER (globe/sky + cards)
                                                                              client-side TLE propagation
```

- **Engine (Python):** polite pollers per source (cache + poll deltas, respect
  terms), normalize into the unified record, run detectors, assign tier, apply
  watchlist, write the record store the viewer reads.
- **Viewer:** a globe/sky surface with layer toggles (orbital / NEO / space
  weather / launches) and a tier-then-freshness sorted card list; detail pane
  with provenance + anomaly evidence + "view original source." TLEs propagate to
  positions client-side (satellite.js), so the viewing layer needs no server of
  its own.

## The unified record

One record, `domain` discriminator (`orbital | neo | space_weather |
launch_reentry`), with a domain-specific `location` payload and an `anomalies[]`
list. Full shape in [`../schema/record.md`](../schema/record.md). Key points:

- **Anomaly = a delta WITH evidence**, not a bare flag. Detection lives in the
  engine; the record carries the *result* + evidence so the UI explains itself.
- **`sources[]` + `freshness`** on every record. Provenance is load-bearing.

## Tiering (Dragon Eye grammar)

- **T1 (always red):** high-Pc conjunction; imminent reentry over a populated
  area; severe space weather (X-class / Kp8+); confirmed uncatalogued object on a
  notable orbit; clear RPO against a watched asset.
- **T2 (subcategory colors):** detected maneuver; moderate conjunction; PHA close
  approach within N lunar distances; M-class flare.
- **T3:** routine catalog changes, nominal launches, background.

Space-native categories ride as `anomalies[].kind` + `topics`, not a replacement
ladder. Watchlist hits auto-escalate one tier.

## Watchlist (Dragon Eye lineage)

Pin objects/orbits of interest; pinned subjects get elevated polling and
auto-escalate tier on a hit; a dedicated "Watched" view; state persists between
sessions. **Anchor on static identity** (NORAD id / international designator / NEO
designation), never ephemeral state — Dragon Eye's "lock by registration, not
hex" rule.

## The freshness gate (primary false-positive defense)

A stale TLE looks exactly like a maneuver. So: **an anomaly is not promoted to
T1/T2 if its subject's `freshness.staleness_risk == high` unless a corroborating
source agrees.** `staleness_risk` is computed from source fetch timestamps + the
elset epoch age + domain cadence. CelesTrak-vs-Space-Track agreement is a natural
corroboration check.

## Data sources

Locked SSA spine in [`DATA_SOURCES.md`](DATA_SOURCES.md): Space-Track (+ CelesTrak
fallback) for orbital, Launch Library 2 for launches, NOAA SWPC for space weather,
ESA NEOCC (pending confirm) for NEO. Non-NASA, free, primary+fallback — same
discipline as Dragon Eye's ADSBX/OpenSky.

## Lanes

- **engine/** — pollers, normalizers, detectors, tiering: Rocky + Ice Man.
- **viewer/** — globe/sky UI + cards: Oracle.
- **schema/** — the contract: Oracle + James (locked).
- **security/clearance** — Goldwing, before any public push.

## Phase 2+ (logged, not v1)

Multi-source fusion, predictive maneuver ML, alerting, historical orbit replay,
cross-domain correlation (e.g. space-weather × event timing), and any cross-link
to the Dragon Eye air picture. The unified record + `related_ids` already leave
room for these without schema breakage.
