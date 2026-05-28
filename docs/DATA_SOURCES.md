# Stars Edition — Data Sources

Non-NASA, free, primary + fallback per domain — the same discipline as Dragon
Eye's ADSBX-primary / OpenSky-fallback. Confirmed by Rocky's source evaluation
(2026-05-28).

| Domain | Primary | Fallback / bootstrap | Auth |
|---|---|---|---|
| **Orbital** (catalog, elsets, conjunctions, decay) | **Space-Track.org** (USSF 18 SDS — authoritative; the source others mirror) | **CelesTrak** (clean TLE mirror) | Space-Track: free registration · CelesTrak: none |
| **Launches / reentries** | **Launch Library 2** (The Space Devs) | — | none; optional free key raises limits |
| **Space weather** | **NOAA SWPC** | — | none |
| **Near-Earth objects** | **ESA NEOCC** *(pending Rocky's API confirm)* | Minor Planet Center | none / TBD |

## Notes

- **Space-Track is load-bearing** — catalog + conjunction CDM + decay covers three
  anomaly categories from one source. Respect its usage rules: cache the catalog
  locally and poll deltas; don't hammer.
- **CelesTrak** is the no-key bootstrap so the engine runs before a Space-Track
  account is provisioned — and CelesTrak-vs-Space-Track agreement doubles as the
  corroboration check for the freshness gate.
- **Client-side render:** TLEs → positions via satellite.js in the viewer; the
  engine does ingest + anomaly, the viewer does propagation. No render server.
- **NEO gap:** JPL CNEOS is the obvious feed but it's NASA — excluded by the
  non-NASA rule. ESA NEOCC is the proposed non-NASA replacement, pending API-shape
  confirmation.

## Register first

1. **Space-Track.org** (the public orbital spine)
2. **Launch Library 2** (optional free key)

## Secrets

No credential is ever committed. Space-Track login + any API keys live in `.env`
(gitignored). If a key would ship in a client bundle, treat it as extractable and
scope it accordingly.
